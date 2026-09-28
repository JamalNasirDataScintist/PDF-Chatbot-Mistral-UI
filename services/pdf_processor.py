"""
PDF Processing Service
Handles text extraction from PDF documents using PyPDF2.
"""

import logging
from typing import Optional, Tuple
import PyPDF2

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction and preprocessing"""

    def extract_text(self, pdf_path: str) -> Tuple[Optional[str], int]:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            text = ""
            page_count = 0

            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)
                logger.info(f"Processing {page_count} page(s)...")

                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n[Page {i + 1}]\n{page_text}\n"

            cleaned = self._clean_text(text)
            logger.info(f"Extracted {len(cleaned)} characters from {page_count} pages")
            return cleaned, page_count

        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return None, 0

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove null bytes and excessive whitespace
        text = text.replace('\x00', '')
        # Normalize multiple spaces but preserve newlines
        lines = [' '.join(line.split()) for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line.strip())
        return text.strip()
