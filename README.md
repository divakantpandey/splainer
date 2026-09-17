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
