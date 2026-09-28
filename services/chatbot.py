"""
Chatbot Service - Mistral AI + RAG Architecture
Combines semantic search (sentence-transformers) with
Mistral AI for intelligent, context-aware responses.
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import torch
import requests
from sentence_transformers import SentenceTransformer
from config import Config

logger = logging.getLogger(__name__)


class Chatbot:
    """
    AI Chatbot using RAG (Retrieval Augmented Generation):
    1. Embeds document chunks using sentence-transformers
    2. Finds most relevant chunks via cosine similarity
    3. Sends context + question to Mistral AI for answer generation
    """

    SYSTEM_PROMPT = """You are an intelligent document assistant. You answer questions 
based ONLY on the provided document context. 

Rules:
- Answer clearly and concisely based on the context provided
- If the answer is not in the context, say "I couldn't find that information in the uploaded document"
- Use bullet points or numbered lists when listing multiple items
- Be professional, accurate, and helpful
- Reference specific details from the document when possible"""

    def __init__(self):
        logger.info("Initializing Chatbot with Mistral AI + RAG...")

        # Load local embedding model
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        logger.info(f"Embedding model loaded: {Config.EMBEDDING_MODEL}")

        # Document storage
        self.chunks: List[str] = []
        self.embeddings: List[torch.Tensor] = []
        self.metadata: List[Dict] = []

        # Mistral API settings
        self.api_key = Config.MISTRAL_API_KEY
        self.model = Config.MISTRAL_MODEL
        self.max_tokens = Config.MISTRAL_MAX_TOKENS
        self.temperature = Config.MISTRAL_TEMPERATURE
        self.top_k = Config.TOP_K_CHUNKS

        logger.info(f"Mistral model: {self.model}")
        logger.info("Chatbot ready!")

    def add_document(self, text: str, filename: str) -> str:
        """
        Process and add a document to the knowledge base.

        Args:
            text: Extracted document text
            filename: Original filename

        Returns:
            Document ID
        """
        logger.info(f"Indexing document: {filename}")
        chunks = self._chunk_text(text)
        doc_id = f"doc_{len(self.metadata)}"

        # Generate embeddings for all chunks at once (faster)
        embeddings = self.embedding_model.encode(chunks, convert_to_tensor=True)

        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            self.chunks.append(chunk)
            self.embeddings.append(emb)
            self.metadata.append({
                'doc_id': doc_id,
                'filename': filename,
                'chunk_index': i,
                'total_chunks': len(chunks)
            })

        logger.info(f"Indexed {len(chunks)} chunks from '{filename}'")
        return doc_id

    def get_answer(self, question: str) -> Dict:
        """
        Generate an AI answer using RAG pipeline.

        Args:
            question: User's question

        Returns:
            Dict with answer, sources, confidence
        """
        # Step 1: Retrieve relevant chunks
        relevant = self._retrieve(question)

        if not relevant:
            return {
                'answer': "I couldn't find relevant information in the uploaded documents.",
                'sources': [],
                'confidence': 'low'
            }

        # Step 2: Build context from retrieved chunks
        context = self._build_context(relevant)

        # Step 3: Query Mistral AI
        answer = self._query_mistral(question, context)

        # Step 4: Build source references
        sources = [
            {
                'filename': c['metadata']['filename'],
                'chunk': c['metadata']['chunk_index'] + 1,
                'snippet': c['text'][:120] + '...' if len(c['text']) > 120 else c['text'],
                'relevance': round(c['score'] * 100, 1)
            }
            for c in relevant
        ]

        return {
            'answer': answer,
            'sources': sources,
            'confidence': self._confidence(relevant)
        }

    def _retrieve(self, question: str) -> List[Dict]:
        """Find most relevant document chunks via cosine similarity"""
        q_emb = self.embedding_model.encode(question, convert_to_tensor=True)

        scores = []
        for i, emb in enumerate(self.embeddings):
            score = torch.cosine_similarity(
                q_emb.unsqueeze(0), emb.unsqueeze(0)
            ).item()
            scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        top = scores[:self.top_k]

        return [
            {
                'text': self.chunks[idx],
                'metadata': self.metadata[idx],
                'score': score
            }
            for idx, score in top if score > 0.2  # filter low-relevance chunks
        ]

    def _build_context(self, chunks: List[Dict]) -> str:
        """Build a clean context string from retrieved chunks"""
        parts = []
        for i, c in enumerate(chunks, 1):
            parts.append(
                f"[Source {i} - {c['metadata']['filename']}]\n{c['text']}"
            )
        return "\n\n---\n\n".join(parts)

    def _query_mistral(self, question: str, context: str) -> str:
        """
        Send question + context to Mistral AI API and get answer.

        Args:
            question: User's question
            context: Retrieved document context

        Returns:
            AI-generated answer string
        """
        if not self.api_key:
            return "⚠️ Mistral API key not configured. Please add MISTRAL_API_KEY to your .env file."

        user_message = f"""Based on the following document context, please answer the question.

DOCUMENT CONTEXT:
{context}

QUESTION: {question}

Please provide a clear, accurate answer based only on the context above."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()

        except requests.exceptions.Timeout:
            logger.error("Mistral API timeout")
            return "⚠️ Request timed out. Please try again."
        except requests.exceptions.HTTPError as e:
            logger.error(f"Mistral API HTTP error: {e}")
            if response.status_code == 401:
                return "⚠️ Invalid Mistral API key. Please check your .env file."
            elif response.status_code == 429:
                return "⚠️ Rate limit reached. Please wait a moment and try again."
            return f"⚠️ API error: {str(e)}"
        except Exception as e:
            logger.error(f"Mistral API error: {str(e)}")
            return f"⚠️ Error generating answer: {str(e)}"

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks for better context coverage"""
        words = text.split()
        chunks = []
        step = Config.CHUNK_SIZE - Config.CHUNK_OVERLAP

        for i in range(0, len(words), step):
            chunk = ' '.join(words[i:i + Config.CHUNK_SIZE])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def _confidence(self, chunks: List[Dict]) -> str:
        """Calculate confidence level from similarity scores"""
        if not chunks:
            return 'low'
        avg = np.mean([c['score'] for c in chunks])
        if avg > 0.65:
            return 'high'
        elif avg > 0.45:
            return 'medium'
        return 'low'

    def has_documents(self) -> bool:
        """Check if any documents are loaded"""
        return len(self.chunks) > 0

    def get_document_list(self) -> List[Dict]:
        """Get list of unique uploaded documents"""
        seen = {}
        for meta in self.metadata:
            doc_id = meta['doc_id']
            if doc_id not in seen:
                seen[doc_id] = {
                    'id': doc_id,
                    'filename': meta['filename'],
                    'chunks': meta['total_chunks']
                }
        return list(seen.values())

    def clear_documents(self):
        """Clear all documents from knowledge base"""
        self.chunks.clear()
        self.embeddings.clear()
        self.metadata.clear()
        logger.info("Knowledge base cleared")
