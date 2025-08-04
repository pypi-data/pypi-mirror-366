# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a GitOps tool for managing multiple applications across Kubernetes clusters. It consists of two main components:

1. **GitOps CLI** (`gitops/`) - Command-line tool for managing app deployments, built using the `invoke` framework
2. **GitOps Server** (`gitops_server/`) - FastAPI-based webhook server that handles deployment automation

## Development Commands

### Setup
```bash
# Install dependencies using uv
uv sync

# Install the CLI tool for development
uv tool install -e .
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_core.py

# Run with coverage
uv run pytest --cov=gitops --cov=gitops_server
```

### Linting and Formatting
```bash
# Format code with ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable linting issues
uv run ruff check --fix .

# Type checking with mypy
uv run mypy gitops/ gitops_server/
```

### Running the CLI
```bash
# Run gitops commands during development
uv run python -m gitops.main --help

# Or if installed globally
gitops --help
```

### Running the Server
```bash
# Run the gitops server locally
uv run uvicorn gitops_server.main:app --reload
```

## Architecture

### CLI Component (`gitops/`)
- **main.py**: Entry point using invoke's Program framework
- **core.py**: Main CLI commands (bump, summary, etc.)
- **shorthands.py**: Shorthand command aliases
- **settings.py**: Configuration management
- **utils/**: Helper modules for apps, images, kubernetes operations, CLI formatting, etc.

### Server Component (`gitops_server/`)
- **main.py**: FastAPI application entry point with webhook endpoint
- **app.py**: FastAPI app configuration
- **workers/**: Background workers for deployment operations
- **workers/deploy.py**: Main deployment loop code
- **workers/worker.py**: Entry point for recieving webhook
- **utils/**: Git, GitHub, and Slack integration utilities

### Key Patterns
- Uses `invoke` framework for CLI task definitions
- Async operations with progress bars for CLI commands
- FastAPI with webhook validation for server component
- Kubernetes operations through the `kubernetes_asyncio` library
- Git operations for managing cluster repository state

## Configuration

- **Environment Variables**: Set `GITOPS_APPS_DIRECTORY` to specify the apps directory location
- **Secrets**: Server configuration goes in `secrets.env` (see `secrets.example.env`)
- **Ruff Config**: Located in `ruff.toml` with specific rules for this codebase
- **Dependencies**: Managed through `pyproject.toml` with separate server optional dependencies

## Testing Structure

- Tests are in the `tests/` directory
- Uses pytest with async support (`pytest-asyncio`)
- Sample data and webhook fixtures in `sample_data.py` and `webhook_sample_data.py`
- Conftest provides shared test configuration