"""
Configuration Settings for PDF Chatbot - Mistral AI Edition
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'applab-mistral-chatbot-2026')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB

    # Mistral AI
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')
    MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-small-latest')
    MISTRAL_MAX_TOKENS = int(os.getenv('MISTRAL_MAX_TOKENS', 1024))
    MISTRAL_TEMPERATURE = float(os.getenv('MISTRAL_TEMPERATURE', 0.3))

    # Embeddings (sentence-transformers — local, no API needed)
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

    # RAG Settings
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 500))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 50))
    TOP_K_CHUNKS = int(os.getenv('TOP_K_CHUNKS', 4))
