from click.testing import CliRunner

from app import analyze


def test_cli_basic(temp_files):
    """Test the CLI with basic arguments."""
    runner = CliRunner()
    result = runner.invoke(analyze, [fi["path"] for fi in temp_files])

    assert result.exit_code == 0
    assert "Analysis Results:" in result.output
    assert "Total:" in result.output


def test_cli_max_concurrent(temp_files):
    """Test the --max-concurrent option."""
    runner = CliRunner()
    result = runner.invoke(
        analyze, [fi["path"] for fi in temp_files] + ["--max-concurrent", "2"]
    )

    assert result.exit_code == 0


