from app import AnalysisResult


def check_result(
    result: AnalysisResult,
    expected_total: int,
    expected_count: int,
    expected_word: str
) -> None:
    """
    Helper to assert that an AnalysisResult matches expected values.
    """
    assert isinstance(result, AnalysisResult)

    assert result.total_words == expected_total
    assert result.word_count == expected_count
    assert result.search_word == expected_word

