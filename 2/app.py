import click
import logging
import asyncio
import aiofiles

from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


logger = logging.getLogger(__name__)


@dataclass
class FileAnalysis:
    """
    Holds analysis results for a single file.

    Attributes:
        file_name: Name of the file (without path).
        word_count: Number of words found in the file.
        char_count: Total number of characters (including whitespace).
    """
    file_name: str
    word_count: int
    char_count: int


class FileAnalyzer:
    """
    Manages concurrent analysis of multiple files using asyncio.

    Args:
        file_paths: List of paths to the files to be analyzed.
        max_concurrent: Maximum number of files processed simultaneously.
    """

    def __init__(self, file_paths: List[str], max_concurrent: int = 5) -> None:
        self.file_paths = file_paths

        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.lock = asyncio.Lock()

        self.total_words: int = 0
        self.total_chars: int = 0
        self.results: List[FileAnalysis] = []

    async def _analyze_single(self, file_path: str) -> Optional[FileAnalysis]:
        """
        Asynchronously read and analyze one file.

        Args:
            file_path: Path to the file to analyze.

        Returns:
            A FileAnalysis object if successful, otherwise None.

        Logs errors if the file is not found or cannot be read.
        """
        async with self.semaphore:
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
                return None
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return None

            words = content.split()
            word_count = len(words)
            char_count = len(content)

            result = FileAnalysis(
                file_name=Path(file_path).name,
                word_count=word_count,
                char_count=char_count
            )

            # Update global totals under lock protection
            async with self.lock:
                self.total_words += word_count
                self.total_chars += char_count
                self.results.append(result)

            logger.debug(
                f"File {file_path} processed:"
                f" {word_count} words, {char_count} characters"
            )
            return result

    async def analyze_all(self) -> List[FileAnalysis]:
        """
        Launch concurrent analysis for all files.

        Returns:
            A list of FileAnalysis objects for successfully processed files.
        """
        tasks = [self._analyze_single(path) for path in self.file_paths]
        results = await asyncio.gather(*tasks)
        successful = [r for r in results if r is not None]
        return successful

    def print_results(self) -> None:
        """Display the analysis results in the console."""
        click.echo("\nAnalysis Results:")
        for i, res in enumerate(self.results, 1):
            click.echo(
                f"{i}. {res.file_name}:"
                f" {res.word_count} words, {res.char_count} characters"
            )
        click.echo(
            f"Total: {self.total_words} words, {self.total_chars} characters."
        )


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

# ----------------------------------------------------------------------
# Command Line Interface (Click)
# ----------------------------------------------------------------------

@click.command()
@click.argument(
    'files',
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.option(
    '--max-concurrent',
    '-c',
    default=5,
    show_default=True,
    help='Maximum number of files to process concurrently'
)
def analyze(files: List[str], max_concurrent: int) -> None:
    """
    Analyze text files: count words and characters in each file.

    FILES: one or more text file paths to be analyzed.
    """
    setup_logging()

    logger.info(
        f"Starting analysis for {len(files)} files"
        f" (max concurrent: {max_concurrent})"
    )
    analyzer = FileAnalyzer(list(files), max_concurrent)

    try:
        asyncio.run(analyzer.analyze_all())
        analyzer.print_results()
    except Exception as e:
        logger.exception("Critical error during analysis")
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    analyze()

