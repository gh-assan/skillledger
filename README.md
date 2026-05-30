# SkillLedger

A Rails API application for skill execution, verification, and account management.

## Stack

- **Rails 8.1 API mode** (no views, no sessions)
- **SQLite** (development/test), **PostgreSQL** (production)
- **RSpec** + **FactoryBot** for testing
- **SimpleCov** for code coverage
- **rswag** for OpenAPI/Swagger docs
- **RuboCop** for linting

## Architecture

| Layer | Location |
|-------|----------|
| Controllers | `app/controllers/api/v1/` (thin, no business logic) |
| Services | `app/services/` (all business rules) |
| Models | `app/models/` (Active Record) |
| OpenAPI | `swagger/v1/swagger.yaml` (auto-generated) |

## API Endpoints

### Skills
- `POST /api/v1/skills` - Create a skill
- `GET /api/v1/skills` - List skills
- `GET /api/v1/skills/:id` - Get skill details
- `POST /api/v1/skills/:id/execute` - Execute a skill

### Executions
- `GET /api/v1/executions` - List executions
- `GET /api/v1/executions/:id` - Get execution details
- `POST /api/v1/executions/:id/verify` - Verify an execution

### Accounts
- `POST /api/v1/accounts` - Create an account
- `GET /api/v1/accounts/:id/balance` - Get account balance

### Health
- `GET /api/v1/health` - Health check

## Setup

```bash
bundle install
rails db:create db:migrate
rails server
```

## Testing

```bash
bundle exec rspec        # Run all tests
bundle exec rubocop      # Lint check
bundle exec brakeman     # Security audit
```

## OpenAPI Docs

After running the swaggerize task, docs are available at `/api-docs` when the server is running.

```bash
bundle exec rails rswag:specs:swaggerize
```

## CI

GitHub Actions CI runs on push/PR to `main`:
- RSpec tests
- RuboCop linting
- Brakeman security scan
