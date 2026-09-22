"""Prompt templates for LLM-assisted SQL generation.

Contains string constants and template functions for constructing
prompts sent to the LLM for SQL generation. No business logic —
just prompt formatting.

TODO: Replace placeholder templates with production prompts.
TODO: Add few-shot examples.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Placeholder prompt templates — replace with production content.

SYSTEM_PROMPT = """You are a SQL generation assistant. Given a description of a \
query's intent and the target SQL dialect, generate a valid SQL query.

Rules:
- Output ONLY the SQL query, no explanations.
- Use the specified dialect's syntax.
- Use proper identifier quoting.
"""

TRANSLATION_PROMPT_TEMPLATE = """Translate the following SPL query intent into \
{dialect} SQL:

SPL Intent:
{spl_description}

Relational IR (partial):
{relational_ir_json}

Target dialect: {dialect}

Generate the complete SQL query:
"""

ERROR_CORRECTION_PROMPT_TEMPLATE = """The following SQL query failed to execute. \
Please correct it.

Original SQL:
{sql}

Error message:
{error_message}

Target dialect: {dialect}

Generate the corrected SQL query:
"""


def format_translation_prompt(
    spl_description: str,
    relational_ir_json: str,
    dialect: str,
) -> str:
    """Format a translation prompt for the LLM."""
    return f"""You are a SQL generation assistant. Given an SPL query and partial relational structure, generate a valid SQL query in {dialect}.

Rules:
- Output ONLY the SQL query, no explanations.
- Use {dialect} syntax and proper identifier quoting.
- Ensure the semantics of the SPL query are perfectly translated.

Original SPL query:
{spl_description}

Partial Relational Structure:
{relational_ir_json}

SQL:"""

def format_error_correction_prompt(
    sql: str,
    error_message: str,
    dialect: str,
) -> str:
    """Format an error correction prompt for the LLM."""
    return f"""The following {dialect} SQL query failed to execute. Please correct it.

Original SQL:
```sql
{sql}
```

Error message:
{error_message}

Target dialect: {dialect}

Rules:
- Output ONLY the corrected SQL query without any markdown formatting or explanations.

Corrected SQL:"""
