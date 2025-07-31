"""
Integration module for the complete vivre pipeline.

This module provides high-level interfaces for processing parallel texts through
the complete pipeline: parsing EPUB files, segmenting text into sentences, and
aligning sentences between languages.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .align import Aligner
from .parser import VivreParser
from .segmenter import Segmenter


class VivrePipeline:
    """
    High-level interface for the complete vivre text processing pipeline.

    This class provides a convenient interface for processing parallel texts
    through the complete workflow: parsing EPUB files, segmenting text into
    sentences, and aligning sentences between languages.

    The pipeline supports both single-chapter and multi-chapter processing,
    with options for automatic language detection and custom alignment parameters.

    Attributes:
        parser: The EPUB parser instance
        segmenter: The sentence segmenter instance
        aligner: The text aligner instance
        language_pair: The language pair for alignment (e.g., "en-es")

    Example:
        >>> pipeline = VivrePipeline("en-es")
        >>> alignments = pipeline.process_parallel_epubs(
        ...     "english_book.epub", "spanish_book.epub"
        ... )
        >>> for source, target in alignments:
        ...     print(f"EN: {source}")
        ...     print(f"ES: {target}")
    """

    def __init__(
        self,
        language_pair: str = "en-es",
        c: Optional[float] = None,
        s2: Optional[float] = None,
        gap_penalty: Optional[float] = None,
    ) -> None:
        """
        Initialize the vivre pipeline.

        Args:
            language_pair: Language pair for alignment (e.g., "en-es", "en-fr")
            c: Custom mean ratio for alignment (optional)
            s2: Custom variance for alignment (optional)
            gap_penalty: Custom gap penalty for alignment (optional)
        """
        self.parser = VivreParser()
        self.segmenter = Segmenter()
        self.aligner = Aligner(
            language_pair=language_pair,
            c=c,
            s2=s2,
            gap_penalty=gap_penalty,
        )
        self.language_pair = language_pair

    def process_parallel_epubs(
        self,
        source_epub_path: Union[str, Path],
        target_epub_path: Union[str, Path],
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
        max_chapters: Optional[int] = None,
    ) -> List[Tuple[str, str]]:
        """
        Process parallel EPUB files through the complete pipeline.

        This method processes two EPUB files (source and target languages)
        through the complete pipeline: parsing, segmentation, and alignment.

        Args:
            source_epub_path: Path to source language EPUB file
            target_epub_path: Path to target language EPUB file
            source_language: Source language code (optional, auto-detected if None)
            target_language: Target language code (optional, auto-detected if None)
            max_chapters: Maximum number of chapters to process (optional)

        Returns:
            List of aligned sentence pairs (source, target)

        Raises:
            FileNotFoundError: If EPUB files don't exist
            ValueError: If parsing or alignment fails
        """
        # Parse both EPUB files
        source_chapters = self.parser.parse_epub(source_epub_path)
        target_chapters = self.parser.parse_epub(target_epub_path)

        if not source_chapters or not target_chapters:
            raise ValueError("No chapters found in one or both EPUB files")

        # Limit chapters if specified
        if max_chapters:
            source_chapters = source_chapters[:max_chapters]
            target_chapters = target_chapters[:max_chapters]

        # Process each chapter pair
        all_alignments: List[Tuple[str, str]] = []

        for i, (
            (source_title, source_content),
            (target_title, target_content),
        ) in enumerate(zip(source_chapters, target_chapters)):
            # Segment chapters into sentences
            source_sentences = self.segmenter.segment(
                source_content, language=source_language
            )
            target_sentences = self.segmenter.segment(
                target_content, language=target_language
            )

            if source_sentences and target_sentences:
                # Align sentences
                chapter_alignments = self.aligner.align(
                    source_sentences, target_sentences
                )
                all_alignments.extend(chapter_alignments)

        return all_alignments

    def process_parallel_texts(
        self,
        source_text: str,
        target_text: str,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
    ) -> List[Tuple[str, str]]:
        """
        Process parallel text content through the pipeline.

        This method processes two text strings (source and target languages)
        through segmentation and alignment, skipping the parsing step.

        Args:
            source_text: Source language text content
            target_text: Target language text content
            source_language: Source language code (optional, auto-detected if None)
            target_language: Target language code (optional, auto-detected if None)

        Returns:
            List of aligned sentence pairs (source, target)
        """
        # Segment texts into sentences
        source_sentences = self.segmenter.segment(source_text, language=source_language)
        target_sentences = self.segmenter.segment(target_text, language=target_language)

        if not source_sentences or not target_sentences:
            return []

        # Align sentences
        return self.aligner.align(source_sentences, target_sentences)

    def process_parallel_chapters(
        self,
        source_chapters: List[Tuple[str, str]],
        target_chapters: List[Tuple[str, str]],
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
    ) -> List[Tuple[str, str]]:
        """
        Process parallel chapter lists through the pipeline.

        This method processes two lists of chapters (title, content pairs)
        through segmentation and alignment, skipping the parsing step.

        Args:
            source_chapters: List of (title, content) pairs for source language
            target_chapters: List of (title, content) pairs for target language
            source_language: Source language code (optional, auto-detected if None)
            target_language: Target language code (optional, auto-detected if None)

        Returns:
            List of aligned sentence pairs (source, target)
        """
        all_alignments: List[Tuple[str, str]] = []

        for (source_title, source_content), (target_title, target_content) in zip(
            source_chapters, target_chapters
        ):
            # Segment chapters into sentences
            source_sentences = self.segmenter.segment(
                source_content, language=source_language
            )
            target_sentences = self.segmenter.segment(
                target_content, language=target_language
            )

            if source_sentences and target_sentences:
                # Align sentences
                chapter_alignments = self.aligner.align(
                    source_sentences, target_sentences
                )
                all_alignments.extend(chapter_alignments)

        return all_alignments

    def batch_process_epubs(
        self,
        epub_pairs: List[Tuple[Union[str, Path], Union[str, Path]]],
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
        max_chapters_per_book: Optional[int] = None,
    ) -> Dict[str, List[Tuple[str, str]]]:
        """
        Process multiple pairs of EPUB files in batch.

        This method processes multiple pairs of EPUB files, returning alignments
        for each pair in a dictionary keyed by the source file path.

        Args:
            epub_pairs: List of (source_path, target_path) tuples
            source_language: Source language code (optional, auto-detected if None)
            target_language: Target language code (optional, auto-detected if None)
            max_chapters_per_book: Maximum chapters per book (optional)

        Returns:
            Dictionary mapping source file paths to alignment results
        """
        results: Dict[str, List[Tuple[str, str]]] = {}

        for source_path, target_path in epub_pairs:
            try:
                alignments = self.process_parallel_epubs(
                    source_path,
                    target_path,
                    source_language=source_language,
                    target_language=target_language,
                    max_chapters=max_chapters_per_book,
                )
                results[str(source_path)] = alignments
            except Exception as e:
                # Log error but continue with other pairs
                print(f"Error processing {source_path}: {e}")
                results[str(source_path)] = []

        return results

    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about the current pipeline configuration.

        Returns:
            Dictionary containing pipeline configuration information
        """
        return {
            "language_pair": self.language_pair,
            "aligner_parameters": {
                "c": self.aligner.c,
                "s2": self.aligner.s2,
                "gap_penalty": self.aligner.gap_penalty,
            },
            "supported_languages": self.segmenter.get_supported_languages(),
        }


def create_pipeline(
    language_pair: str = "en-es",
    **kwargs: Any,
) -> VivrePipeline:
    """
    Create a new vivre pipeline instance.

    This is a convenience function for creating pipeline instances with
    default or custom parameters.

    Args:
        language_pair: Language pair for alignment
        **kwargs: Additional arguments to pass to VivrePipeline constructor

    Returns:
        Configured VivrePipeline instance

    Example:
        >>> pipeline = create_pipeline("en-fr", gap_penalty=5.0)
        >>> alignments = pipeline.process_parallel_texts(
        ...     "Hello world.", "Bonjour le monde."
        ... )
    """
    return VivrePipeline(language_pair=language_pair, **kwargs)
