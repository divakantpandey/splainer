# spl-to-sql

<!-- TODO: confirm license choice -->
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/TODO/spl-to-sql/actions/workflows/ci.yml/badge.svg)](https://github.com/TODO/spl-to-sql/actions/workflows/ci.yml)

Translate Splunk SPL (Search Processing Language) queries into SQL.

## Architecture Overview

`spl-to-sql` follows a multi-stage compiler pipeline:

1. **Parse** — SPL query string → ANTLR4 parse tree
2. **SPL IR** — Parse tree → SPL-shaped intermediate representation (mirrors SPL semantics)
3. **Relational IR** — SPL IR → relational-algebra-shaped IR (mirrors SQL semantics)
4. **Codegen** — Relational IR → SQL text (deterministic rules first, LLM fallback for uncovered constructs)
5. **Execute** — Run generated SQL against target DB, retry with error feedback on failure

<!-- TODO: Replace with actual architecture diagram -->
```
┌─────────┐    ┌─────────┐    ┌──────────────┐    ┌─────────┐    ┌─────────┐
│  Parse  │───▶│ SPL IR  │───▶│ Relational IR│───▶│ Codegen │───▶│ Execute │
│ (ANTLR) │    │         │    │              │    │(Rules+LLM)   │(Retry)  │
└─────────┘    └─────────┘    └──────────────┘    └─────────┘    └─────────┘
```

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/TODO/spl-to-sql.git
cd spl-to-sql
uv sync
```

To install with dev/test dependencies:

```bash
uv sync --extra dev --extra test
```

## Usage

> **Note:** This project is in early scaffolding stage. The CLI and pipeline are not yet implemented.

```bash
uv run spl-to-sql translate "search index=main | stats count by host"
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development setup instructions.

```bash
# Run tests
uv run pytest

# Lint & format
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Type check
uv run mypy src/
```

## License

<!-- TODO: confirm license choice -->
This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
