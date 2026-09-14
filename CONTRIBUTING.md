# Contributing to spl-to-sql

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Prerequisites**: Python 3.11+ and [uv](https://docs.astral.sh/uv/)

2. **Clone and install**:
   ```bash
   git clone https://github.com/TODO/spl-to-sql.git
   cd spl-to-sql
   uv sync --extra dev --extra test
   ```

3. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=spl_to_sql --cov-report=html

# Run a specific test file
uv run pytest tests/parser/test_listener.py
```

Integration tests (requiring live LLM or DB connections) are excluded from the default run. To include them:

```bash
uv run pytest -m integration
```

## Code Style

This project uses:
- **ruff** for linting and formatting
- **mypy** (strict mode) for type checking
- **Google-style** docstrings

Pre-commit hooks enforce these automatically. To run manually:

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/
```

## Pull Request Process

1. Fork the repository and create a feature branch from `main`.
2. Write tests for any new functionality.
3. Ensure all checks pass: `ruff check`, `ruff format --check`, `mypy`, `pytest`.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a pull request with a clear description of changes.

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) where practical:
- `feat: add new SPL command parser`
- `fix: correct SQL quoting for identifiers`
- `docs: update architecture diagram`
- `test: add codegen dialect tests`

## Questions?

Open an issue for discussion before starting large changes.
