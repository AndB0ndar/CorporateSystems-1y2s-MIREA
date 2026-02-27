import re
import click
import logging

from pathlib import Path
from typing import Optional
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


class FileSearcher:
    """
    High‑level facade for analyzing a text file.

    Args:
        file_path: Path to the file to search.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self._text: Optional[str] = None

    def _ensure_text_loaded(self) -> None:
        """
        Loads the file content into `self._text` if it hasn't been loaded yet.
        """
        if self._text is not None:
            return

        logger.info(f"Starting to read file: {self.file_path}")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self._text = file.read()
            logger.info(f"File '{self.file_path}' successfully read")
            logger.debug(
                f"Size '{self.file_path}': {len(self._text)} characters"
            )

        except Exception as e:
            logger.error(f"Error reading file '{self.file_path}': {e}")
            raise Exception(f"Error reading file '{self.file_path}': {e}")

    def count_words(self, search_word: str) -> AnalysisResult:
        """
        Counts total words and occurrences of the given word in the owned text.

        Args:
            search_word: The word to search for (case‑insensitive).

        Returns:
            An AnalysisResult object containing the counts.
        """
        logger.info(f"Starting search for word: '{search_word}'")
        words = re.findall(r'\w+', self._text.lower())
        total = len(words)
        count = sum(1 for word in words if word == search_word.lower())

        logger.info(f"Analysis completed.")
        logger.debug(
            f" Total words: {total}, occurrences of '{search_word}': {count}"
        )
        return AnalysisResult(total, count, search_word)

    def search(self, search_word: str) -> AnalysisResult:
        """
        Performs analysis on the file:
        total words and occurrences of `search_word`.

        Args:
            search_word: The word to search for.

        Returns:
            An AnalysisResult with the counts.
        """
        self._ensure_text_loaded()
        return self.count_words(search_word)


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


@click.command()
@click.argument(
    'file_path',
    type=click.Path(exists=True, dir_okay=False, readable=True)
)
@click.argument('search_word')
def search(file_path: str, search_word: str) -> None:
    """
    Counts total words in the file
    and the number of occurrences of the specified word.
    FILE_PATH is path to the text file. SEARCH_WORD use to search for.
    """
    setup_logging()

    try:
        searcher = FileSearcher(file_path)
        result = searcher.search(search_word)
        click.echo()
        result.display()
    except Exception as e:
        logger.exception("Critical error during search command execution")
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    search()

