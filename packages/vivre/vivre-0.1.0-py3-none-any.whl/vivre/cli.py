"""
Command-line interface for the vivre library.

This module provides a CLI for common tasks like reading EPUB files
and aligning parallel texts.
"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table

from .api import align as align_api
from .api import read

# Create Typer app and console
app = typer.Typer(
    name="vivre",
    help="A library for processing parallel texts",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def align(
    source_epub: Path = typer.Argument(
        ...,
        help="Path to source language EPUB file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    target_epub: Path = typer.Argument(
        ...,
        help="Path to target language EPUB file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    language_pair: str = typer.Argument(
        ...,
        help="Language pair code (e.g., 'en-es', 'fr-en') - REQUIRED",
    ),
    method: str = typer.Option(
        "gale-church",
        "--method",
        "-m",
        help="Alignment method to use",
        case_sensitive=False,
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format (json, text, csv, xml, dict)",
        case_sensitive=False,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: stdout)",
        file_okay=True,
        dir_okay=False,
    ),
    c: Optional[float] = typer.Option(
        None,
        "--c",
        help="Gale-Church alignment parameter c",
    ),
    s2: Optional[float] = typer.Option(
        None,
        "--s2",
        help="Gale-Church alignment parameter s2",
    ),
    gap_penalty: Optional[float] = typer.Option(
        None,
        "--gap-penalty",
        help="Gale-Church gap penalty parameter",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed progress and statistics",
    ),
) -> None:
    """
    Align two EPUB files using the complete pipeline.

    This command parses both EPUB files, segments the text into sentences,
    and aligns them using the specified method. The language_pair parameter
    is required for accurate alignment.

    Examples:
        $ vivre align english.epub french.epub en-fr
        $ vivre align english.epub spanish.epub es-en --format csv
        $ vivre align english.epub french.epub en-fr --output result.json
    """
    if verbose:
        console.print(
            Panel(
                f"[bold blue]Aligning EPUB files[/bold blue]\n"
                f"Source: [green]{source_epub}[/green]\n"
                f"Target: [green]{target_epub}[/green]\n"
                f"Language pair: [yellow]{language_pair}[/yellow]\n"
                f"Method: [cyan]{method}[/cyan]\n"
                f"Format: [magenta]{format}[/magenta]",
                title="[bold]Alignment Configuration[/bold]",
            )
        )

    # Validate format
    if format.lower() not in ["json", "dict", "text", "csv", "xml"]:
        console.print(
            f"[red]Error:[/red] Invalid format '{format}'. "
            f"Use 'json', 'dict', 'text', 'csv', or 'xml'."
        )
        raise typer.Exit(1)

    # Validate language pair format
    if "-" not in language_pair:
        console.print(
            f"[red]Error:[/red] Invalid language pair '{language_pair}'. "
            f"Use format 'en-fr', 'es-en', etc."
        )
        raise typer.Exit(1)

    try:
        # Build kwargs for alignment parameters
        kwargs = {}
        if c is not None:
            kwargs["c"] = c
        if s2 is not None:
            kwargs["s2"] = s2
        if gap_penalty is not None:
            kwargs["gap_penalty"] = gap_penalty

        # Perform alignment
        if verbose:
            console.print("[yellow]Processing alignment...[/yellow]")

        # Filter out _pipeline from kwargs as it's not a CLI parameter
        align_kwargs = {k: v for k, v in kwargs.items() if k != "_pipeline"}
        result = align_api(
            source_epub,
            target_epub,
            language_pair,
            method,
            **align_kwargs,  # type: ignore[arg-type]
        )

        # Format output based on requested format
        if format.lower() == "json":
            output_text = result.to_json()
        elif format.lower() == "dict":
            output_dict = result.to_dict()
            output_text = json.dumps(output_dict, indent=2, ensure_ascii=False)
        elif format.lower() == "text":
            output_text = result.to_text()
        elif format.lower() == "csv":
            output_text = result.to_csv()
        elif format.lower() == "xml":
            output_text = result.to_xml()
        else:
            output_text = result.to_json()

        # Output result
        if output:
            output.write_text(output_text, encoding="utf-8")
            console.print(f"[green]Results saved to:[/green] {output}")
        else:
            if format.lower() == "json":
                console.print(JSON(output_text))
            else:
                console.print(output_text)

        if verbose:
            corpus_data = result.to_dict()
            total_alignments = sum(
                len(ch.get("alignments", []))
                for ch in corpus_data.get("chapters", {}).values()
            )
            book_title = corpus_data.get("book_title", "Unknown")
            lang_pair = corpus_data.get("language_pair", "Unknown")
            chapter_count = len(corpus_data.get("chapters", {}))

            console.print(
                Panel(
                    f"[bold green]Alignment Complete![/bold green]\n"
                    f"Book: [cyan]{book_title}[/cyan]\n"
                    f"Language pair: [yellow]{lang_pair}[/yellow]\n"
                    f"Chapters: [magenta]{chapter_count}[/magenta]\n"
                    f"Total alignments: [blue]{total_alignments}[/blue]",
                    title="[bold]Summary[/bold]",
                )
            )

    except Exception as e:
        console.print(f"[red]Error during alignment:[/red] {e}")
        raise typer.Exit(1)


def _format_alignments_as_text(output_data: dict) -> str:
    """Format alignments as plain text."""
    lines = []
    lines.append(f"Book: {output_data['book_title']}")
    lines.append(f"Language Pair: {output_data['language_pair']}")
    lines.append(f"Method: {output_data['method']}")
    lines.append(f"Total Alignments: {output_data['total_alignments']}")
    lines.append("=" * 50)

    source_lang, target_lang = output_data["language_pair"].split("-")

    for alignment in output_data["alignments"]:
        lines.append(
            f"\n{alignment['id']}. {source_lang.upper()}: {alignment['source']}"
        )
        lines.append(f"   {target_lang.upper()}: {alignment['target']}")

    return "\n".join(lines)


def _format_alignments_as_csv(output_data: dict) -> str:
    """Format alignments as CSV with enhanced metadata."""
    source_lang, target_lang = output_data["language_pair"].split("-")

    # Enhanced CSV with metadata
    metadata_line = (
        f'"{output_data["book_title"]}","{output_data["language_pair"]}",'
        f'"{output_data["method"]}","{output_data["source_epub"]}",'
        f'"{output_data["target_epub"]}","{output_data["total_alignments"]}"'
    )
    lines = [
        "book_title,language_pair,method,source_epub,target_epub,total_alignments",
        metadata_line,
        "",  # Empty line to separate metadata from alignments
        f"id,{source_lang},{target_lang},source_length,target_length",
    ]

    for alignment in output_data["alignments"]:
        source_text = alignment["source"].replace('"', '""')  # Escape quotes
        target_text = alignment["target"].replace('"', '""')  # Escape quotes
        alignment_line = (
            f'"{alignment["id"]}","{source_text}","{target_text}",'
            f'"{alignment["source_length"]}","{alignment["target_length"]}"'
        )
        lines.append(alignment_line)

    return "\n".join(lines)


def _format_alignments_as_xml(output_data: dict) -> str:
    """Format alignments as XML."""
    source_lang, target_lang = output_data["language_pair"].split("-")

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<alignments>",
        f"  <book_title>{output_data['book_title']}</book_title>",
        f"  <language_pair>{output_data['language_pair']}</language_pair>",
        f"  <method>{output_data['method']}</method>",
        f"  <source_epub>{output_data['source_epub']}</source_epub>",
        f"  <target_epub>{output_data['target_epub']}</target_epub>",
        f"  <total_alignments>{output_data['total_alignments']}</total_alignments>",
    ]

    for alignment in output_data["alignments"]:
        xml_lines.extend(
            [
                f'  <alignment id="{alignment["id"]}">',
                f"    <source>{alignment['source']}</source>",
                f"    <target>{alignment['target']}</target>",
                f"    <source_length>{alignment['source_length']}</source_length>",
                f"    <target_length>{alignment['target_length']}</target_length>",
                "</alignment>",
            ]
        )

    xml_lines.append("</alignments>")

    return "\n".join(xml_lines)


@app.command()
def parse(
    epub_path: Path = typer.Argument(
        ...,
        help="Path to the EPUB file to parse",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    show_content: bool = typer.Option(
        False,
        "--show-content",
        "-c",
        help="Show chapter content (can be very long)",
    ),
    max_chapters: Optional[int] = typer.Option(
        None,
        "--max-chapters",
        "-m",
        help="Maximum number of chapters to display",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format (json, dict, text, csv, xml)",
        case_sensitive=False,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: stdout)",
        file_okay=True,
        dir_okay=False,
    ),
    segment: bool = typer.Option(
        False,
        "--segment",
        "-s",
        help="Segment chapters into sentences",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Language code for segmentation (auto-detected if not specified)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output",
    ),
) -> None:
    """
    Parse and analyze an EPUB file with comprehensive details.

    This command provides detailed analysis of EPUB files including metadata,
    chapter structure, content statistics, and optional sentence segmentation.
    It's the one-stop-shop for analyzing a single EPUB file.

    Examples:
        $ vivre parse book.epub
        $ vivre parse book.epub --show-content --max-chapters 3
        $ vivre parse book.epub --segment --language en --format csv
        $ vivre parse book.epub --verbose --output analysis.json
    """
    if verbose:
        console.print(
            Panel(
                f"[bold blue]Parsing EPUB file[/bold blue]\n"
                f"File: [green]{epub_path}[/green]\n"
                f"Format: [magenta]{format}[/magenta]\n"
                f"Show content: [yellow]{show_content}[/yellow]\n"
                f"Segment: [cyan]{segment}[/cyan]",
                title="[bold]Parse Configuration[/bold]",
            )
        )

    # Validate format
    if format.lower() not in ["json", "dict", "text", "csv", "xml"]:
        console.print(
            f"[red]Error:[/red] Invalid format '{format}'. "
            f"Use 'json', 'dict', 'text', 'csv', or 'xml'."
        )
        raise typer.Exit(1)

    try:
        # Parse the EPUB
        if verbose:
            console.print("[yellow]Parsing EPUB file...[/yellow]")

        chapters = read(epub_path)

        # Segment if requested
        if segment:
            if verbose:
                console.print("[yellow]Segmenting chapters...[/yellow]")
            chapters.segment(language)

        # Prepare output data
        output_data: dict = {
            "file_path": str(epub_path),
            "book_title": chapters.book_title,
            "book_author": "Unknown",  # Could be enhanced to extract from metadata
            "book_language": language or "auto-detected",
            "chapter_count": len(chapters),
            "chapters": [],
        }

        # Process chapters
        for i, (title, content) in enumerate(chapters.chapters, 1):
            if max_chapters and i > max_chapters:
                break

            chapter_data: dict = {
                "number": i,
                "title": title,
                "word_count": len(content.split()),
                "character_count": len(content),
            }

            # Add content if requested
            if show_content:
                chapter_data["content"] = content
            else:
                # Add preview
                preview = content[:200] + "..." if len(content) > 200 else content
                chapter_data["content_preview"] = preview

            # Add segmented sentences if available
            if segment and chapters._segmented_chapters:
                segmented_chapter = chapters._segmented_chapters[i - 1]
                chapter_data["sentences"] = segmented_chapter[1]

            output_data["chapters"].append(chapter_data)

        # Format output based on requested format
        if format.lower() == "json":
            output_text = json.dumps(output_data, indent=2, ensure_ascii=False)
        elif format.lower() == "dict":
            output_text = json.dumps(output_data, indent=2, ensure_ascii=False)
        elif format.lower() == "text":
            output_text = _format_parse_as_text(output_data)
        elif format.lower() == "csv":
            output_text = _format_parse_as_csv(output_data)
        elif format.lower() == "xml":
            output_text = _format_parse_as_xml(output_data)
        else:
            output_text = json.dumps(output_data, indent=2, ensure_ascii=False)

        # Output result
        if output:
            if isinstance(output_text, dict):
                output.write_text(
                    json.dumps(output_text, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            else:
                output.write_text(str(output_text), encoding="utf-8")
            console.print(f"[green]Results saved to:[/green] {output}")
        else:
            if verbose:
                # Show rich formatted summary
                book_title = output_data["book_title"]
                file_path = output_data["file_path"]
                chapter_count = output_data["chapter_count"]
                book_language = output_data["book_language"]

                console.print(
                    Panel(
                        f"[bold blue]Book Title:[/bold blue] {book_title}\n"
                        f"[bold blue]File Path:[/bold blue] {file_path}\n"
                        f"[bold blue]Chapters:[/bold blue] {chapter_count}\n"
                        f"[bold blue]Language:[/bold blue] {book_language}",
                        title="[bold green]Parse Summary[/bold green]",
                    )
                )

                # Show chapter statistics
                if output_data["chapters"]:
                    table = Table(title="Chapter Statistics")
                    table.add_column("#", style="cyan", justify="right")
                    table.add_column("Title", style="magenta")
                    table.add_column("Words", style="yellow", justify="right")
                    table.add_column("Chars", style="green", justify="right")

                    for chapter in output_data["chapters"]:
                        title = chapter["title"]
                        if len(title) > 50:
                            title = title[:50] + "..."
                        table.add_row(
                            str(chapter["number"]),
                            title,
                            str(chapter["word_count"]),
                            str(chapter["character_count"]),
                        )

                    console.print(table)

                    if len(output_data["chapters"]) < output_data["chapter_count"]:
                        console.print(
                            f"[yellow]Note:[/yellow] Showing first "
                            f"{len(output_data['chapters'])} "
                            f"of {output_data['chapter_count']} chapters"
                        )
            else:
                if format.lower() == "json":
                    console.print(JSON(str(output_text)))
                elif isinstance(output_text, dict):
                    console.print(JSON(json.dumps(output_text, ensure_ascii=False)))
                else:
                    console.print(str(output_text))

    except Exception as e:
        console.print(f"[red]Error parsing EPUB:[/red] {e}")
        raise typer.Exit(1)


def _format_parse_as_text(output_data: dict) -> str:
    """Format parse results as plain text."""
    lines = []
    lines.append(f"File: {output_data['file_path']}")
    lines.append(f"Book Title: {output_data['book_title']}")
    lines.append(f"Author: {output_data['book_author']}")
    lines.append(f"Language: {output_data['book_language']}")
    lines.append(f"Chapters: {output_data['chapter_count']}")
    lines.append("=" * 50)

    for chapter in output_data["chapters"]:
        lines.append(f"\nChapter {chapter['number']}: {chapter['title']}")
        lines.append(f"Words: {chapter['word_count']}")
        lines.append(f"Characters: {chapter['character_count']}")
        if "content_preview" in chapter:
            lines.append(f"Preview: {chapter['content_preview']}")
        elif "content" in chapter:
            lines.append(f"Content: {chapter['content']}")

    return "\n".join(lines)


def _format_parse_as_csv(output_data: dict) -> str:
    """Format parse results as CSV."""
    lines = [
        "file_path,book_title,book_author,book_language,chapter_count",
        (
            f'"{output_data["file_path"]}","{output_data["book_title"]}",'
            f'"{output_data["book_author"]}","{output_data["book_language"]}",'
            f'"{output_data["chapter_count"]}"'
        ),
        "",  # Empty line to separate metadata from chapters
        "chapter_number,title,word_count,character_count,content_preview",
    ]

    for chapter in output_data["chapters"]:
        title = chapter["title"].replace('"', '""')  # Escape quotes
        preview = chapter.get("content_preview", "").replace('"', '""')
        lines.append(
            f'"{chapter["number"]}","{title}","{chapter["word_count"]}",'
            f'"{chapter["character_count"]}","{preview}"'
        )

    return "\n".join(lines)


def _format_parse_as_xml(output_data: dict) -> str:
    """Format parse results as XML."""
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<epub_parse>",
        f"  <file_path>{output_data['file_path']}</file_path>",
        f"  <book_title>{output_data['book_title']}</book_title>",
        f"  <book_author>{output_data['book_author']}</book_author>",
        f"  <book_language>{output_data['book_language']}</book_language>",
        f"  <chapter_count>{output_data['chapter_count']}</chapter_count>",
        "  <chapters>",
    ]

    for chapter in output_data["chapters"]:
        char_count_line = (
            f"      <character_count>{chapter['character_count']}</character_count>"
        )
        xml_lines.extend(
            [
                f'    <chapter number="{chapter["number"]}">',
                f"      <title>{chapter['title']}</title>",
                f"      <word_count>{chapter['word_count']}</word_count>",
                char_count_line,
            ]
        )

        if "content_preview" in chapter:
            xml_lines.append(
                f"      <content_preview>{chapter['content_preview']}</content_preview>"
            )
        elif "content" in chapter:
            xml_lines.append(f"      <content>{chapter['content']}</content>")

        xml_lines.append("    </chapter>")

    xml_lines.extend(["  </chapters>", "</epub_parse>"])

    return "\n".join(xml_lines)


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit",
        callback=lambda v: typer.echo("vivre 0.1.0") if v else None,
    ),
) -> None:
    """
    Vivre - A library for processing parallel texts.

    This CLI provides two powerful commands for EPUB processing and text alignment:

    • [bold]parse[/bold] - Comprehensive EPUB analysis with metadata, structure,
      and optional segmentation
    • [bold]align[/bold] - Parallel text alignment using machine learning techniques

    Examples:
        $ vivre parse book.epub --verbose
        $ vivre align english.epub french.epub en-fr --format csv
        $ vivre --help
    """
    pass


if __name__ == "__main__":
    app()
