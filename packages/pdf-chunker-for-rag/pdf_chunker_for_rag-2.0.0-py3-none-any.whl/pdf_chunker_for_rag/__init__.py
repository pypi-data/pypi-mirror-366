 #!/usr/bin/env python3

"""
PDF Chunker Package
==================

A sophisticated PDF chunking system that creates structured, meaningful chunks
from PDF documents using font-based header detection and intelligent content filtering.

Main Features:
- Strategic header-based chunking (one chunk per header)
- Automatic font size analysis for optimal header detection
- Smart undersized chunk processing (remove meaningless, merge meaningful)
- Oversized chunk splitting with hierarchical sub-header detection
- Enhanced meaning detection with metadata filtering
- Comprehensive summarization and reporting

Usage:
    from pdf_chunker import CleanHybridPDFChunker
    
    chunker = CleanHybridPDFChunker()
    chunks = chunker.strategic_header_chunking("document.pdf")

Author: Generated AI Assistant
Version: 2.0 (Production)
Date: August 2, 2025
"""

from .chunk_creator import CleanHybridPDFChunker

__version__ = "2.0.0"
__author__ = "AI Assistant"
__email__ = "assistant@example.com"

__all__ = [
    "CleanHybridPDFChunker"
]

# For backward compatibility and ease of use
PDFChunker = CleanHybridPDFChunker
