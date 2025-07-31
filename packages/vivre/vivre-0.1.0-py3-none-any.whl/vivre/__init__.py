"""
Vivre: A library for parsing EPUB files and aligning parallel texts.

This library provides tools for:
- Parsing EPUB files and extracting chapters
- Segmenting text into sentences using spaCy models
- Aligning parallel texts using the Gale-Church algorithm
- Outputting results in various formats (JSON, CSV, XML, text)

Top-level API:
- read(): Parse EPUB files and extract chapters
- align(): Align parallel texts and return AlignmentResult object
- quick_align(): Simple one-liner for basic alignment
- get_supported_languages(): Get list of supported languages

Example:
    # Simple usage with top-level functions
    >>> chapters = vivre.read('path/to/epub')
    >>> print(f"Found {len(chapters)} chapters")
    >>> sentences = chapters.segment()
    >>> result = vivre.align('english.epub', 'french.epub', 'en-fr')
    >>> print(result.to_json())

    # Quick alignment for simple use cases
    >>> pairs = vivre.quick_align('english.epub', 'french.epub', 'en-fr')
    >>> for source, target in pairs[:3]:
    ...     print(f"EN: {source}")
    ...     print(f"FR: {target}")

    # Advanced usage with classes
    >>> from vivre import VivreParser, Segmenter, Aligner
    >>> parser = VivreParser()
    >>> chapters = parser.parse_epub('book.epub')
    >>> segmenter = Segmenter()
    >>> sentences = segmenter.segment('Hello world!', 'en')
    >>> aligner = Aligner()
    >>> alignments = aligner.align(['Hello'], ['Bonjour'])
    >>> for source, target in alignments:
    ...     print(f"EN: {source}")
    ...     print(f"ES: {target}")

Command Line Usage:
    # Parse an EPUB file
    $ vivre parse book.epub

    # Align two EPUB files
    $ vivre align english.epub french.epub --language-pair en-fr --format json

    # Get help
    $ vivre --help
"""

from .align import Aligner
from .api import (
    AlignmentResult,
    Chapters,
    align,
    clear_pipeline_cache,
    get_supported_languages,
    quick_align,
    read,
)
from .integration import VivrePipeline, create_pipeline
from .parser import VivreParser
from .segmenter import Segmenter

__version__ = "0.1.0"

__all__ = [
    "Aligner",
    "Chapters",
    "AlignmentResult",
    "VivreParser",
    "Segmenter",
    "VivrePipeline",
    "create_pipeline",
    "read",
    "align",
    "quick_align",
    "get_supported_languages",
    "clear_pipeline_cache",
]
