import pytest
from typing import Callable

from app import FileSearcher

from utils import check_result


@pytest.mark.parametrize("text, word, expected_total, expected_count", [
    ("Hello world! Hello everyone.", "hello", 4, 2),
    ("Python python PYTHON", "python", 3, 3),
    ("One two three", "four", 3, 0),
    ("", "test", 0, 0),
    ("Слово, слово, ещё слово.", "слово", 4, 3),
    ("  Много   пробелов  и знаков препинания!!! ", "много", 5, 1),
    ("word1,word2;word3.word4!word5?word6", "word1", 6, 1),
])
def test_count_words(
    searcher_with_text: Callable[[str], FileSearcher],
    text: str,
    word: str,
    expected_total: int,
    expected_count: int
) -> None:
    """
    Parametrized test for various inputs.
    """
    searcher = searcher_with_text(text)
    result = searcher.count_words(word)
    check_result(result, expected_total, expected_count, word)


def test_case_insensitivity(
    searcher_with_text: Callable[[str], FileSearcher]
) -> None:
    """
    Verify that the search is case‑insensitive.
    """
    text = "Apple APPLE appLe"
    searcher = searcher_with_text(text)

    result = searcher.count_words("apple")
    check_result(result, 3, 3, "apple")

    result = searcher.count_words("APPLE")
    check_result(result, 3, 3, "APPLE")

    result = searcher.count_words("AppLe")
    check_result(result, 3, 3, "AppLe")


def test_word_not_found(
    searcher_with_text: Callable[[str], FileSearcher]
) -> None:
    """
    When the word is not present, count should be zero.
    """
    searcher = searcher_with_text("one two three")
    result = searcher.count_words("four")
    check_result(result, 3, 0, "four")

