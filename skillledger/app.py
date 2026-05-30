"""Application factory — wires config, DB, services, controllers, and middleware."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from flask import Flask
from flask_cors import CORS

from skillledger.config import Config
from skillledger.controllers.accounts import accounts_bp, _init as init_accounts
from skillledger.controllers.executions import executions_bp, _init as init_executions
from skillledger.controllers.health import health_bp
from skillledger.controllers.skills import skills_bp, _init as init_skills
from skillledger.middleware import register_error_handlers, register_request_logging
from skillledger.repositories import (
    AccountRepository,
    DatabaseManager,
    ExecutionRepository,
    SkillRepository,
)
from skillledger.services import AccountService, ExecutionService, SkillService

logger = logging.getLogger("skillledger")


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    balance INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    owner_account_id TEXT NOT NULL,
    price_per_call INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    FOREIGN KEY (owner_account_id) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS executions (
    id TEXT PRIMARY KEY,
    skill_id TEXT NOT NULL,
    requester_account_id TEXT NOT NULL,
    input_params TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    result TEXT,
    cost INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    verified_at TEXT,
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    FOREIGN KEY (requester_account_id) REFERENCES accounts(id)
);
"""


def init_db(db_path: str) -> None:
    """Create the SQLite database file and ensure tables exist."""
    parent = Path(db_path).parent
    parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.close()
    logger.info("Database initialised at %s", db_path)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app(config: Config | None = None) -> Flask:
    """Build and return a configured Flask application instance."""
    if config is None:
        config = Config.from_env()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.secret_key
    CORS(app)

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Database
    db_path = config.database_path
    init_db(db_path)
    db = DatabaseManager(db_path)

    # Repositories
    skill_repo = SkillRepository(db)
    execution_repo = ExecutionRepository(db)
    account_repo = AccountRepository(db)

    # Services
    skill_service = SkillService(skill_repo, account_repo)
    execution_service = ExecutionService(execution_repo, skill_repo, account_repo)
    account_service = AccountService(account_repo)

    # Controllers (inject services)
    init_skills(skill_service, execution_service)
    init_executions(execution_service)
    init_accounts(account_service)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(executions_bp)
    app.register_blueprint(accounts_bp)

    # Middleware
    register_error_handlers(app)
    register_request_logging(app)

    return app


# ---------------------------------------------------------------------------
# Entry point (python -m skillledger.app)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cfg = Config.from_env()
    application = create_app(cfg)
    logger.info(
        "Starting SkillLedger on %s:%s (debug=%s)",
        cfg.host,
        cfg.port,
        cfg.debug,
    )
    application.run(host=cfg.host, port=cfg.port, debug=cfg.debug)
