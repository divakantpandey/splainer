"""Tests for spl_to_sql.cli."""

from __future__ import annotations

from click.testing import CliRunner

from spl_to_sql.cli import main


class TestMainGroup:
    """Tests for the main CLI group."""

    def test_main_help(self) -> None:
        """The main group should display help text."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "spl-to-sql" in result.output

    def test_main_version(self) -> None:
        """The main group should display the version."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0


class TestTranslateCommand:
    """Tests for the translate command."""

    def test_translate_success(self, simple_spl_query: str) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["translate", "search index=main"])
        assert result.exit_code == 0
        assert "SELECT" in result.output

    def test_translate_with_dialect(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["translate", "--dialect", "snowflake", "search index=main"])
        assert result.exit_code == 0
        assert "SELECT" in result.output
