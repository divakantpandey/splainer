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
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose internal logging.")
def main(verbose: bool) -> None:
    """spl-to-sql: Translate Splunk SPL queries into SQL."""
    # Load config and configure logging early
    config = SplToSqlConfig.from_env()
    log_level = "INFO" if verbose else "WARNING"
    configure_logging(log_level)


@main.command()
@click.argument("query")
@click.option(
    "--dialect",
    type=click.Choice(["postgres", "snowflake", "mysql"]),
    default="postgres",
    help="Target SQL dialect.",
)
@click.option(
    "--execute/--no-execute",
    default=False,
    help="Execute the generated SQL against the configured database.",
)
@click.option(
    "--agent/--no-agent",
    default=True,
    help="Use LangGraph agent-based orchestration (default: enabled).",
)
@click.option(
    "--show-tree/--no-show-tree",
    default=True,
    help="Show the intermediate translation tree (AST -> Relational IR -> SQL).",
)
@click.option(
    "--draw-graph",
    is_flag=True,
    help="Draw the ASCII architecture diagram of the LangGraph agents and exit.",
)
def translate(query: str, dialect: str, execute: bool, agent: bool, show_tree: bool, draw_graph: bool) -> None:
    """Translate an SPL query into SQL.

    When --agent is enabled (default), uses LangGraph-based agent
    orchestration with automatic routing, error correction, remote
    SQL validation, and rich console tree logging.

    Args:
        query: The SPL query string to translate.
        dialect: Target SQL dialect (default: postgres).
        execute: Whether to execute the generated SQL.
        agent: Whether to use agent-based orchestration.
        show_tree: Whether to show the translation tree.
        draw_graph: Print the ASCII graph architecture and exit.
    """
    if draw_graph:
        from spl_to_sql.agent.graph import build_pipeline_graph
        from spl_to_sql.config import SplToSqlConfig
        
        config = SplToSqlConfig.from_env()
        graph = build_pipeline_graph(config)
        click.echo("🤖 Agent Pipeline Architecture:")
        graph.get_graph().print_ascii()
        click.echo("\n" + "─" * 40 + "\n")

    if agent:
        _translate_with_agent(query, dialect, execute, show_tree)
    else:
        _translate_legacy(query, dialect, execute, show_tree)


def _translate_with_agent(query: str, dialect: str, execute: bool, show_tree: bool) -> None:
    """Run translation via the LangGraph agent pipeline."""
    from spl_to_sql.agent import run_pipeline
    from spl_to_sql.config import SplToSqlConfig

    try:
        # Override console_tree_enabled based on --show-tree flag
        config = SplToSqlConfig.from_env()
        config.agent.console_tree_enabled = show_tree
        
        result = run_pipeline(query=query, dialect=dialect, execute=execute, config_override=config)

        if result.error and not result.sql:
            click.echo(f"Pipeline failed: {result.error}", err=True)
            raise SystemExit(1)

        # If we didn't show the tree, just print the raw SQL to stdout
        if not show_tree and result.sql:
            click.echo(result.sql)
        elif result.sql:
            logger.debug("Generated SQL:\n%s", result.sql)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        logger.debug(traceback.format_exc())
        raise SystemExit(1)


def _translate_legacy(
    query: str, dialect: str, execute: bool, show_tree: bool
) -> None:
    """Run translation via the original inline pipeline (backward compat)."""
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
        
        # 3 & 4. Lowering and Codegen
        from spl_to_sql.exceptions import CodegenError
        sql = ""
        try:
            relational_ir = lower_to_relational(spl_ir)
            sql = generate_sql(relational_ir)
        except CodegenError as e:
            click.echo(f"Deterministic translation failed ({e}), falling back to LLM...")
            from spl_to_sql.codegen.llm.client import LLMClient
            from spl_to_sql.codegen.llm.prompts import format_translation_prompt
            from spl_to_sql.config import SplToSqlConfig
            
            config = SplToSqlConfig.from_env()
            llm_client = LLMClient(config=config.llm)
            
            ir_json = spl_ir.model_dump_json(indent=2)
            
            prompt = format_translation_prompt(
                spl_description=query,
                relational_ir_json=ir_json,
                dialect=dialect,
            )
            sql = llm_client.generate_sql(prompt)
            
            from spl_to_sql.ir.relational_ir.nodes import RelationalQuery, SelectNode
            relational_ir = RelationalQuery(select=SelectNode(columns=["*"], from_table="unknown_due_to_llm_fallback"))
        
        def _build_spl_tree(node, command):
            if hasattr(command, 'expression') and command.expression:
                node.add(f"Expression: [dim]{command.expression}[/dim]")
            elif getattr(command, 'command_name', None) == "stats" or command.__class__.__name__.lower() == "stats":
                if hasattr(command, 'aggregations'):
                    agg_str = ", ".join([f"{a.function_name}({a.field.field_name if hasattr(a.field, 'field_name') else ''})" for a in command.aggregations])
                    node.add(f"Aggregations: [dim]{agg_str}[/dim]")
                if hasattr(command, 'group_by') and command.group_by:
                    gb_str = ", ".join([gb.field_name for gb in command.group_by if hasattr(gb, 'field_name')])
                    node.add(f"Group By: [dim]{gb_str}[/dim]")
            else:
                node.add(f"[dim]{command}[/dim]")
        
        if show_tree:
            from rich.console import Console
            from rich.tree import Tree
            
            console = Console()
            root = Tree(f"[bold blue]Pipeline:[/bold blue] {query}")
            
            spl_branch = root.add("[bold yellow]SPL IR[/bold yellow]")
            for i, stage in enumerate(spl_ir.stages, 1):
                stage_branch = spl_branch.add(f"[cyan]Stage {i}: {stage.command_name}[/cyan]")
                _build_spl_tree(stage_branch, stage.command)
                
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
                rel_branch.add(f"ORDER BY: [dim]{', '.join([f'{c} {d.value}' for c, d in select.order_by])}[/dim]")
            if select.limit:
                rel_branch.add(f"LIMIT: [dim]{select.limit}[/dim]")
                
            sql_branch = root.add("[bold green]Generated SQL[/bold green]")
            sql_branch.add(f"[green]{sql}[/green]")
            
            console.print(root)
        else:
            click.echo(sql)
        
    except Exception as e:
        click.echo(f"Error translating query: {e}", err=True)
        import traceback
        logger.debug(traceback.format_exc())
