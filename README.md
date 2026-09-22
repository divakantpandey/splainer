# spl-to-sql

<!-- TODO: confirm license choice -->
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/TODO/spl-to-sql/actions/workflows/ci.yml/badge.svg)](https://github.com/TODO/spl-to-sql/actions/workflows/ci.yml)

Translate Splunk SPL (Search Processing Language) queries into SQL.

## Usage

Translate queries using the CLI interface. By default, it prints out the rich intermediate transformation tree:

```bash
uv run spl-to-sql translate 'search index=main (status=200 OR status IN (301, 302)) NOT error | stats sum(bytes) AS total_bytes by host'
```

**Output:**

```
Translating query: search index=main (status=200 OR status IN (301, 302)) NOT error | stats sum(bytes) AS total_bytes by host
Pipeline: search index=main (status=200 OR status IN (301, 302)) NOT error | stats sum(bytes) AS total_bytes by host
├── SPL IR
│   ├── Stage 1: search
│   │   └── Expression: source_text='' left=BinaryOp(source_text='', 
│   │       left=BinaryOp(source_text='', left=FieldRef(source_text='', 
│   │       field_name='index'), op='=', right=Literal(source_text='', 
│   │       value='main')), op='AND', right=BinaryOp(source_text='', 
│   │       left=BinaryOp(source_text='', left=FieldRef(source_text='', 
│   │       field_name='status'), op='=', right=Literal(source_text='', 
│   │       value=200)), op='OR', right=InExpr(source_text='', 
│   │       field=FieldRef(source_text='', field_name='status'), 
│   │       values=[Literal(source_text='', value=301), Literal(source_text='', 
│   │       value=302)]))) op='AND' right=UnaryOp(source_text='', op='NOT', 
│   │       expr=BinaryOp(source_text='', left=FieldRef(source_text='', 
│   │       field_name='_raw'), op='=', right=Literal(source_text='', 
│   │       value='error')))
│   └── Stage 2: stats
│       ├── Aggregations: sum(bytes)
│       └── Group By: host
├── Relational IR
│   ├── FROM: main
│   ├── WHERE: (((index = 'main') AND ((status = 200) OR status IN (301, 302))) 
│   │   AND NOT ((_raw = 'error')))
│   ├── SELECT: SUM(bytes) AS total_bytes, host
│   └── GROUP BY: host
└── Generated SQL
    └── SELECT SUM(bytes) AS total_bytes, host
        FROM main
        WHERE (((index = 'main') AND ((status = 200) OR status IN (301, 302))) 
        AND NOT ((_raw = 'error')))
        GROUP BY host;
```

To just print the generated SQL without the tree, you can use `--no-show-tree`:
```bash
uv run spl-to-sql translate "search index=main | stats count by sourcetype" --no-show-tree
```

## Minimum Viable Product (MVP) Features

`spl-to-sql` now supports a foundational end-to-end pipeline covering core SPL semantics.

* **ANTLR4 Powered Parser**: Fully parses basic commands like `search` and `stats`.
* **Advanced Expressions**: Accurately constructs nested expression trees for conditions incorporating implicit `AND`, explicit `OR`, `NOT`, and `IN` operators.
* **Aggregations**: Handles grouping (`GROUP BY`) and multiple aggregations natively mapped to their relational counterparts (e.g., `stats count`, `sum(bytes)`).
* **Tier 1 SPL Commands Supported**: Deterministically translates `search`, `where`, `eval`, `stats`, `sort`, `head`, `tail`, `rename`, `table`, `fields`, `dedup`, `top`, and `rare`.
* **Rich AST Visualization**: Prints an integrated, terminal-friendly tree view showing exactly how your SPL query transforms at each pipeline stage.
* **Deterministic SQL Codegen**: Emits standard SQL deterministically for recognized commands.
* **LLM Semantic Fallback**: Automatically falls back to an AI compiler (via standard OpenAI models or local LLMs) when encountering unhandled/complex SPL commands.

### LLM Fallback Codegen (Hybrid Compilation)

When the deterministic translation engine encounters an SPL command it cannot safely lower to Relational IR (e.g. `transaction`, `append`), it gracefully fails over to a Language Model to semantically bridge the gap.

**Using Standard Providers (OpenAI, etc.)**
Set your API key as an environment variable:
```bash
export SPL_TO_SQL_LLM__API_KEY="sk-..."
export SPL_TO_SQL_LLM__MODEL_NAME="gpt-4o"
```

**Using Local Models (Ollama, vLLM, LM Studio)**
Local models offer full privacy and zero costs. You can point the client to any OpenAI-compatible local server. An API key is not required when a custom base URL is specified:

```bash
# E.g. using a local Ollama server running mistral
export SPL_TO_SQL_LLM__BASE_URL="http://localhost:11434/v1"
export SPL_TO_SQL_LLM__MODEL_NAME="mistral"
```

Run an unsupported command and watch it seamlessly fall back:
```bash
uv run spl-to-sql translate 'search index=main | transaction host'
```

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

## Test Infrastructure (Splunk & MySQL)

The repository provides local test infrastructure running **Splunk Enterprise** and **MySQL 8.0** via Docker Compose (compatible with Rancher Desktop / Docker Desktop).

### Starting the Infrastructure

```bash
docker compose -f infra/docker-compose.yml up -d
```

- **Automated Alembic Migrations**: The `spl-migrator` service automatically detects when MySQL is healthy and applies all pending Alembic schema migrations (`alembic upgrade head`) and seeds test datasets (`web_logs`, `auth_events`). No manual SQL scripts are required.
- **Splunk Enterprise**: Web UI available at [http://localhost:8000](http://localhost:8000) and REST API at `https://localhost:8089` (`admin` / `SplunkTestPassword123!`).
- **MySQL**: Accessible at `localhost:3306` (database `testdb`, credentials `spluser` / `splpassword`).

### Database Migrations via Alembic

Run migrations directly from your host environment:

```bash
# Apply migrations
uv run alembic upgrade head

# Rollback migrations
uv run alembic downgrade -1

# Check current revision
uv run alembic current
```

See [infra/README.md](infra/README.md) for full configuration details, environment variables, and teardown instructions.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development setup instructions.

```bash
# Run tests
uv run pytest

# Lint & format
uv run ruff check src/ tests/ migrations/
uv run ruff format --check src/ tests/ migrations/

# Type check
uv run mypy src/
```

## License

<!-- TODO: confirm license choice -->
This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
