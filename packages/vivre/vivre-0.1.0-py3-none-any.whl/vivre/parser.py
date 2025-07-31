"""
EPUB Parser module for the vivre library.

This module provides functionality to load, validate, and parse EPUB files,
extracting chapter content while filtering out non-story elements like
acknowledgements, covers, table of contents, etc.

The VivreParser class implements a robust EPUB parsing system that follows
EPUB standards to extract story content while intelligently filtering out
front matter, back matter, and other non-story elements.

Example:
    >>> from vivre.parser import VivreParser
    >>> parser = VivreParser()
    >>> chapters = parser.parse_epub("book.epub")
    >>> for title, content in chapters:
    ...     print(f"Chapter: {title}")
    ...     print(f"Content: {content[:100]}...")
"""

import os
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from bs4 import BeautifulSoup, Tag
from defusedxml import ElementTree as ET

# XML namespaces for EPUB parsing
NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf",
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
}


class VivreParser:
    """
    A robust parser for EPUB files that extracts story content while filtering
    non-story elements.

    This parser follows EPUB standards to extract chapter titles and content from
    EPUB files, intelligently filtering out front matter, back matter, and other
    non-story content.

    The parser implements a multi-stage approach:
    1. EPUB validation and structure analysis
    2. Table of contents parsing for chapter titles
    3. Content extraction with intelligent filtering
    4. Text cleaning and normalization

    The parser can handle various EPUB formats and structures, including
    different table of contents formats (NCX and HTML) and various content
    organization patterns.

    IMPORTANT: This parser is stateless and can be safely reused for multiple
    EPUB files without state pollution. Each parse_epub() call is independent.

    Attributes:
        file_path: Path to the currently loaded EPUB file, if any.
        _is_loaded: Boolean indicating whether an EPUB file is currently loaded.

    Example:
        >>> parser = VivreParser()
        >>> chapters1 = parser.parse_epub("book1.epub")  # Safe to reuse
        >>> chapters2 = parser.parse_epub("book2.epub")  # No state pollution
        >>> print(f"Found {len(chapters1)} chapters in book1")
        >>> print(f"Found {len(chapters2)} chapters in book2")
    """

    # Multilingual non-story content keywords
    NON_STORY_KEYWORDS = {
        "en": [
            "cover",
            "title",
            "titlepage",
            "front cover",
            "back cover",
            "acknowledgement",
            "acknowledgments",
            "acknowledgements",
            "table of contents",
            "contents",
            "toc",
            "copyright",
            "legal",
            "disclaimer",
            "about the author",
            "author bio",
            "biography",
            "translator",
            "translation",
            "translator's note",
            "preface",
            "foreword",
            "introduction",
            "prologue",
            "epilogue",
            "afterword",
            "appendix",
            "index",
            "bibliography",
            "references",
            "citations",
            "notes",
            "glossary",
            "credits",
            "dedication",
            "colophon",
        ],
        "es": [
            "cubierta",
            "título",
            "página de título",
            "cubierta frontal",
            "cubierta trasera",
            "agradecimientos",
            "reconocimientos",
            "tabla de contenidos",
            "contenidos",
            "índice",
            "derechos de autor",
            "copyright",
            "legal",
            "descargo de responsabilidad",
            "sobre el autor",
            "biografía del autor",
            "biografía",
            "traductor",
            "traducción",
            "nota del traductor",
            "prólogo",
            "prefacio",
            "introducción",
            "epílogo",
            "apéndice",
            "bibliografía",
            "referencias",
            "citas",
            "notas",
            "glosario",
            "créditos",
            "dedicatoria",
            "colofón",
        ],
        "fr": [
            "couverture",
            "titre",
            "page de titre",
            "couverture avant",
            "couverture arrière",
            "remerciements",
            "table des matières",
            "sommaire",
            "index",
            "copyright",
            "droits d'auteur",
            "légal",
            "avertissement",
            "à propos de l'auteur",
            "biographie de l'auteur",
            "biographie",
            "traducteur",
            "traduction",
            "note du traducteur",
            "préface",
            "avant-propos",
            "introduction",
            "épilogue",
            "appendice",
            "bibliographie",
            "références",
            "citations",
            "notes",
            "glossaire",
            "crédits",
            "dédicace",
            "colophon",
        ],
        "de": [
            "umschlag",
            "titel",
            "titelseite",
            "vorderer umschlag",
            "hinterer umschlag",
            "danksagung",
            "danksagungen",
            "inhaltsverzeichnis",
            "inhalt",
            "index",
            "urheberrecht",
            "copyright",
            "rechtlich",
            "haftungsausschluss",
            "über den autor",
            "autorenbiografie",
            "biografie",
            "übersetzer",
            "übersetzung",
            "übersetzernotiz",
            "vorwort",
            "einleitung",
            "epilog",
            "anhang",
            "bibliografie",
            "referenzen",
            "zitate",
            "notizen",
            "glossar",
            "credits",
            "widmung",
            "kolophon",
        ],
        "it": [
            "copertina",
            "titolo",
            "frontespizio",
            "copertina anteriore",
            "copertina posteriore",
            "ringraziamenti",
            "indice",
            "contenuti",
            "copyright",
            "diritti d'autore",
            "legale",
            "disclaimer",
            "sull'autore",
            "biografia dell'autore",
            "biografia",
            "traduttore",
            "traduzione",
            "nota del traduttore",
            "prefazione",
            "introduzione",
            "epilogo",
            "appendice",
            "bibliografia",
            "riferimenti",
            "citazioni",
            "note",
            "glossario",
            "crediti",
            "dedica",
            "colophon",
        ],
    }

    def __init__(self) -> None:
        """
        Initialize the VivreParser.

        Creates a new parser instance ready to parse EPUB files.
        The parser is stateless and can be reused for multiple files.
        """
        self.file_path: Optional[Path] = None
        self._is_loaded: bool = False

    def load_epub(self, file_path: Union[str, Path]) -> bool:
        """
        Load and validate an EPUB file from the given path.

        This method performs comprehensive validation including:
        - Input path validation (None, empty, invalid characters)
        - File existence and accessibility checks
        - EPUB format validation (ZIP structure, required files)
        - Corrupted file detection

        The validation process ensures that the file is a valid EPUB by checking:
        1. File exists and is readable
        2. File is not empty and has minimum size
        3. File has ZIP magic number (PK\x03\x04)
        4. ZIP structure is valid and contains required EPUB files
        5. META-INF/container.xml exists (required for EPUB)

        Args:
            file_path: Path to the EPUB file to load. Can be a string or Path object.

        Returns:
            True if the file was successfully loaded and validated.

        Raises:
            FileNotFoundError: If the EPUB file doesn't exist.
            ValueError: If the file path is invalid, file is not readable,
                       or file is not a valid EPUB (empty, corrupted, wrong format).

        Example:
            >>> parser = VivreParser()
            >>> success = parser.load_epub("book.epub")
            >>> if success:
            ...     print("EPUB loaded successfully")
        """
        # Validate input path
        if file_path is None:
            raise ValueError("File path cannot be None")

        # Convert to string for validation
        if isinstance(file_path, (str, Path)):
            path_str = str(file_path).strip()
        else:
            raise ValueError(
                f"File path must be a string or Path object, "
                f"not {type(file_path).__name__}"
            )

        # Check for empty or whitespace-only paths
        if not path_str:
            raise ValueError("File path cannot be empty")

        # Check for invalid characters in path
        invalid_chars = ["\x00", "\n", "\r", "\t"]
        for char in invalid_chars:
            if char in path_str:
                raise ValueError("File path contains invalid characters")

        # Convert to Path object
        file_path = Path(file_path)

        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {file_path}")

        # Check if it's a file
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            raise ValueError(f"EPUB file is not readable: {file_path}")

        # Basic EPUB validation - check if it's a ZIP file (EPUBs are ZIP archives)
        try:
            with open(file_path, "rb") as f:
                # Check if file is empty
                f.seek(0, 2)  # Seek to end
                file_size = f.tell()
                if file_size == 0:
                    raise ValueError(
                        f"File is not a valid EPUB (empty file): {file_path}"
                    )

                # Check if file is too small to be a valid ZIP
                if file_size < 4:
                    raise ValueError(
                        f"File is not a valid EPUB (file too small): {file_path}"
                    )

                # Check ZIP magic number
                f.seek(0)  # Seek to beginning
                magic = f.read(4)
                if magic != b"PK\x03\x04":
                    raise ValueError(
                        f"File is not a valid EPUB (not a ZIP archive): {file_path}"
                    )

                # Try to open as ZIP to validate structure
                try:
                    with zipfile.ZipFile(file_path, "r") as test_zip:
                        # Check if it has the minimum required files for an EPUB
                        file_list = test_zip.namelist()
                        if "META-INF/container.xml" not in file_list:
                            raise ValueError(
                                f"File is not a valid EPUB "
                                f"(missing container.xml): {file_path}"
                            )
                except zipfile.BadZipFile:
                    raise ValueError(
                        f"File is not a valid EPUB "
                        f"(corrupted ZIP structure): {file_path}"
                    )
        except Exception as e:
            if "File is not a valid EPUB" in str(e):
                raise  # Re-raise our specific validation errors
            raise ValueError(f"Error reading EPUB file: {e}")

            # If we get here, the file is valid
        self.file_path = file_path
        self._is_loaded = True
        return True

    def is_loaded(self) -> bool:
        """
        Check if an EPUB file is currently loaded.

        Returns:
            True if an EPUB file is loaded, False otherwise.
        """
        return self._is_loaded

    def parse_epub(self, file_path: Union[str, Path]) -> List[Tuple[str, str]]:
        """
        Parse an EPUB file and extract chapter titles and text content.

        This method performs comprehensive EPUB parsing following EPUB standards:
        1. Reads container.xml to locate content.opf
        2. Parses content.opf to get manifest and spine
        3. Extracts chapter titles from table of contents
        4. Processes spine items in reading order
        5. Filters out non-story content
        6. Extracts chapter text content

        Args:
            file_path: Path to the EPUB file to parse. Can be a string or Path object.

        Returns:
            List of tuples containing (chapter_title, chapter_text) pairs.
            Only story chapters are included, with non-story content filtered out.

        Raises:
            FileNotFoundError: If the EPUB file doesn't exist.
            ValueError: If the file path is invalid, file is not a valid EPUB,
                       or the EPUB structure cannot be parsed.
        """
        # Use load_epub for validation (DRY principle)
        if not self.load_epub(file_path):
            raise ValueError(f"Failed to load EPUB file: {file_path}")

        chapters: List[Tuple[str, str]] = []

        try:
            with zipfile.ZipFile(file_path, "r") as epub_zip:
                # Step 1: Find the container.xml to locate the content.opf
                container_xml = epub_zip.read("META-INF/container.xml")
                container_root = ET.fromstring(container_xml)

                # Extract the path to the content.opf file
                selector = (
                    './/container:rootfile[@media-type="application/oebps-package+xml"]'
                )
                rootfile_elem = container_root.find(selector, NAMESPACES)
                if rootfile_elem is None:
                    raise ValueError("Could not find content.opf in container.xml")

                content_opf_path = rootfile_elem.get("full-path")
                if not content_opf_path:
                    raise ValueError("No full-path attribute found in rootfile")

                # Step 2: Parse the content.opf to get the spine (reading order)
                content_opf = epub_zip.read(content_opf_path)
                content_root = ET.fromstring(content_opf)

                # Extract metadata (book title and language) - now stateless
                book_metadata = self._extract_metadata(content_opf)
                book_language = book_metadata.get("language", "en")

                # Get the base directory for the content files
                content_dir = Path(content_opf_path).parent

                # Step 3: Extract chapter titles from table of contents using EPUB
                # standards
                chapter_titles = self._extract_chapter_titles(
                    epub_zip, content_dir, content_opf
                )

                # Find the spine to get the reading order
                spine_elem = content_root.find(".//opf:spine", NAMESPACES)
                if spine_elem is None:
                    raise ValueError("Could not find spine in content.opf")

                # Get all itemref elements in the spine
                itemrefs = spine_elem.findall(".//opf:itemref", NAMESPACES)
                if not itemrefs:
                    raise ValueError("No itemref elements found in spine")

                # Step 4: Extract chapter content for each item in the spine
                for itemref in itemrefs:
                    idref = itemref.get("idref")
                    if not idref:
                        continue

                    # Find the manifest item with this id
                    manifest_elem = content_root.find(".//opf:manifest", NAMESPACES)
                    if manifest_elem is None:
                        continue

                    item_elem = manifest_elem.find(
                        f'.//opf:item[@id="{idref}"]', NAMESPACES
                    )
                    if item_elem is None:
                        continue

                    href = item_elem.get("href")
                    if not href:
                        continue

                    # Skip non-story content based on href pattern
                    if self._is_non_story_content("", href, book_language):
                        continue

                    # Construct the full path to the chapter file
                    chapter_path = content_dir / href

                    # Read and parse the chapter file
                    try:
                        chapter_content = epub_zip.read(str(chapter_path))
                        chapter_title, chapter_text = self._extract_chapter_content(
                            chapter_content
                        )

                        # Use title from table of contents if available
                        if href in chapter_titles:
                            chapter_title = chapter_titles[href]

                        # Skip if still a generic title (check without soup for basic
                        # validation)
                        if (
                            len(chapter_title.strip()) < 3
                            or len(chapter_title.split()) > 15
                        ):
                            continue

                        # Skip if text is too short (likely just a title page)
                        if len(chapter_text.strip()) < 100:
                            continue

                        # Skip back matter (files with 'bm' in the name)
                        if "bm" in href.lower():
                            continue

                        chapters.append((chapter_title, chapter_text))
                    except Exception as e:
                        # Skip chapters that can't be parsed
                        warning_msg = f"Warning: Could not parse chapter {href}: {e}"
                        print(warning_msg)
                        continue

        except zipfile.BadZipFile:
            raise ValueError(f"File is not a valid ZIP archive: {file_path}")
        except ET.ParseError as e:
            raise ValueError(f"Error parsing EPUB XML: {e}")
        except Exception as e:
            raise ValueError(f"Error reading EPUB file: {e}")

        return chapters

    def _extract_chapter_content(self, chapter_content: bytes) -> Tuple[str, str]:
        """
        Extract chapter title and text from HTML/XML content using BeautifulSoup.

        This method uses BeautifulSoup to robustly parse HTML/XML content,
        handling malformed HTML that would cause XML parsers to fail.

        Args:
            chapter_content: Raw bytes of the chapter file.

        Returns:
            Tuple of (chapter_title, chapter_text).
        """
        # Decode content and parse with BeautifulSoup
        content_str = chapter_content.decode("utf-8", errors="ignore")
        # Use XML parser for EPUB content to avoid warnings
        soup = BeautifulSoup(content_str, "lxml-xml")

        # Extract title using BeautifulSoup selectors
        title = self._extract_title(soup)

        # Extract text using BeautifulSoup's get_text()
        text = self._extract_text(soup)

        # If we got "Untitled Chapter" but text starts with what looks like a
        # title,
        # try to extract the title from the beginning of the text
        if title == "Untitled Chapter" and text.strip():
            # Look for patterns like "1. Title" or "2. Title" at the beginning
            # Stop at the first sentence boundary or when we hit the actual content
            pattern = r"^(\d+\.?\s+[^.!?]+?)(?=\s+[A-Z]|$)"
            title_match = re.match(pattern, text.strip())
            if title_match:
                title = title_match.group(1).strip()

        # Explicitly remove the title from the text if it appears at the beginning
        if title and title != "Untitled Chapter":
            text = self._remove_title_from_text(text, title)

        return title, text

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract title from BeautifulSoup object using multiple strategies.

        This method tries various selectors to find the chapter title,
        prioritizing more specific selectors over generic ones.

        Args:
            soup: The BeautifulSoup object to search for titles.

        Returns:
            The extracted title, or "Untitled Chapter" if none found.
        """
        # Try different possible title locations in order of preference
        title_selectors = [
            "h1.chapter",  # Specific chapter headings
            "h1[id*='chapter']",  # Chapter headings with chapter in ID
            "h1",  # Any h1
            "h2.chapter",  # Chapter h2 headings
            "h2",  # Any h2
            "h3.chapter",  # Chapter h3 headings
            "h3",  # Any h3
            "title",  # Title tag
            "head title",  # Head title
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                title_text = title_elem.get_text().strip()
                # Skip generic titles that are likely not chapter titles
                if title_text and not self._is_generic_title(title_text, soup):
                    return title_text

        # If no title found, try to get the first meaningful heading text
        for tag in ["h1", "h2", "h3"]:
            for elem in soup.find_all(tag):
                if elem.get_text().strip():
                    title_text = elem.get_text().strip()
                    if not self._is_generic_title(title_text, soup):
                        return title_text

        return "Untitled Chapter"

    def _is_generic_title(self, title: str, soup: BeautifulSoup) -> bool:
        """
        Check if a title is generic and likely not a chapter title.

        This method uses content-agnostic rules to identify titles that are
        probably book titles or other generic content rather than specific
        chapter titles.

        Args:
            title: The title to check.
            soup: BeautifulSoup object of the chapter content.

        Returns:
            True if the title is generic, False otherwise.
        """
        title_lower = title.lower()

        # Check if title is too short (likely not a chapter title)
        if len(title.strip()) < 3:
            return True

        # Check if title is excessively long (likely subtitle or publisher info)
        if len(title.split()) > 15:
            return True

        # Check if title matches the book title from metadata
        # This instance variable is no longer available, so we'll skip this check
        # if self._book_title and title_lower == self._book_title.lower():
        #     return True

        # Check if title matches the HTML document title (but allow if it's the
        # only title found)
        if soup:
            head_title = soup.find("title")
            if head_title and head_title.get_text().strip():
                doc_title = head_title.get_text().strip().lower()
                if title_lower == doc_title:
                    # Only consider it generic if we found other potential titles
                    other_titles = soup.find_all(["h1", "h2", "h3"])
                    # More than just the title tag
                    if len(other_titles) > 1:
                        return True

        # Check if title is just repeated words (likely not a chapter title)
        words = title_lower.split()
        if len(words) > 1 and words.count(words[0]) > 1:
            return True

        return False

    def _extract_chapter_titles(
        self, epub_zip: zipfile.ZipFile, content_dir: Path, content_opf: bytes
    ) -> Dict[str, str]:
        """
        Extract chapter titles from the table of contents using EPUB standards.

        This method follows the EPUB specification to find and parse the
        navigation document:
        - EPUB3: HTML navigation document with properties="nav"
        - EPUB2: NCX file referenced in spine toc attribute

        Args:
            epub_zip: The EPUB zip file.
            content_dir: Base directory for content files.
            content_opf: Raw bytes of the content.opf file.

        Returns:
            Dictionary mapping href to chapter title.
        """
        chapter_titles: Dict[str, str] = {}

        # Find navigation document using EPUB standards
        nav_path = self._find_navigation_document(content_opf, epub_zip, content_dir)

        if nav_path:
            try:
                nav_content = epub_zip.read(nav_path)

                # Determine if it's HTML (EPUB3) or NCX (EPUB2)
                if nav_path.lower().endswith(".ncx"):
                    # Parse NCX file for chapter titles
                    nav_root = ET.fromstring(nav_content)
                    nav_points = nav_root.findall(".//{*}navPoint")

                    for nav_point in nav_points:
                        # Get the title
                        title_elem = nav_point.find(".//{*}text")
                        if title_elem is not None and title_elem.text:
                            title = title_elem.text.strip()

                            # Get the href
                            content_elem = nav_point.find(".//{*}content")
                            if content_elem is not None:
                                src = content_elem.get("src")
                                if src:
                                    # Extract the filename from src (remove anchor)
                                    href = src.split("#")[0]
                                    chapter_titles[href] = title
                else:
                    # Parse HTML navigation document for chapter links
                    soup = BeautifulSoup(nav_content, "lxml-xml")
                    links = soup.find_all("a")

                    for link in links:
                        if isinstance(link, Tag):
                            href_attr = link.get("href")
                            if (
                                href_attr
                                and isinstance(href_attr, str)
                                and link.get_text().strip()
                            ):
                                title = link.get_text().strip()
                                # Clean up href (remove anchor if present)
                                href = href_attr.split("#")[0]
                                chapter_titles[href] = title

            except Exception as e:
                print(
                    f"Warning: Could not extract chapter titles from navigation "
                    f"document: {e}"
                )

        # Fallback to old method if standards-compliant method fails
        if not chapter_titles:
            try:
                # Look for common table of contents files
                toc_files = ["toc.ncx", "OEBPS/toc.ncx", "OEBPS/html/toc.ncx"]

                toc_content = None
                for toc_file in toc_files:
                    try:
                        toc_content = epub_zip.read(toc_file)
                        break
                    except KeyError:
                        continue

                if toc_content:
                    # Parse NCX file for chapter titles
                    toc_root = ET.fromstring(toc_content)
                    nav_points = toc_root.findall(".//{*}navPoint")

                    for nav_point in nav_points:
                        # Get the title
                        title_elem = nav_point.find(".//{*}text")
                        if title_elem is not None and title_elem.text:
                            title = title_elem.text.strip()

                            # Get the href
                            content_elem = nav_point.find(".//{*}content")
                            if content_elem is not None:
                                src = content_elem.get("src")
                                if src:
                                    # Extract the filename from src (remove anchor)
                                    href = src.split("#")[0]
                                    chapter_titles[href] = title

            except Exception as e:
                print(
                    f"Warning: Could not extract chapter titles from fallback TOC: {e}"
                )

        return chapter_titles

    def _extract_text(self, soup: Union[BeautifulSoup, Tag]) -> str:
        """
        Extract all text content from BeautifulSoup object with paragraph structure.

        This method extracts text on a block-level element basis to preserve
        paragraph breaks, which improves sentence segmentation accuracy.

        Args:
            soup: The BeautifulSoup object to extract text from.

        Returns:
            Cleaned text content with preserved paragraph structure.
        """
        # Focus on body content if available
        body = soup.find("body")
        if body is not None and isinstance(body, Tag):
            soup = body

        # Extract text from block-level elements to preserve paragraph structure
        block_elements = soup.find_all(
            ["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article"]
        )

        if block_elements:
            # Extract text from each block element
            text_blocks = []
            for element in block_elements:
                text = element.get_text(separator=" ", strip=True)
                if text:
                    text_blocks.append(text)

            # Join blocks with double newlines to preserve paragraph breaks
            text = "\n\n".join(text_blocks)
        else:
            # Fallback to simple text extraction if no block elements found
            text = soup.get_text(separator=" ", strip=True)

        # Clean up the text while preserving paragraph breaks
        text = re.sub(
            r"\n\s*\n\s*\n+", "\n\n", text
        )  # Normalize multiple paragraph breaks
        text = re.sub(r"[ \t]+", " ", text)  # Normalize whitespace within lines
        text = text.strip()

        return text

    def _is_non_story_content(self, title: str, href: str, book_language: str) -> bool:
        """
        Check if content should be filtered out as non-story content.

        This method identifies various types of non-story content that
        should be excluded from the final chapter list. It prioritizes
        href patterns over title patterns for more robust filtering.

        Args:
            title: The chapter title.
            href: The chapter file path.
            book_language: The book's language code.

        Returns:
            True if the content should be filtered out, False otherwise.
        """
        href_lower = href.lower()

        # PRIORITY 1: Check href for common non-story file patterns
        # These patterns are the most reliable indicators
        non_story_patterns = [
            "cover",
            "title",
            "titlepage",
            "front",
            "back",
            "toc",
            "contents",
            "copyright",
            "legal",
            "acknowledgement",
            "preface",
            "foreword",
            "epilogue",
            "afterword",
            "appendix",
            "index",
            "bibliography",
            "references",
            "glossary",
            "fm",
            "ded",
            "cop",
            "adc",
            "author",
        ]

        if any(pattern in href_lower for pattern in non_story_patterns):
            return True

        # Check for specific file patterns that indicate non-story content
        # Front matter files (fm1, fm2, etc.)
        if re.search(r"fm\d+", href_lower):
            return True

        # Dedication files
        if re.search(r"ded", href_lower):
            return True

        # Copyright files
        if re.search(r"cop", href_lower):
            return True

        # Acknowledgements files
        if re.search(r"adc", href_lower):
            return True

        # Front split files
        if re.search(r"front_split", href_lower):
            return True

        # PRIORITY 2: Only check title if href passed the initial filter
        # This prevents important content from being discarded based on generic titles
        if title:
            # Get the appropriate keyword list for the book's language
            keywords = self.NON_STORY_KEYWORDS.get(
                book_language, self.NON_STORY_KEYWORDS["en"]
            )

            # Check title for common non-story content indicators
            title_lower = title.lower()
            if any(keyword in title_lower for keyword in keywords):
                return True

        return False

    def _extract_metadata(self, content_opf: bytes) -> Dict[str, str]:
        """
        Extract book metadata from content.opf file.

        Args:
            content_opf: Raw bytes of the content.opf file.

        Returns:
            Dictionary containing 'title' and 'language' metadata.
        """
        metadata: Dict[str, str] = {}
        try:
            root = ET.fromstring(content_opf)

            # Extract book title from dc:title
            title_elem = root.find(".//dc:title", NAMESPACES)
            if title_elem is not None and title_elem.text:
                metadata["title"] = title_elem.text.strip()

            # Extract language from dc:language
            lang_elem = root.find(".//dc:language", NAMESPACES)
            if lang_elem is not None and lang_elem.text:
                lang_code = lang_elem.text.strip().lower()
                # Map language codes to our supported languages
                lang_mapping = {
                    "en": "en",
                    "eng": "en",
                    "english": "en",
                    "es": "es",
                    "spa": "es",
                    "spanish": "es",
                    "español": "es",
                    "fr": "fr",
                    "fra": "fr",
                    "french": "fr",
                    "français": "fr",
                    "de": "de",
                    "ger": "de",
                    "german": "de",
                    "deutsch": "de",
                    "it": "it",
                    "ita": "it",
                    "italian": "it",
                    "italiano": "it",
                }
                metadata["language"] = lang_mapping.get(lang_code, "en")

        except Exception as e:
            print(f"Warning: Could not extract metadata: {e}")
        return metadata

    def _find_navigation_document(
        self, content_opf: bytes, epub_zip: zipfile.ZipFile, content_dir: Path
    ) -> Optional[str]:
        """
        Find the navigation document using EPUB standards.

        This method implements the EPUB specification for finding the table of contents:
        - EPUB3: Look for item with properties="nav" in manifest
        - EPUB2: Look for spine toc attribute and find corresponding NCX file

        Args:
            content_opf: Raw bytes of the content.opf file.
            epub_zip: The EPUB zip file.
            content_dir: Base directory for content files.

        Returns:
            Path to the navigation document, or None if not found.
        """
        try:
            root = ET.fromstring(content_opf)

            # EPUB3: Look for navigation document with properties="nav"
            manifest = root.find(".//opf:manifest", NAMESPACES)
            if manifest is not None:
                for item in manifest.findall(".//opf:item", NAMESPACES):
                    properties = item.get("properties")
                    if properties and "nav" in properties.split():
                        href = item.get("href")
                        if href:
                            # Resolve relative path
                            nav_path = content_dir / href
                            return str(nav_path)

            # EPUB2: Look for NCX file referenced in spine
            spine = root.find(".//opf:spine", NAMESPACES)
            if spine is not None:
                toc_id = spine.get("toc")
                if toc_id:
                    # Find the item with this ID in manifest
                    if manifest is not None:
                        for item in manifest.findall(".//opf:item", NAMESPACES):
                            if item.get("id") == toc_id:
                                href = item.get("href")
                                if href:
                                    # Resolve relative path
                                    nav_path = content_dir / href
                                    return str(nav_path)

            return None

        except Exception as e:
            print(f"Warning: Could not find navigation document: {e}")
            return None

    def _remove_title_from_text(self, text: str, title: str) -> str:
        """
        Remove the title from the beginning of the text.

        Args:
            text: The text content.
            title: The title to remove.

        Returns:
            Text with title removed from the beginning.
        """
        if not title or title == "Untitled Chapter":
            return text

        # First, normalize whitespace in the text
        text = re.sub(r"\s+", " ", text.strip())

        # Try exact match first
        title_escaped = re.escape(title)
        text = re.sub(f"^{title_escaped}\\s*", "", text, flags=re.IGNORECASE)

        # Try variations of the title
        title_variations = [
            title.replace(".", ""),  # Remove periods
            title.replace("  ", " "),  # Normalize double spaces
            title.strip(),
            re.sub(r"\s+", " ", title),  # Normalize all whitespace
        ]

        for variation in title_variations:
            if variation and variation != title:
                variation_escaped = re.escape(variation)
                text = re.sub(
                    f"^{variation_escaped}\\s*", "", text, flags=re.IGNORECASE
                )

        # Try removing just the first few words if they match the title
        title_words = title.split()
        if len(title_words) >= 2:
            # Try removing first 2-3 words if they match the title
            for i in range(2, min(4, len(title_words) + 1)):
                partial_title = " ".join(title_words[:i])
                partial_escaped = re.escape(partial_title)
                text = re.sub(f"^{partial_escaped}\\s*", "", text, flags=re.IGNORECASE)

        return text.strip()


# Backward compatibility alias
Parser = VivreParser
