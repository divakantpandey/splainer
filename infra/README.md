# Test Infrastructure: Splunk & MySQL

This directory contains the Docker Compose setup for local testing of `spl-to-sql`, hosting **Splunk Enterprise** and **MySQL** with **automated Alembic schema migrations**.

## Prerequisites: Rancher Desktop

1. Ensure Rancher Desktop is running (`/Applications/Rancher Desktop.app`).
2. **Recommended Settings** in Rancher Desktop (*Preferences -> Virtual Machine*):
   - **Memory**: At least 4 GB (6 GB recommended for Splunk).
   - **CPUs**: 2–4 cores.
   - **Emulation**: On Apple Silicon (M1/M2/M3/M4), ensure Rosetta support is enabled under *Virtual Machine -> Emulation* for fast `amd64` execution of Splunk.
   - **Container Engine**: `dockerd (moby)`.

## Starting the Infrastructure

```bash
# From the project root:
docker compose -f infra/docker-compose.yml up -d
```

When you start the stack:
1. `mysql` and `splunk` containers start.
2. Once MySQL passes its health check, the `migrator` container runs `alembic upgrade head` automatically to create the schemas (`web_logs`, `auth_events`) and insert the test fixtures. No manual SQL scripts are executed.

To view logs:
```bash
docker compose -f infra/docker-compose.yml logs -f
```

To stop the services:
```bash
docker compose -f infra/docker-compose.yml down
```

To reset the database and clean volumes:
```bash
docker compose -f infra/docker-compose.yml down -v
```

## Running Migrations Locally (Without Docker)

You can also apply or rollback migrations directly from your local Python environment:

```bash
# Apply migrations against local or remote DB
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Or programmatically in Python code / tests:
from spl_to_sql.db import run_migrations
run_migrations("mysql+pymysql://spluser:splpassword@localhost:3306/testdb")
```

## Service Details & Credentials

| Service | Port | Default Credentials | Description |
| :--- | :--- | :--- | :--- |
| **Splunk Web** | `http://localhost:8000` | User: `admin`<br>Pass: `SplunkTestPassword123!` | Splunk Web UI |
| **Splunk REST API** | `https://localhost:8089` | User: `admin`<br>Pass: `SplunkTestPassword123!` | Management & Search API |
| **Splunk HEC** | `http://localhost:8088` | Token: `00000000-0000-0000-0000-000000000000` | HTTP Event Collector |
| **MySQL 8.0** | `localhost:3306` | Root Pass: `rootpassword`<br>DB: `testdb`<br>User: `spluser`<br>Pass: `splpassword` | Target SQL database managed by Alembic |
| **Alembic Migrator** | One-shot | N/A | Auto-runs `alembic upgrade head` upon MySQL healthiness |
