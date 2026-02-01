"""
Resume Parser Service

Extracts text content from PDF resume files using pdfplumber.
"""

import io
from typing import Optional

import pdfplumber

from app.logging_config import get_logger

logger = get_logger(__name__)

# Maximum file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes


class ResumeParseError(Exception):
    """Exception raised when resume parsing fails."""
    pass


def validate_file_size(file_content: bytes) -> None:
    """
    Validate that the file size is within limits.
    
    Args:
        file_content: The raw bytes of the uploaded file.
        
    Raises:
        ResumeParseError: If file exceeds maximum size.
    """
    file_size = len(file_content)
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise ResumeParseError(
            f"File size ({size_mb:.2f}MB) exceeds maximum allowed size (5MB)"
        )


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file_content: The raw bytes of the PDF file.
        
    Returns:
        Extracted text from all pages of the PDF.
        
    Raises:
        ResumeParseError: If the PDF cannot be parsed.
    """
    try:
        # Validate file size first
        validate_file_size(file_content)
        
        # Create a file-like object from bytes
        pdf_stream = io.BytesIO(file_content)
        
        extracted_text = []
        
        with pdfplumber.open(pdf_stream) as pdf:
            if len(pdf.pages) == 0:
                raise ResumeParseError("PDF file contains no pages")
            
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue
        
        if not extracted_text:
            raise ResumeParseError(
                "Could not extract any text from the PDF. "
                "The file may be scanned/image-based or corrupted."
            )
        
        # Join all pages with newlines
        full_text = "\n\n".join(extracted_text)
        
        logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
        return full_text
        
    except ResumeParseError:
        raise
    except Exception as e:
        logger.error(f"Failed to parse PDF: {e}")
        raise ResumeParseError(f"Failed to parse PDF: {str(e)}")


def get_text_preview(text: str, max_length: int = 500) -> str:
    """
    Get a preview of the extracted text.
    
    Args:
        text: The full extracted text.
        max_length: Maximum length of the preview.
        
    Returns:
        Truncated text with ellipsis if needed.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."
