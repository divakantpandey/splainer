"""Rich console tree renderer for agent pipeline logs.

Converts structured ``AgentLog`` entries (serialized as dicts in
``PipelineState``) into a beautiful Rich Tree showing the status,
timing, routing decisions, and results of each pipeline node.

Output is sent to **both** stdout (for the user) and stderr
(for piping/debugging).
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from spl_to_sql.agent.logging import AgentLog

logger = logging.getLogger(__name__)

# Status → emoji mapping
_STATUS_ICONS: dict[str, str] = {
    "started": "▶",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "retry": "🔄",
    "skipped": "⏭️",
    "info": "ℹ️",
    "routing": "🔀",
}

# Status → Rich style
_STATUS_STYLES: dict[str, str] = {
    "started": "bold cyan",
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "retry": "bold yellow",
    "skipped": "dim",
    "info": "blue",
    "routing": "bold magenta",
}


def _format_duration(duration_ms: float | None) -> str:
    """Format duration for display.

    Args:
        duration_ms: Duration in milliseconds, or None.

    Returns:
        Formatted string like " (1.2ms)" or " (1.23s)" or "".
    """
    if duration_ms is None:
        return ""
    if duration_ms < 1000:
        return f" ({duration_ms:.1f}ms)"
    return f" ({duration_ms / 1000:.2f}s)"


def _add_log_node(parent: Tree, log: AgentLog) -> None:
    """Recursively add a log entry and its children to the tree."""
    icon = _STATUS_ICONS.get(log.status, "•")
    style = _STATUS_STYLES.get(log.status, "")
    duration_str = _format_duration(log.duration_ms)

    if style:
        label = f"[{style}]{icon} {log.detail}{duration_str}[/{style}]"
    else:
        label = f"{icon} {log.detail}{duration_str}"
        
    node = parent.add(label)

    for child in log.children:
        _add_log_node(node, child)


def _build_result_table(rows: list[dict[str, Any]], max_rows: int = 10) -> Table:
    """Build a Rich Table from query result rows.

    Args:
        rows: List of row dicts from SQL execution.
        max_rows: Maximum rows to display.

    Returns:
        A Rich Table for display.
    """
    if not rows:
        return Table(title="(no results)")

    table = Table(show_header=True, header_style="bold")

    # Add columns from first row's keys
    for col_name in rows[0]:
        table.add_column(str(col_name))

    # Add rows (limited)
    for row in rows[:max_rows]:
        table.add_row(*(str(v) for v in row.values()))

    if len(rows) > max_rows:
        table.add_row(*["..." for _ in rows[0]])

    return table


def render_agent_tree(
    agent_logs: list[dict[str, Any]],
    execution_result: list[dict[str, Any]] | None = None,
    generated_sql: str = "",
) -> None:
    """Render all agent logs as a unified Rich console tree.

    Output goes to **both** stdout and stderr as requested.

    Args:
        agent_logs: List of serialized AgentLog dicts from PipelineState.
        execution_result: Optional query results to display.
        generated_sql: The final generated SQL to display.
    """
    # Build the tree
    root = Tree("[bold blue]🤖 spl-to-sql Agent Pipeline[/bold blue]")

    for log_dict in agent_logs:
        log = AgentLog.from_dict(log_dict)
        icon = _STATUS_ICONS.get(log.status, "•")
        style = _STATUS_STYLES.get(log.status, "")
        duration_str = _format_duration(log.duration_ms)

        if style:
            header = f"[{style}]{icon} {log.agent_name}{duration_str}[/{style}]"
        else:
            header = f"{icon} {log.agent_name}{duration_str}"
            
        agent_node = root.add(header)

        # Add detail as first child
        if log.detail:
            detail_style = _STATUS_STYLES.get(log.status, "dim")
            agent_node.add(f"[{detail_style}]{log.detail}[/{detail_style}]")

        # Add nested children
        for child in log.children:
            _add_log_node(agent_node, child)

    # Add SQL output if present
    if generated_sql:
        sql_node = root.add("[bold green]📝 Generated SQL[/bold green]")
        sql_node.add(f"[green]{generated_sql}[/green]")

    # Add execution results if present
    if execution_result is not None:
        result_node = root.add(
            f"[bold cyan]📊 Results ({len(execution_result)} rows)[/bold cyan]"
        )
        if execution_result:
            table = _build_result_table(execution_result)
            result_node.add(table)

    # Output to stdout
    stdout_console = Console(file=sys.stdout)
    stdout_console.print(root)

