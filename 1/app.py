"""
Console application for text file analysis.
Counts total words and occurrences of a specified word.
Demonstrates ownership/borrowing concepts (in Python context) and includes logging.
"""

import re
import click
import logging

from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """
    Holds the result of a text analysis.

    Attributes:
        total_words: Total number of words found in the text.
        word_count: Number of occurrences of the searched word.
        search_word: The word that was searched for.
    """

    total_words: int
    word_count: int
    search_word: str

    def display(self) -> None:
        """
        Prints the analysis result to the console using click.echo.
        """
        click.echo(f"Total words in file: {self.total_words}")
        click.echo(
            f"Occurrences of the word '{self.search_word}': {self.word_count}"
        )

    def __repr__(self) -> str:
        """Returns a string representation useful for logging."""
        return f"AnalysisResult(total_words={self.total_words}, word_count={self.word_count}, search_word='{self.search_word}')"


class FileReader:
    """
    Responsible for reading the content of a file.

    Args:
        file_path: Path to the file to be read.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def read(self) -> str:
        """
        Reads the entire content of the file and returns it as a string.

        Returns:
            The full text content of the file.

        Raises:
            Exception: If any error occurs during file reading
                (file not found, permissions, etc.).
        """
        logger.info(f"Starting to read file: {self.file_path}")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content: str = file.read()
            logger.info(
                f"File '{self.file_path}' successfully read,"
                f" size: {len(content)} characters"
            )
            return content
        except Exception as e:
            logger.error(f"Error reading file '{self.file_path}': {e}")
            raise Exception(f"Error reading file '{self.file_path}': {e}")


class TextSearcher:
    """
    Analyzes a given text:
    counts total words and occurrences of a specific word.

    Args:
        text: The text content to analyze.
    """

    def __init__(self, text: str) -> None:
        self._text: str = text

    def count_words(self, search_word: str) -> AnalysisResult:
        """
        Counts total words and occurrences of the given word in the owned text.

        Args:
            search_word: The word to search for (case‑insensitive).

        Returns:
            An AnalysisResult object containing the counts.
        """
        logger.info(
            f"Starting text analysis. Searching for word: '{search_word}'"
        )
        text_lower: str = self._text.lower()
        search_lower: str = search_word.lower()

        words: list[str] = re.findall(r'\w+', text_lower)
        total: int = len(words)
        count: int = sum(1 for word in words if word == search_lower)

        logger.info(
            f"Analysis completed."
            f" Total words: {total}, occurrences of '{search_word}': {count}"
        )
        return AnalysisResult(total, count, search_word)


class FileSearcher:
    """
    High‑level facade for analyzing a text file.

    Args:
        file_path: Path to the file to analyze.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self._text: Optional[str] = None

    def _ensure_text_loaded(self) -> None:
        """
        Loads the file content into `self._text` if it hasn't been loaded yet.
        """
        if self._text is None:
            reader = FileReader(self.file_path)
            self._text = reader.read()

    def analyze(self, search_word: str) -> AnalysisResult:
        """
        Performs analysis on the file:
            total words and occurrences of `search_word`.

        Args:
            search_word: The word to search for.

        Returns:
            An AnalysisResult with the counts.
        """
        self._ensure_text_loaded()
        searcher = TextSearcher(self._text)  # type: ignore
        return searcher.count_words(search_word)


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


@click.group()
def cli() -> None:
    """
    Console application for text file analysis.
    Counts total words and the number of occurrences of a specified word.
    """
    pass


@cli.command()
@click.argument(
    'file_path',
    type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.argument('search_word')
def process(file_path: str, search_word: str) -> None:
    """
    Counts total words in the file and the number of occurrences of the specified word.

    Arguments:
        file_path: Path to the text file.
        search_word: Word to search for.
    """
    setup_logging()

    try:
        searcher = FileSearcher(file_path)
        result: AnalysisResult = searcher.analyze(search_word)
        result.display()
    except Exception as e:
        logger.exception("Critical error during process command execution")
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()

