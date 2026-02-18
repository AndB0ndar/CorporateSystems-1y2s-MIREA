"""
Unit tests for the TextSearcher and FileSearcher classes using pytest.
Tests include both in‑memory analysis and real file analysis from the ./data/ directory.
"""

import pytest
from pathlib import Path
from typing import Callable

from app import FileSearcher, TextSearcher, AnalysisResult


# ------------------------------------------------------------------------------
# Fixtures and helpers
# ------------------------------------------------------------------------------

@pytest.fixture
def searcher_with_text() -> Callable[[str], TextSearcher]:
    """
    Fixture that returns a factory function to create a TextSearcher with given text.
    """
    def _create_searcher(text: str) -> TextSearcher:
        return TextSearcher(text)
    return _create_searcher


def check_result(result: AnalysisResult, expected_total: int, expected_count: int, expected_word: str) -> None:
    """
    Helper to assert that an AnalysisResult matches expected values.
    """
    assert result.total_words == expected_total
    assert result.word_count == expected_count
    assert result.search_word == expected_word


# ------------------------------------------------------------------------------
# Tests for in‑memory analysis
# ------------------------------------------------------------------------------

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
    searcher_with_text: Callable[[str], TextSearcher],
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


def test_case_insensitivity(searcher_with_text: Callable[[str], TextSearcher]) -> None:
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


def test_word_not_found(searcher_with_text: Callable[[str], TextSearcher]) -> None:
    """
    When the word is not present, count should be zero.
    """
    searcher = searcher_with_text("one two three")
    result = searcher.count_words("four")
    check_result(result, 3, 0, "four")

# ------------------------------------------------------------------------------
# Tests for real file analysis using ./data/ files
# ------------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "sample_english.txt": {
        "total": 27,
        "counts": {"hello": 4, "world": 2, "simple": 1}
    },
    "sample_russian.txt": {
        "total": 27,
        "counts": {"привет": 4, "мир": 2, "слово": 2}
    },
    "sample_mixed.txt": {
        "total": 22,
        "counts": {"слово": 5, "тест123": 1, "another": 1}
    },
    "empty.txt": {
        "total": 0,
        "counts": {"any": 0}
    },
    "large.txt": {
        "total": None,
        "counts": {"lorem": 2, "ipsum": 2}
    }
}


@pytest.mark.parametrize("filename", list(EXPECTED.keys()))
def test_file_analysis(filename: str) -> None:
    """
    Test FileSearcher on a real text file located in ./data/.
    Compares total word count and specific word occurrences against expected values.
    If the file does not exist, the test is skipped.
    """
    file_path = DATA_DIR / filename
    if not file_path.exists():
        pytest.skip(f"Test file {filename} not found in {DATA_DIR}")

    searcher = FileSearcher(str(file_path))

    # 1. Check total word count (except for large.txt, where we only ensure it's positive)
    if filename != "large.txt":
        # Pick any word that is known to exist in the file (first key in counts, or "test" for empty)
        if EXPECTED[filename]["counts"]:
            test_word = next(iter(EXPECTED[filename]["counts"]))
        else:
            test_word = "test"
        result = searcher.analyze(test_word)
        assert result.total_words == EXPECTED[filename]["total"], \
            f"{filename}: expected total {EXPECTED[filename]['total']}, got {result.total_words}"
    else:
        # For large.txt, just verify that total_words > 0 (using a word that appears)
        result = searcher.analyze("lorem")
        assert result.total_words > 0, f"{filename}: total words should be positive"

    # 2. Check occurrences for each specified word
    for word, expected_count in EXPECTED[filename]["counts"].items():
        result = searcher.analyze(word)
        assert result.word_count == expected_count, \
            f"{filename}: word '{word}' expected {expected_count}, got {result.word_count}"

