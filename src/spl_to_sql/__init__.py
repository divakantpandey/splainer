"""spl-to-sql: Translate Splunk SPL queries into SQL.

Design Notes (Scaffold v0)
==========================
This scaffold implements a five-stage compiler pipeline:

  1. Parse (ANTLR4)  →  2. SPL IR  →  3. Relational IR  →  4. Codegen  →  5. Execute

Key architectural decisions and flags for future work:

- **Two IR stages vs one**: We use two IRs (spl_ir and relational_ir) rather than
  a single AST. spl_ir mirrors SPL semantics (piped commands, eval expressions),
  while relational_ir mirrors relational algebra (SELECT, JOIN, WHERE). This
  separation keeps the parser output faithful to the source language and defers
  SQL-specific concerns to the lowering step. If this proves overengineered for
  v0, collapsing into a single IR is straightforward — just merge relational_ir
  into spl_ir and remove the lowering step.

- **ir/transforms/**: Optimization passes (predicate pushdown, constant folding)
  are stubbed but flagged as OPTIONAL for v0. Cut this module if it adds
  complexity before the core pipeline works end-to-end.

- **codegen/dialects/**: Dialect-specific SQL rendering is stubbed for Postgres
  and Snowflake. This is premature if only one dialect is targeted initially, but
  the abstraction cost is near-zero for stubs. Cut if unwanted.

- **codegen/llm/**: The LLM fallback path is deliberately separated from
  deterministic codegen. Pure LLM-only translation is the thing to avoid — the
  architecture enforces that deterministic rules are tried first, and LLM is
  only invoked for constructs that rules don't cover. The stub structure doesn't
  *enforce* this boundary at runtime yet — that's a TODO for the pipeline
  orchestrator.

- **Missing modules NOT included (and why)**:
  - validation/: Pre-execution SQL syntax checking is premature. If codegen
    produces invalid SQL, execution/ catches it via the feedback loop.
  - schema/: Mapping Splunk index/sourcetype metadata to SQL table/column names
    requires real design decisions about metadata sources. Deferred. A TODO is
    noted in config.py.

- **Modules that might be premature but are kept**:
  - ir/transforms/: See above. Flagged as optional.
  - codegen/dialects/: See above. Trivial stub cost.

TODO: Wire stages together into a working pipeline in cli.py.
TODO: Add pipeline orchestrator module if stage composition gets complex.
"""

__version__ = "0.1.0"

__all__: list[str] = []
