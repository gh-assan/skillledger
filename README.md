# SkillLedger

On-chain verifiable capability marketplace for autonomous agents.

## Architecture

Multi-layered Python application:

| Layer | Responsibility |
|-------|---------------|
| controllers/ | HTTP entry points — parse input, delegate to services |
| services/ | Business logic, orchestration |
| repositories/ | Data access (DB, cache, blockchain) |
| models/ | Domain schemas and types |
| middleware/ | Auth, error handling, logging |
| config/ | Configuration loading (env, files) |

## Quick Start

```bash
pip install -r requirements.txt
python -m skillledger.app
```

## Testing

```bash
pytest --cov=skillledger --cov-report=term-missing
```

## Documentation

API docs available at `/docs` when running.
OpenAPI spec at `openapi.yaml`.

