# spl-to-sql

<!-- TODO: confirm license choice -->
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/TODO/spl-to-sql/actions/workflows/ci.yml/badge.svg)](https://github.com/TODO/spl-to-sql/actions/workflows/ci.yml)

Translate Splunk SPL (Search Processing Language) queries into SQL.

## Usage

Translate queries using the CLI interface. By default, it runs through the **LangGraph Agent Pipeline** and prints out a rich intermediate transformation tree showing routing decisions and execution timings:

```bash
uv run spl-to-sql translate 'search index=main (status=200 OR status IN (301, 302)) NOT error | stats sum(bytes) AS total_bytes by host'
```

**Output:**

```
🤖 spl-to-sql Agent Pipeline
├── ✅ parse_node (1.9ms)
│   └── Successfully parsed SPL query
├── ✅ ir_build_node (0.2ms)
│   └── Built SPL IR with 2 stages: search, stats
├── ✅ lowering_node (0.0ms)
│   └── Successfully lowered to Relational IR
├── ✅ codegen_deterministic_node (0.0ms)
│   └── Successfully generated SQL
└── 📝 Generated SQL
    └── SELECT SUM(bytes) AS total_bytes, host
        FROM main
        WHERE (((status = 200) OR status IN (301, 302)) AND NOT ((_raw = 'error')))
        GROUP BY host;
```

### Automatic Validation & LLM Feedback Loop
Pass the `--execute` flag to automatically run the generated SQL against your target database. If the database rejects the query (e.g. invalid syntax or schema errors), the agent captures the remote error and loops back to the LLM to automatically fix it!

```bash
uv run spl-to-sql translate "search index=app | transaction request_id | where duration > 5" --dialect mysql --execute
```

**Feedback Loop Output:**
```text
🤖 spl-to-sql Agent Pipeline
├── ✅ parse_node (2.0ms)
├── ✅ ir_build_node (0.2ms)
├── ⚠️ lowering_node (0.0ms)
│   └── Lowering unsupported: UnknownCommand
├── ✅ codegen_llm_node (4.0s)
│   └── Successfully generated SQL with LLM
├── ❌ validate_node (81.0ms)
│   └── Execution failed: (1054, "Unknown column 'duration' in 'field list'")
├── ✅ validate_fix_node (3.4s)
│   └── LLM corrected SQL query based on DB schema error
├── ✅ validate_node (30.0ms)
│   └── Query execution successful
├── 📝 Generated SQL
│   └── SELECT `request_id`, TIMESTAMPDIFF(SECOND, MIN(`timestamp`), MAX(`timestamp`)) AS duration
│       FROM `app`
│       GROUP BY `request_id` HAVING duration > 5;
└── 📊 Results (1 rows)
    └── ┏━━━━━━━━━━━━┳━━━━━━━━━━┓
        ┃ request_id ┃ duration ┃
        ┡━━━━━━━━━━━━╇━━━━━━━━━━┩
        │ REQ-1001   │       10 │
        └────────────┴──────────┘
```

### Visualizing the Architecture
Pass the `--draw-graph` flag to view the state machine's decision flow directly in your terminal:

```bash
uv run spl-to-sql translate "search index=main" --draw-graph
```

**Graph Output:**
```text
🤖 Agent Pipeline Architecture:
                                                             +-----------+                                                    
                                                             | __start__ |                                                    
                                                             +-----------+                                                    
                                                                   *                                                          
                                                               +-------+....                                                  
                                                              .| parse |... .........                                         
                                                           ... +-------+   ......    .........                                
                                       +----------+                                                ....                 ..... 
                                       | ir_build |                                                   .                     . 
                                       +----------+                                                   .                     . 
                                             *                                                        .                     . 
                                       +----------+                                                   .                     . 
                                       | lowering |..                                                 .                     . 
                                       +----------+  ......                                           .                     . 
                  +-----------------------+                                  ...                      .                     . 
                  | codegen_deterministic |.                                   .                      .                     . 
                  +-----------------------+ ........                           .                      .                     . 
                    .                                ..                 +-------------+               .                     . 
                    .                                 .            .....| codegen_llm |               .                     . 
                    .                                 .............     +-------------+               .                     . 
              +----------+                            .                        .                      .                     . 
              | validate |                            .                        .                       ..                 ..  
              +----------+                            .                        .                         ..             ..    
             ...         ...                          .                        .                           ..         ..      
+--------------+                ...                   ..                       .                          +-----------+       
| validate_fix |......             ......               ..                  ...                        ...| parse_fix |       
+--------------+      ...........        ......           ..               .                    .......   +-----------+       
                                 ..........    ......       ..          ...            .........                              
                                                      ........  ..   ..    .....                                              
                                                           +---------------+                                                  
                                                           | render_output |                                                  
                                                           +---------------+                                                  
                                                                   *                                                          
                                                              +---------+                                                     
                                                              | __end__ |                                                     
                                                              +---------+  
```

### CLI Flags
* `--execute` / `--no-execute`: Validate the generated SQL against the actual database.
* `--dialect [postgres|snowflake|mysql]`: Target SQL dialect (default: postgres).
* `--draw-graph`: Render the ASCII architecture diagram of the LangGraph agents.
* `--no-show-tree`: Skip the visual tree and print only the raw SQL (useful for piping `> output.sql`).

## Minimum Viable Product (MVP) Features

`spl-to-sql` now uses a **sophisticated LangGraph orchestration pipeline** for resilient end-to-end translation.

* **Agentic Orchestration**: Uses LangGraph to route queries dynamically between deterministic compilers and LLM fallback paths.
* **Auto-Recovery Loop**: Executes queries remotely and automatically uses LLMs to fix schema or syntax errors based on live DB feedback.
* **ANTLR4 Powered Parser**: Fully parses basic commands like `search` and `stats`, with automatic syntax-correction LLM loops on parsing failure.
* **Advanced Expressions**: Accurately constructs nested expression trees for conditions incorporating implicit `AND`, explicit `OR`, `NOT`, and `IN` operators.
* **Tier 1 SPL Commands Supported**: Deterministically translates `search`, `where`, `eval`, `stats`, `sort`, `head`, `tail`, `rename`, `table`, `fields`, `dedup`, `top`, and `rare`.
* **Rich AST Visualization**: Prints an integrated, terminal-friendly tree view showing agent routing and transformation steps.
* **Dialect Support**: Configurable generation for `postgres`, `snowflake`, and `mysql`.

### LLM Fallback Codegen (Hybrid Compilation)

When the deterministic translation engine encounters an SPL command it cannot safely lower to Relational IR (e.g. `transaction`, `append`), it gracefully fails over to a Language Model to semantically bridge the gap.

**Configuration Auto-Loading**
Configuration (like database strings and API keys) is automatically loaded from your `infra/.env` file. 

**Using Standard Providers (OpenAI, etc.)**
Add to `infra/.env`:
```bash
SPL_TO_SQL_LLM__API_KEY="sk-..."
SPL_TO_SQL_LLM__MODEL_NAME="gpt-4o"
```

**Using Local Models (Ollama, vLLM, LM Studio)**
Local models offer full privacy and zero costs. Just provide your base URL in `infra/.env` (no API key required!):
```bash
SPL_TO_SQL_LLM__BASE_URL="http://localhost:11434/v1"
SPL_TO_SQL_LLM__MODEL_NAME="mistral"
```

## Architecture Overview

`spl-to-sql` follows a multi-stage LangGraph agent pipeline:

1. **Parse** — SPL query string → ANTLR4 parse tree (retries with LLM on syntax error)
2. **SPL IR** — Parse tree → SPL-shaped intermediate representation
3. **Relational IR** — SPL IR → relational-algebra-shaped IR
4. **Codegen** — Relational IR → SQL text (deterministic rules first, routes to LLM on unsupported commands)
5. **Validate & Fix** — Runs SQL against target DB. If it fails, routes remote error + SQL to LLM for auto-correction up to 3 times.

*(Run `spl-to-sql translate "..." --draw-graph` to see the live ASCII representation of this state machine!)*

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
