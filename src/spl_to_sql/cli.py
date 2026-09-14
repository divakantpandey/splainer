"""CLI entry point for spl-to-sql.

Provides the ``spl-to-sql`` command-line interface using Click.

TODO: Wire the pipeline stages together so ``translate`` actually works.
"""

import logging

import click

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(package_name="spl-to-sql")
def main() -> None:
    """spl-to-sql: Translate Splunk SPL queries into SQL."""


@main.command()
@click.argument("query")
@click.option(
    "--dialect",
    type=click.Choice(["postgres", "snowflake"]),
    default="postgres",
    help="Target SQL dialect.",
)
@click.option(
    "--execute/--no-execute",
    default=False,
    help="Execute the generated SQL against the configured database.",
)
def translate(query: str, dialect: str, execute: bool) -> None:
    """Translate an SPL query into SQL.

    Args:
        query: The SPL query string to translate.
        dialect: Target SQL dialect (default: postgres).
        execute: Whether to execute the generated SQL.

    TODO: Implement the full translation pipeline:
        1. Parse SPL query via ANTLR4.
        2. Build SPL IR from parse tree.
        3. Lower SPL IR to Relational IR.
        4. Generate SQL via deterministic codegen (with LLM fallback).
        5. Optionally execute and retry on failure.
    """
    # TODO: Implement pipeline orchestration
    raise NotImplementedError("Translation pipeline not yet implemented")
