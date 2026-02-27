import os
import pytest
import tempfile

from typing import List, Dict, Any


@pytest.fixture
def temp_files() -> List[Dict[str, Any]]:
    """
    Creates temporary text files and returns a list of dictionaries,
    each of which contains:
        - name: the original file name
        - path: the full path to the temporary file
        - words: expected number of words
        - chars: expected number of characters (including spaces and newlines)
    """
    files_content = {
        "test1.txt": {
            "content": "Hello world! This is a test.",
            "words": 6,
            "chars": 28
        },
        "test2.txt": {
            "content": "Python programming\nMultiline\ntext.",
            "words": 4,
            "chars": 34
        },
        "empty.txt": {
            "content": "",
            "words": 0,
            "chars": 0
        },
        "russian.txt": {
            "content": "Привет, мир! Это тест на русском языке.",
            "words": 7,
            "chars": 39
        },
    }

    file_infos = []
    for name, info in files_content.items():
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(info["content"])
            file_infos.append({
                "name": name,
                "path": f.name,
                "words": info["words"],
                "chars": info["chars"]
            })

    yield file_infos

    for info in file_infos:
        os.unlink(info["path"])


@pytest.fixture
def temp_file_paths(temp_file_info) -> List[str]:
    """Returns only a list of temporary file paths."""
    return [info["path"] for info in temp_file_info]

