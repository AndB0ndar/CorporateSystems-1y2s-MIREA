import pytest
from typing import Callable

from app import FileSearcher


@pytest.fixture
def searcher_with_text() -> Callable[[str], FileSearcher]:
    """
    Fixture that returns factory function
    to create FileSearcher with given text.
    """
    def _create_searcher(text: str) -> FileSearcher:
        fs = FileSearcher(None)
        fs._text = text
        return fs
    return _create_searcher

