import pytest
from pathlib import Path

from app import FileSearcher


DATA_DIR = Path(__file__).parent.parent / "data"

EXPECTED = {
    "english.txt": {
        "total": 27,
        "counts": {"hello": 4, "world": 2, "simple": 1}
    },
    "russian.txt": {
        "total": 27,
        "counts": {"привет": 4, "мир": 2, "слово": 2}
    },
    "mixed.txt": {
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
    Compares total word count
    and specific word occurrences against expected values.
    If the file does not exist, the test is skipped.
    """
    file_path = DATA_DIR / filename
    if not file_path.exists():
        pytest.skip(f"Test file {filename} not found in {DATA_DIR}")

    searcher = FileSearcher(str(file_path))

    # 1. Check total word count
    if filename != "large.txt":
        if EXPECTED[filename]["counts"]:
            test_word = next(iter(EXPECTED[filename]["counts"]))
        else:
            test_word = "test"
        result = searcher.search(test_word)
        assert result.total_words == EXPECTED[filename]["total"], \
            f"{filename}: expected total {EXPECTED[filename]['total']}, got {result.total_words}"
    else: # for large.txt, where only ensure it is positive
        result = searcher.search("lorem")
        assert result.total_words > 0, f"{filename}: total words should be positive"

    # 2. Check occurrences for each specified word
    for word, expected_count in EXPECTED[filename]["counts"].items():
        result = searcher.search(word)
        assert result.word_count == expected_count, \
            f"{filename}: word '{word}' expected {expected_count}, got {result.word_count}"

