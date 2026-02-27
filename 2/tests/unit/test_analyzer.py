import pytest
import asyncio

from pathlib import Path

from app import FileAnalyzer, FileAnalysis


@pytest.mark.asyncio
async def test_analyze_single_file(temp_files):
    """Test analysis of a single file."""
    file_info = temp_files[0]
    analyzer = FileAnalyzer([])
    result = await analyzer._analyze_single(file_info["path"])

    assert result is not None
    assert isinstance(result, FileAnalysis)
    assert result.word_count == file_info["words"]
    assert result.char_count == file_info["chars"]


@pytest.mark.asyncio
async def test_analyze_all_files(temp_files):
    """Test analysis of all files and global totals."""
    analyzer = FileAnalyzer([fi["path"] for fi in temp_files])
    results = await analyzer.analyze_all()

    assert len(results) == len(analyzer.results) == 4
    assert all([isinstance(r, FileAnalysis) for r in results])

    total_words_expected = sum([fi["words"] for fi in temp_files])
    assert analyzer.total_words == total_words_expected
    total_chars_expected = sum([fi["chars"] for fi in temp_files])
    assert analyzer.total_chars == total_chars_expected


@pytest.mark.asyncio
async def test_file_not_found():
    """Test handling of a missing file."""
    analyzer = FileAnalyzer(["nonexistent_file.txt"])
    result = await analyzer._analyze_single("nonexistent_file.txt")

    assert result is None
    assert analyzer.total_words == 0
    assert analyzer.total_chars == 0
    assert analyzer.results == []


@pytest.mark.asyncio
async def test_mutex_synchronization(temp_files):
    """
    Verify that the lock correctly protects the global counters.
    Runs multiple analyses of the same files concurrently.
    """
    count = 3
    analyzer = FileAnalyzer([], max_concurrent=10)
    tasks = [analyzer._analyze_single(fi["path"]) for fi in temp_files * count]
    await asyncio.gather(*tasks)

    total_words_expected = sum([fi["words"] for fi in temp_files]) * count
    assert analyzer.total_words == total_words_expected
    total_chars_expected = sum([fi["chars"] for fi in temp_files]) * count
    assert analyzer.total_chars == total_chars_expected

    assert len(analyzer.results) == len(temp_files) * count


def test_print_results(capsys, temp_files):
    """Test that print_results() produces expected output."""
    analyzer = FileAnalyzer([fi["path"] for fi in temp_files])

    asyncio.run(analyzer.analyze_all())

    analyzer.print_results()
    captured = capsys.readouterr()

    assert "Analysis Results:" in captured.out
    assert "Total:" in captured.out

