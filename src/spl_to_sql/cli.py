"""CLI entry point for spl-to-sql.

Provides the ``spl-to-sql`` command-line interface using Click.

TODO: Wire the pipeline stages together so ``translate`` actually works.
"""

import logging

import click

from spl_to_sql.config import SplToSqlConfig
from spl_to_sql.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(package_name="spl-to-sql")
def main() -> None:
    """spl-to-sql: Translate Splunk SPL queries into SQL."""
    # Load config and configure logging early
    config = SplToSqlConfig.from_env()
    configure_logging(config.log_level)


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
    """
    try:
        from spl_to_sql.parser import parse
        from spl_to_sql.ir.spl_ir.builder import build_spl_ir
        from spl_to_sql.ir.relational_ir.lowering import lower_to_relational
        from spl_to_sql.codegen.deterministic import generate_sql
        
        click.echo(f"Translating query: {query}")
        
        # 1. Parse
        tree = parse(query)
        
        # 2. SPL IR
        spl_ir = build_spl_ir(tree)
        
        # 3. Relational IR
        relational_ir = lower_to_relational(spl_ir)
        
        # 4. Codegen
        sql = generate_sql(relational_ir)
        
        # Always show tree for now based on user instruction
        from rich.console import Console
        from rich.tree import Tree
        
        console = Console()
        root = Tree(f"[bold blue]Pipeline:[/bold blue] {query}")
        
        # SPL IR branch
        spl_branch = root.add("[bold yellow]SPL IR[/bold yellow]")
        for i, stage in enumerate(spl_ir.stages):
            stage_branch = spl_branch.add(f"[cyan]Stage {i+1}: {stage.command_name}[/cyan]")
            if hasattr(stage.command, 'expression') and stage.command.expression:
                stage_branch.add(f"Expression: [dim]{stage.command.expression}[/dim]")
            elif stage.command_name == "stats":
                if hasattr(stage.command, 'aggregations'):
                    agg_str = ", ".join([f"{a.function_name}({a.field.field_name if hasattr(a.field, 'field_name') else ''})" for a in stage.command.aggregations])
                    stage_branch.add(f"Aggregations: [dim]{agg_str}[/dim]")
                if hasattr(stage.command, 'group_by') and stage.command.group_by:
                    gb_str = ", ".join([gb.field_name for gb in stage.command.group_by if hasattr(gb, 'field_name')])
                    stage_branch.add(f"Group By: [dim]{gb_str}[/dim]")
            else:
                stage_branch.add(f"[dim]{stage.command}[/dim]")
        
        # Relational IR branch
        rel_branch = root.add("[bold magenta]Relational IR[/bold magenta]")
        select = relational_ir.select
        rel_branch.add(f"FROM: [green]{select.from_table}[/green]")
        if select.where:
            rel_branch.add(f"WHERE: [dim]{select.where.expression_text}[/dim]")
        if select.columns:
            rel_branch.add(f"SELECT: [dim]{', '.join(select.columns)}[/dim]")
        if select.group_by:
            rel_branch.add(f"GROUP BY: [dim]{', '.join(select.group_by)}[/dim]")
        if select.order_by:
            rel_branch.add(f"ORDER BY: [dim]{', '.join([f'{c} {d}' for c, d in select.order_by])}[/dim]")
        if select.limit:
            rel_branch.add(f"LIMIT: [dim]{select.limit}[/dim]")
        
        # SQL branch
        sql_branch = root.add("[bold green]Generated SQL[/bold green]")
        sql_branch.add(f"[green]{sql}[/green]")
        
        console.print(root)
        
    except Exception as e:
        click.echo(f"Error translating query: {e}", err=True)
        import traceback
        logger.debug(traceback.format_exc())
