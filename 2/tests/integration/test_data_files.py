import pytest
import asyncio

from pathlib import Path
from click.testing import CliRunner

from app import FileAnalyzer, analyze


DATA_DIR = Path(__file__).parent.parent.parent / "data"

DATA_EXPECTED = {
    "sample_english.txt": {"words": 27, "chars": 156},
    "sample_russian.txt": {"words": 27, "chars": 175},
    "empty.txt": {"words": 0, "chars": 0},
    "large.txt": {"words": 138, "chars": 900},
}


@pytest.mark.skipif(
    not DATA_DIR.exists(), reason="Directory ./data/ not found"
)
@pytest.mark.parametrize("filename", list(DATA_EXPECTED.keys()))
def test_data_files(filename):
    """Test analysis of files located in ./data/."""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        pytest.skip(f"File {filename} not found in ./data/")

    analyzer = FileAnalyzer([str(file_path)])
    results = asyncio.run(analyzer.analyze_all())

    assert len(results) == 1
    assert results[0].word_count == DATA_EXPECTED[filename]["words"]
    assert results[0].char_count == DATA_EXPECTED[filename]["chars"]


@pytest.mark.skipif(
    not DATA_DIR.exists(), reason="Directory ./data/ not found"
)
def test_cli_with_data_files():
    """Run the CLI on all files found in ./data/."""
    files = [str(f) for f in DATA_DIR.glob("*.txt") if f.is_file()]
    if not files:
        pytest.skip("No .txt files in ./data/")

    runner = CliRunner()
    result = runner.invoke(analyze, files)

    assert result.exit_code == 0
    assert "Analysis Results:" in result.output

