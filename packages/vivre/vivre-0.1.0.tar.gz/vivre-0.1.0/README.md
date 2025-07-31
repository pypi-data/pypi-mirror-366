# Vivre

[![codecov](https://codecov.io/github/anidixit64/vivre/graph/badge.svg?token=JJLN3K87G4)](https://codecov.io/github/anidixit64/vivre)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI/CD Pipeline](https://github.com/anidixit64/vivre/actions/workflows/ci.yml/badge.svg)](https://github.com/anidixit64/vivre/actions/workflows/ci.yml)
[![Documentation](https://readthedocs.org/projects/vivre/badge/?version=latest)](https://vivre.readthedocs.io/en/latest/)
[![Languages](https://img.shields.io/badge/Languages-4-green.svg)](https://github.com/anidixit64/vivre#language-support)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)

A Python library for parsing EPUB files and aligning parallel texts.

## Description

Vivre provides tools for processing parallel texts through a complete pipeline: parsing EPUB files, segmenting text into sentences, and aligning sentences between languages using the Gale-Church algorithm. The library offers both a simple API for programmatic use and a powerful command-line interface.

## Features

- **EPUB Parsing**: Robust parsing with content filtering and chapter extraction
- **Sentence Segmentation**: Multi-language sentence segmentation using spaCy
- **Text Alignment**: Statistical text alignment using the Gale-Church algorithm
- **Multiple Output Formats**: JSON, CSV, XML, text, and dictionary formats
- **Language Support**: English, Spanish, French, German, Italian, Portuguese, and more
- **Simple API**: Easy-to-use top-level functions for common tasks
- **Command Line Interface**: Clean CLI with two powerful commands
- **Error Handling**: Comprehensive error handling with helpful messages
- **Type Safety**: Full type hints and validation

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Installation

#### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/anidixit64/vivre.git
cd vivre
```

2. Install the package:
```bash
pip install -e .
```

3. Install required spaCy models:
```bash
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download fr_core_news_sm
python -m spacy download it_core_news_sm
```

#### Option 2: Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/anidixit64/vivre.git
cd vivre
```

2. Build the Docker image:
```bash
docker build -t vivre .
```

3. Use the helper script for different operations:
```bash
# Run test suite (default)
./docker-run.sh

# Drop into interactive shell
./docker-run.sh shell

# Show CLI help
./docker-run.sh cli

# Get help on available options
./docker-run.sh help
```

The Docker setup includes all dependencies and spaCy models pre-installed.

## Usage

### Command Line Interface

Vivre provides a clean CLI with two powerful commands:

```bash
# Parse and analyze an EPUB file
vivre parse book.epub --verbose

# Parse with content display and segmentation
vivre parse book.epub --show-content --segment --language en

# Parse with custom output format
vivre parse book.epub --format csv --output analysis.csv

# Align two EPUB files (language pair is required)
vivre align english.epub french.epub en-fr

# Align with different output formats
vivre align english.epub french.epub en-fr --format json
vivre align english.epub french.epub en-fr --format csv --output alignments.csv
vivre align english.epub french.epub en-fr --format xml --output alignments.xml

# Align with custom parameters
vivre align english.epub french.epub en-fr --c 1.1 --s2 7.0 --gap-penalty 2.5

# Get help
vivre --help
vivre align --help
vivre parse --help
```

**Quick Start Examples:**

```bash
# Parse a book and see its structure
vivre parse sample.epub --verbose

# Align English and French versions of the same book
vivre align english_book.epub french_book.epub en-fr --format json --output alignment.json

# Parse with sentence segmentation
vivre parse sample.epub --segment --language en --format csv --output sentences.csv
```

### Simple API

Vivre provides easy-to-use top-level functions for common tasks:

```python
import vivre

# Parse EPUB and extract chapters
chapters = vivre.read('path/to/epub')
print(f"Found {len(chapters)} chapters")

# Segment chapters into sentences
segmented = chapters.segment('en')  # Specify language for better accuracy
sentences = segmented.get_segmented()

# Quick alignment - returns simple sentence pairs
pairs = vivre.quick_align('english.epub', 'french.epub', 'en-fr')
for source, target in pairs[:5]:
    print(f"EN: {source}")
    print(f"FR: {target}")

# Full alignment with rich output
result = vivre.align('english.epub', 'french.epub', 'en-fr')
print(result.to_json())      # JSON output
print(result.to_csv())       # CSV output
print(result.to_text())      # Formatted text
print(result.to_xml())       # XML output
print(result.to_dict())      # Python dictionary

# Work with Chapters objects seamlessly
source_chapters = vivre.read('english.epub')
target_chapters = vivre.read('french.epub')
result = vivre.align(source_chapters, target_chapters, 'en-fr')  # Works with objects too!

# Get supported languages
languages = vivre.get_supported_languages()
print(f"Supported languages: {languages}")
```

**Quick Start Examples:**

```python
import vivre

# Parse a book
chapters = vivre.read('sample.epub')
print(f"Book has {len(chapters)} chapters")

# Align two books
result = vivre.align('english.epub', 'french.epub', 'en-fr')
print(result.to_json())

# Get sentence pairs
pairs = vivre.quick_align('english.epub', 'french.epub', 'en-fr')
for en, fr in pairs[:3]:
    print(f"EN: {en}")
    print(f"FR: {fr}")
    print()
```

### Advanced Usage

For more control, you can use the individual components:

```python
from vivre import VivreParser, Segmenter, Aligner

# Parse EPUB
parser = VivreParser()
chapters = parser.parse_epub('book.epub')

# Segment text
segmenter = Segmenter()
sentences = segmenter.segment('Hello world!', 'en')

# Align texts
aligner = Aligner()
alignments = aligner.align(['Hello'], ['Bonjour'])

# Pipeline for complex workflows
from vivre import VivrePipeline
pipeline = VivrePipeline('en-fr')
result = pipeline.process_parallel_epubs('english.epub', 'french.epub')
```

## API Reference

### Top-level Functions

- `read(epub_path)` - Parse EPUB and return Chapters object
- `align(source, target, language_pair)` - Align parallel texts, returns AlignmentResult
- `quick_align(source_epub, target_epub, language_pair)` - Simple alignment, returns sentence pairs
- `get_supported_languages()` - Get list of supported language codes

### Classes

- `Chapters` - Container for parsed EPUB chapters with segmentation support
- `AlignmentResult` - Container for alignment results with multiple output formats
- `VivreParser` - Low-level EPUB parser
- `Segmenter` - Sentence segmentation using spaCy
- `Aligner` - Text alignment using Gale-Church algorithm
- `VivrePipeline` - High-level pipeline for complete workflows

## Output Formats

The library supports multiple output formats:

- **JSON**: Structured data for programmatic use
- **CSV**: Tabular data for spreadsheet applications
- **XML**: Hierarchical data for document processing
- **Text**: Human-readable formatted output
- **Dict**: Python dictionary for direct manipulation

## Language Support

Vivre supports the following languages through spaCy models:

- English (`en_core_web_sm`)
- Spanish (`es_core_news_sm`)
- French (`fr_core_news_sm`)
- Italian (`it_core_news_sm`)

These are the languages for which spaCy models are pre-installed and ready to use for EPUB parsing and text segmentation.

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=vivre --cov-report=html

# Run specific test files
pytest tests/test_api.py
pytest tests/test_parser.py
```

### Docker Development

For consistent development environments, use Docker:

```bash
# Build the development image
docker build -t vivre .

# Run tests in Docker
docker run --rm vivre python -m pytest tests/ -v

# Interactive development shell
docker run --rm -it vivre /bin/bash

# Run specific test with coverage
docker run --rm vivre python -m pytest tests/test_api.py --cov=src/vivre/api --cov-report=term-missing
```

### Code Quality

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for detailed information on how to contribute to this project.

### Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/vivre.git
   cd vivre
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Set up development environment**:
   ```bash
   # Install dependencies
   poetry install

   # Install pre-commit hooks
   pre-commit install

   # Install spaCy models
   poetry run python -m spacy download en_core_web_sm
   poetry run python -m spacy download es_core_news_sm
   poetry run python -m spacy download fr_core_news_sm
   poetry run python -m spacy download it_core_news_sm
   ```
5. **Make your changes** and add tests for new functionality
6. **Run tests and quality checks**:
   ```bash
   # Run all tests
   poetry run pytest tests/

   # Run with coverage
   poetry run pytest tests/ --cov=vivre --cov-report=html

   # Run linting and formatting
   poetry run ruff check .
   poetry run ruff format --check .

   # Run type checking
   poetry run mypy src/ tests/
   ```
7. **Ensure all tests pass** and coverage remains >90%
8. **Commit your changes** with clear commit messages
9. **Push to your fork** and submit a pull request

### Development Guidelines

- Follow the existing code style and conventions
- Add type hints to all new functions
- Include docstrings for all public functions and classes
- Write tests for new functionality
- Update documentation as needed
- Ensure all pre-commit hooks pass

For more detailed information, please see our [Contributing Guide](CONTRIBUTING.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### License Summary

- **License**: Apache License 2.0
- **SPDX Identifier**: Apache-2.0
- **Permissions**: Commercial use, modification, distribution, patent use, private use
- **Limitations**: Liability, warranty
- **Conditions**: License and copyright notice

The Apache License 2.0 is a permissive license that allows for:
- Commercial use
- Modification
- Distribution
- Patent use
- Private use

While providing liability protection and requiring license and copyright notice preservation.

For the complete license text, please see the [LICENSE](LICENSE) file in this repository.
