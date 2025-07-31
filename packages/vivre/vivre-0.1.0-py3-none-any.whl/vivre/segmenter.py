"""
Text segmentation module for the vivre library.

This module provides functionality to segment text into sentences or other units.
"""

from typing import List, Optional

import langdetect
import spacy
from spacy.language import Language


class Segmenter:
    """
    A text segmenter that splits text into sentences using spaCy models.

    This class provides methods to segment text into meaningful units
    using language detection and spaCy's sentence tokenization.

    Batch Processing:
    - segment_batch(): For single-language batches (requires explicit language)
    - segment_mixed_batch(): For mixed-language batches (auto-detects languages)

    Note: Some languages (Arabic, Hindi, Thai) use a general-purpose multilingual
    model (xx_ent_wiki_sm) which may provide lower segmentation accuracy compared
    to dedicated language models. For higher accuracy with these languages, consider
    using larger (_lg) or transformer (_trf) spaCy models if available.
    """

    def __init__(self) -> None:
        """Initialize the Segmenter instance."""
        self._models: dict[str, Language] = {}  # Cache by model_name only
        self._supported_languages = {
            "en": "en_core_web_sm",
            "es": "es_core_news_sm",
            "fr": "fr_core_news_sm",
            "de": "de_core_news_sm",
            "it": "it_core_news_sm",
            "pt": "pt_core_news_sm",
            "nl": "nl_core_news_sm",
            "pl": "pl_core_news_sm",
            "ru": "ru_core_news_sm",
            "ja": "ja_core_news_sm",
            "zh": "zh_core_web_sm",
            "ko": "ko_core_news_sm",
            "ar": "xx_ent_wiki_sm",  # Arabic uses multilingual model
            "hi": "xx_ent_wiki_sm",  # Hindi uses multilingual model
            "th": "xx_ent_wiki_sm",  # Thai uses multilingual model
        }

    def _detect_language(self, text: str) -> str:
        """
        Detect the language of the given text using langdetect.

        Args:
            text: The text to detect language for.

        Returns:
            Language code (e.g., 'en', 'es', 'fr').
        """
        try:
            # Use langdetect for robust language detection
            detected_lang = langdetect.detect(text)

            # Validate that the detected language is supported
            if detected_lang in self._supported_languages:
                return detected_lang

            # If detected language is not supported, try to map to supported language
            # Handle common language code variations
            lang_mapping = {
                "zh-cn": "zh",  # Chinese (Simplified)
                "zh-tw": "zh",  # Chinese (Traditional)
                "zh-hans": "zh",  # Chinese (Simplified)
                "zh-hant": "zh",  # Chinese (Traditional)
                "ja-jp": "ja",  # Japanese
                "ko-kr": "ko",  # Korean
                "ar-sa": "ar",  # Arabic (Saudi Arabia)
                "hi-in": "hi",  # Hindi (India)
                "th-th": "th",  # Thai (Thailand)
            }

            if detected_lang in lang_mapping:
                return lang_mapping[detected_lang]

            # Default to English for unsupported languages
            return "en"

        except (langdetect.LangDetectException, Exception):
            # Fallback to English if language detection fails
            return "en"

    def _load_model(self, lang_code: str) -> Language:
        """
        Load or get cached spaCy model for the given language.

        Args:
            lang_code: Language code (e.g., 'en', 'es', 'fr').

        Returns:
            Loaded spaCy language model.

        Raises:
            OSError: If the model is not installed.
        """
        if lang_code not in self._supported_languages:
            raise ValueError(f"Unsupported language: {lang_code}")

        model_name = self._supported_languages[lang_code]

        # Check if this specific model is already loaded
        if model_name in self._models:
            # Model is already loaded, just update the mapping
            return self._models[model_name]

        # Load the model with only necessary components for sentence segmentation
        try:
            # Disable unnecessary components to improve performance
            # We only need the sentence segmenter (senter), not tagger, parser, NER,
            # etc.
            model = spacy.load(
                model_name,
                disable=["tagger", "parser", "ner", "lemmatizer", "attribute_ruler"],
            )

            # Add sentencizer if it's not already in the pipeline
            if "sentencizer" not in model.pipe_names:
                model.add_pipe("sentencizer")

            self._models[model_name] = model
            return model
        except OSError:
            raise OSError(
                f"spaCy model '{model_name}' not found. "
                f"Install it with: python -m spacy download {model_name}"
            )

    def segment(self, text: str, language: Optional[str] = None) -> List[str]:
        """
        Segment text into sentences using spaCy models.

        Args:
            text: The text to segment.
            language: Optional language code (e.g., 'en', 'es', 'fr').
                     If provided, this language will be used without question.
                     If None, language will be auto-detected using langdetect.
                     User override takes precedence for maximum accuracy.

        Returns:
            List of sentence segments.

        Raises:
            OSError: If the required spaCy model is not installed.
            ValueError: If the language is not supported.
        """
        if text is None or not text or not text.strip():
            return []

        # Use user-provided language if available, otherwise auto-detect
        if language is not None:
            # Validate user-provided language
            if not self.is_language_supported(language):
                raise ValueError(f"Unsupported language: {language}")
            detected_language = language
        else:
            # Auto-detect language as fallback
            detected_language = self._detect_language(text)

        # Load the appropriate spaCy model
        nlp = self._load_model(detected_language)

        # Process the text with spaCy
        doc = nlp(text.strip())

        # Extract sentences
        sentences = []
        for sent in doc.sents:
            sentence_text = sent.text.strip()
            if sentence_text:
                sentences.append(sentence_text)

        return sentences

    def segment_batch(self, texts: List[str], language: str) -> List[List[str]]:
        """
        Segment multiple texts into sentences using spaCy's optimized batch processing.

        This method uses spaCy's pipe() method for efficient batch processing,
        making better use of multi-core CPUs and improving performance
        significantly for bulk tasks.

        IMPORTANT: All texts in the batch must be of the same language.
        Mixed-language batches are not supported and will result in incorrect
        segmentation. Use separate batch calls for different languages.

        Args:
            texts: List of texts to segment.
            language: Language code (e.g., 'en', 'es', 'fr').
                     All texts in the batch must be of this language.

        Returns:
            List of sentence segments for each input text.

        Raises:
            OSError: If the required spaCy model is not installed.
            ValueError: If the language is not supported or if texts list is empty.
        """
        if not texts:
            return []

        # Validate language parameter
        if not self.is_language_supported(language):
            raise ValueError(f"Unsupported language: {language}")

        # Load the appropriate spaCy model
        nlp = self._load_model(language)

        # Process texts in batch using spaCy's optimized pipe method
        results = []
        for doc in nlp.pipe([text.strip() for text in texts if text and text.strip()]):
            sentences = []
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                if sentence_text:
                    sentences.append(sentence_text)
            results.append(sentences)

        return results

    def segment_mixed_batch(self, texts: List[str]) -> List[List[str]]:
        """
        Segment multiple texts that may be in different languages.

        This method automatically detects the language of each text and groups
        them by language for efficient batch processing. This is the recommended
        method for processing mixed-language text collections.

        Args:
            texts: List of texts to segment (can be in different languages).

        Returns:
            List of sentence segments for each input text, in the same order.

        Raises:
            OSError: If required spaCy models are not installed.
            ValueError: If texts list is empty.
        """
        if not texts:
            return []

        # Group texts by detected language
        language_groups: dict[str, list[tuple[int, str]]] = {}

        for i, text in enumerate(texts):
            if not text or not text.strip():
                # Empty text - will be handled later
                continue

            detected_lang = self._detect_language(text)
            if detected_lang not in language_groups:
                language_groups[detected_lang] = []
            language_groups[detected_lang].append((i, text))

        # Initialize results list with empty lists
        results: List[List[str]] = [[] for _ in texts]

        # Process each language group separately
        for lang_code, text_items in language_groups.items():
            if not self.is_language_supported(lang_code):
                # Fallback to English for unsupported languages
                lang_code = "en"

            # Extract just the texts for this language group
            indices, lang_texts = zip(*text_items)

            # Process this language group
            lang_results = self.segment_batch(list(lang_texts), lang_code)

            # Place results back in original positions
            for idx, sentences in zip(indices, lang_results):
                results[idx] = sentences

        return results

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes.

        Note: Some languages (Arabic, Hindi, Thai) use a general-purpose multilingual
        model (xx_ent_wiki_sm) which may provide lower segmentation accuracy compared
        to dedicated language models. For higher accuracy with these languages, consider
        using larger (_lg) or transformer (_trf) spaCy models if available.

        Returns:
            List of supported language codes.
        """
        return list(self._supported_languages.keys())

    def is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported.

        Args:
            language: Language code to check.

        Returns:
            True if language is supported, False otherwise.
        """
        return language in self._supported_languages
