"""SQL code generation module — Stage 4 of the spl-to-sql pipeline.

Contains two code generation paths:
- deterministic: Rule-based Relational IR → SQL for the coverable subset.
- llm: Constrained-generation fallback for constructs rules don't cover.

The architecture enforces that deterministic codegen is tried first.
LLM codegen is only invoked for constructs that deterministic rules
can't handle. Pure LLM-only translation is explicitly avoided.

TODO: Implement pipeline orchestration that enforces deterministic-first.
"""
