"""
Top-level API functions for the vivre library.

This module provides simple, user-friendly functions for common tasks:
- read(): Parse EPUB files and extract chapters
- align(): Align parallel texts and output in various formats
- quick_align(): Simple one-liner for basic alignment
- get_supported_languages(): Get list of supported languages
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .integration import VivrePipeline
from .parser import VivreParser
from .segmenter import Segmenter

# Keep a global pipeline instance to be reused by the API functions
# This is a simple way to speed up consecutive API calls in a single script run.
_pipeline_cache: Dict[str, VivrePipeline] = {}


class AlignmentResult:
    """
    A container for alignment results with multiple output format options.

    This class holds the aligned corpus data and provides methods to
    output it in various formats.
    """

    def __init__(self, corpus: Dict[str, Any]):
        """
        Initialize with aligned corpus data.

        Args:
            corpus: The aligned corpus dictionary
        """
        self._corpus = corpus

    def to_dict(self) -> Dict[str, Any]:
        """Return the corpus as a dictionary."""
        return self._corpus.copy()

    def to_json(self, indent: int = 2) -> str:
        """Return the corpus as JSON string."""
        return json.dumps(self._corpus, indent=indent, ensure_ascii=False)

    def to_text(self) -> str:
        """Return the corpus as formatted text."""
        return _format_as_text(self._corpus)

    def to_csv(self) -> str:
        """Return the corpus as CSV string."""
        return _format_as_csv(self._corpus)

    def to_xml(self) -> str:
        """Return the corpus as XML string."""
        return _format_as_xml(self._corpus)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"AlignmentResult(book_title='{self._corpus.get('book_title', '')}', "
            f"language_pair='{self._corpus.get('language_pair', '')}')"
        )


class Chapters:
    """
    A container for parsed chapters with segmentation capabilities.

    This class holds the parsed chapters and provides methods to segment
    the text into sentences.
    """

    def __init__(self, chapters: List[Tuple[str, str]], book_title: str = ""):
        """
        Initialize with parsed chapters.

        Args:
            chapters: List of (title, content) tuples
            book_title: Title of the book
        """
        self.chapters = chapters
        self.book_title = book_title
        self._segmented_chapters: Optional[List[Tuple[str, List[str]]]] = None
        self._segmenter = Segmenter()

    def segment(self, language: Optional[str] = None) -> "Chapters":
        """
        Segment all chapters into sentences.

        Args:
            language: Language code for segmentation (auto-detected if None)

        Returns:
            Self with segmented chapters
        """
        segmented = []
        for title, content in self.chapters:
            sentences = self._segmenter.segment(content, language)
            segmented.append((title, sentences))

        self._segmented_chapters = segmented
        return self

    def get_segmented(self) -> List[Tuple[str, List[str]]]:
        """Get the segmented chapters."""
        if self._segmented_chapters is None:
            raise ValueError(
                "Chapters must be segmented first. Call .segment() method."
            )
        return self._segmented_chapters

    def __len__(self) -> int:
        """Return the number of chapters."""
        return len(self.chapters)

    def __getitem__(self, index: int) -> Tuple[str, str]:
        """Get a chapter by index."""
        return self.chapters[index]

    def __iter__(self):
        """Iterate over chapters."""
        return iter(self.chapters)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Chapters(book_title='{self.book_title}', chapters={len(self.chapters)})"
        )


def read(epub_path: Union[str, Path]) -> Chapters:
    """
    Parse an EPUB file and extract chapters.

    Args:
        epub_path: Path to the EPUB file

    Returns:
        Chapters object containing parsed chapters

    Raises:
        FileNotFoundError: If the EPUB file doesn't exist
        ValueError: If the file is not a valid EPUB

    Example:
        >>> chapters = vivre.read('path/to/epub')
        >>> print(f"Found {len(chapters)} chapters")
        >>> for title, content in chapters:
        ...     print(f"Chapter: {title}")
    """
    epub_path = Path(epub_path)
    if not epub_path.exists():
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")

    parser = VivreParser()
    try:
        chapters = parser.parse_epub(epub_path)
        book_title = getattr(parser, "_book_title", "")
        return Chapters(chapters, book_title)
    except Exception as e:
        raise ValueError(f"Failed to parse EPUB file {epub_path}: {e}")


def align(
    source: Union[str, Path, Chapters],
    target: Union[str, Path, Chapters],
    language_pair: str,
    method: str = "gale-church",
    _pipeline: Optional[VivrePipeline] = None,  # Add this parameter
    **kwargs: Any,
) -> AlignmentResult:
    """
    Align parallel EPUB files or Chapters objects and return an AlignmentResult.

    This function can accept either file paths or Chapters objects, making it
    flexible for different workflows. The language_pair parameter is required
    for accurate alignment.

    Args:
        source: Source language EPUB file path or Chapters object
        target: Target language EPUB file path or Chapters object
        language_pair: Language pair code (e.g., "en-fr", "es-en") - REQUIRED
        method: Alignment method (currently only "gale-church" supported)
        _pipeline: Optional pre-existing VivrePipeline instance for dependency injection
        **kwargs: Additional arguments passed to the pipeline

    Returns:
        AlignmentResult object with methods for different output formats

    Raises:
        FileNotFoundError: If EPUB files don't exist (when using file paths)
        ValueError: If method is not supported or language_pair is invalid

    Example:
        # Using file paths
        >>> result = vivre.align('english.epub', 'french.epub', 'en-fr')
        >>> print(result.to_json())
        >>> print(result.to_csv())

        # Using Chapters objects (seamless workflow)
        >>> source_chapters = vivre.read('english.epub')
        >>> target_chapters = vivre.read('french.epub')
        >>> result = vivre.align(source_chapters, target_chapters, 'en-fr')
        >>> print(result.to_text())

        # Using dependency injection for better performance
        >>> pipeline = VivrePipeline('en-fr')
        >>> result = vivre.align(
        ...     source_chapters, target_chapters, 'en-fr', _pipeline=pipeline
        ... )
        >>> print(result.to_dict())

        # Get as dictionary for programmatic access
        >>> data = result.to_dict()
        >>> print(f"Found {len(data['chapters'])} chapters")
    """
    if method != "gale-church":
        raise ValueError(
            f"Method '{method}' not supported. Only 'gale-church' is available."
        )

    # Validate language pair format
    if not isinstance(language_pair, str) or "-" not in language_pair:
        raise ValueError(
            f"Invalid language_pair: '{language_pair}'. "
            f"Use format 'en-fr', 'es-en', etc."
        )

    # Parse source and target based on their types
    source_chapters, source_title = _parse_source_or_chapters(source, "source")
    target_chapters, target_title = _parse_source_or_chapters(target, "target")

    # Use the provided pipeline or get one from the cache/create a new one
    pipeline = _pipeline
    if pipeline is None:
        # Simple cache key
        cache_key = f"{language_pair}-{json.dumps(kwargs, sort_keys=True)}"
        if cache_key not in _pipeline_cache:
            _pipeline_cache[cache_key] = VivrePipeline(language_pair, **kwargs)
        pipeline = _pipeline_cache[cache_key]

    # Get book title (prefer source title, fallback to target)
    book_title = source_title or target_title

    # Process chapters and create aligned corpus
    try:
        aligned_corpus = _create_aligned_corpus(
            source_chapters, target_chapters, pipeline, book_title, language_pair
        )

        return AlignmentResult(aligned_corpus)

    except Exception as e:
        raise ValueError(f"Failed to align texts: {e}")


def quick_align(
    source_epub: Union[str, Path],
    target_epub: Union[str, Path],
    language_pair: str,
) -> List[Tuple[str, str]]:
    """
    Quick alignment function that returns simple sentence pairs.

    This is a convenience function for simple use cases where you just
    need sentence pairs without the full corpus structure.

    Args:
        source_epub: Path to source language EPUB
        target_epub: Path to target language EPUB
        language_pair: Language pair code (e.g., "en-fr", "es-en") - REQUIRED

    Returns:
        List of (source_sentence, target_sentence) tuples

    Raises:
        FileNotFoundError: If either EPUB file doesn't exist
        ValueError: If language_pair is invalid

    Example:
        >>> pairs = vivre.quick_align('english.epub', 'french.epub', 'en-fr')
        >>> for source, target in pairs[:3]:
        ...     print(f"EN: {source}")
        ...     print(f"FR: {target}")
    """
    # Validate language pair format
    if not isinstance(language_pair, str) or "-" not in language_pair:
        raise ValueError(
            f"Invalid language_pair: '{language_pair}'. "
            f"Use format 'en-fr', 'es-en', etc."
        )

    # Use the main align function and extract sentence pairs
    result = align(source_epub, target_epub, language_pair)
    corpus = result.to_dict()

    pairs = []
    for chapter_data in corpus["chapters"].values():
        for alignment in chapter_data["alignments"]:
            source_lang, target_lang = language_pair.split("-")
            pairs.append((alignment[source_lang], alignment[target_lang]))

    return pairs


def get_supported_languages() -> List[str]:
    """
    Get a list of supported languages for segmentation.

    Returns:
        List of supported language codes.

    Example:
        >>> languages = vivre.get_supported_languages()
        >>> print(f"Supported languages: {languages}")
    """
    segmenter = Segmenter()
    return list(segmenter._supported_languages.keys())


def clear_pipeline_cache() -> None:
    """
    Clear the pipeline cache.

    This is useful for testing or when you want to free up memory.

    Example:
        >>> vivre.clear_pipeline_cache()
    """
    _pipeline_cache.clear()


def _create_aligned_corpus(
    source_chapters: List[Tuple[str, str]],
    target_chapters: List[Tuple[str, str]],
    pipeline: VivrePipeline,
    book_title: str,
    language_pair: str,
) -> Dict[str, Any]:
    """Create the aligned corpus structure."""
    source_lang, target_lang = language_pair.split("-")

    corpus: Dict[str, Any] = {
        "book_title": book_title,
        "language_pair": language_pair,
        "chapters": {},
    }

    # Process each chapter pair
    for i, (
        (source_title, source_content),
        (target_title, target_content),
    ) in enumerate(zip(source_chapters, target_chapters), 1):
        # Segment both chapters
        source_sentences = pipeline.segmenter.segment(source_content)
        target_sentences = pipeline.segmenter.segment(target_content)

        # Align sentences
        alignments = pipeline.aligner.align(source_sentences, target_sentences)

        # Format alignments
        chapter_alignments = []
        for source_sent, target_sent in alignments:
            chapter_alignments.append(
                {source_lang: source_sent, target_lang: target_sent}
            )

        # Add chapter to corpus
        corpus["chapters"][str(i)] = {
            "title": source_title,  # Use source title as primary
            "alignments": chapter_alignments,
        }

    return corpus


def _format_as_text(corpus: Dict[str, Any]) -> str:
    """Format corpus as plain text."""
    lines = []
    lines.append(f"Book: {corpus['book_title']}")
    lines.append(f"Language Pair: {corpus['language_pair']}")
    lines.append("=" * 50)

    for chapter_num, chapter_data in corpus["chapters"].items():
        lines.append(f"\nChapter {chapter_num}: {chapter_data['title']}")
        lines.append("-" * 30)

        for i, alignment in enumerate(chapter_data["alignments"], 1):
            source_lang, target_lang = corpus["language_pair"].split("-")
            lines.append(f"{i}. {source_lang.upper()}: {alignment[source_lang]}")
            lines.append(f"   {target_lang.upper()}: {alignment[target_lang]}")
            lines.append("")

    return "\n".join(lines)


def _format_as_csv(corpus: Dict[str, Any]) -> str:
    """Format corpus as CSV."""
    source_lang, target_lang = corpus["language_pair"].split("-")

    lines = [f"chapter,title,{source_lang},{target_lang}"]

    for chapter_num, chapter_data in corpus["chapters"].items():
        title = chapter_data["title"].replace('"', '""')  # Escape quotes

        for alignment in chapter_data["alignments"]:
            source_text = alignment[source_lang].replace('"', '""')
            target_text = alignment[target_lang].replace('"', '""')
            lines.append(f'"{chapter_num}","{title}","{source_text}","{target_text}"')

    return "\n".join(lines)


def _format_as_xml(corpus: Dict[str, Any]) -> str:
    """Format corpus as XML."""
    source_lang, target_lang = corpus["language_pair"].split("-")

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<alignments>",
        f"  <book_title>{corpus['book_title']}</book_title>",
        f"  <language_pair>{corpus['language_pair']}</language_pair>",
        f"  <total_alignments>{len(corpus['chapters'])}</total_alignments>",
    ]

    for chapter_num, chapter_data in corpus["chapters"].items():
        xml_lines.extend(
            [
                f'  <chapter number="{chapter_num}">',
                f"    <title>{chapter_data['title']}</title>",
                "    <alignments>",
            ]
        )

        for alignment in chapter_data["alignments"]:
            xml_lines.extend(
                [
                    "      <alignment>",
                    f"        <{source_lang}>{alignment[source_lang]}</{source_lang}>",
                    f"        <{target_lang}>{alignment[target_lang]}</{target_lang}>",
                    "      </alignment>",
                ]
            )

        xml_lines.extend(["    </alignments>", "  </chapter>"])

    xml_lines.append("</alignments>")
    return "\n".join(xml_lines)


def _parse_source_or_chapters(
    source: Union[str, Path, Chapters], name: str
) -> Tuple[List[Tuple[str, str]], str]:
    """
    Parse source or target, whether it's a file path or Chapters object.

    Args:
        source: File path or Chapters object
        name: Name for error messages ("source" or "target")

    Returns:
        Tuple of (chapters, book_title)
    """
    if isinstance(source, Chapters):
        # Already parsed Chapters object
        return source.chapters, source.book_title
    else:
        # File path - parse the EPUB
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(
                f"{name.capitalize()} EPUB file not found: {source_path}"
            )

        parser = VivreParser()
        chapters = parser.parse_epub(source_path)

        # Extract book title from EPUB metadata
        book_title = source_path.stem  # Default to filename
        try:
            # Load the EPUB and extract metadata
            import zipfile

            with zipfile.ZipFile(source_path, "r") as epub_zip:
                # Find content.opf
                container_xml = epub_zip.read("META-INF/container.xml")
                from defusedxml import ElementTree as ET

                container_root = ET.fromstring(container_xml)

                # Extract the path to the content.opf file
                selector = (
                    './/container:rootfile[@media-type="application/oebps-package+xml"]'
                )
                rootfile_elem = container_root.find(
                    selector,
                    {"container": "urn:oasis:names:tc:opendocument:xmlns:container"},
                )
                if rootfile_elem is not None:
                    content_opf_path = rootfile_elem.get("full-path")
                    if content_opf_path:
                        content_opf = epub_zip.read(content_opf_path)
                        content_root = ET.fromstring(content_opf)

                        # Extract book title from dc:title
                        title_elem = content_root.find(
                            ".//dc:title",
                            {"dc": "http://purl.org/dc/elements/1.1/"},
                        )
                        if title_elem is not None and title_elem.text:
                            book_title = title_elem.text.strip()
        except Exception:
            # If metadata extraction fails, use filename
            pass

        return chapters, book_title
