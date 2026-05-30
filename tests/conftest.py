"""Shared pytest fixtures for unit and functional tests."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from skillledger.app import create_app, init_db
from skillledger.config import Config
from skillledger.models import Account, Skill
from skillledger.repositories import (
    AccountRepository,
    DatabaseManager,
    ExecutionRepository,
    SkillRepository,
)


@pytest.fixture
def db_path() -> Generator[str, None, None]:
    """Yield a temporary SQLite database path for testing."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = tmp.name
    tmp.close()
    init_db(path)
    yield path
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def db_manager(db_path: str) -> DatabaseManager:
    """Yield a DatabaseManager bound to the temporary db."""
    return DatabaseManager(db_path)


@pytest.fixture
def skill_repo(db_manager: DatabaseManager) -> SkillRepository:
    return SkillRepository(db_manager)


@pytest.fixture
def execution_repo(db_manager: DatabaseManager) -> ExecutionRepository:
    return ExecutionRepository(db_manager)


@pytest.fixture
def account_repo(db_manager: DatabaseManager) -> AccountRepository:
    return AccountRepository(db_manager)


@pytest.fixture
def app(db_path: str) -> Any:
    """Create a Flask app instance pointed at the test database."""
    cfg = Config()
    cfg.database_url = f"sqlite:///{db_path}"
    application = create_app(cfg)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app: Any) -> Any:
    """Yield a Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_account(account_repo: AccountRepository) -> Account:
    """Create and return a sample account."""
    return account_repo.create(Account(address="0xabc123", balance=5000))


@pytest.fixture
def sample_skill(skill_repo: SkillRepository, sample_account: Account) -> Skill:
    """Create and return a sample skill owned by sample_account."""
    return skill_repo.create(
        Skill(
            name="test-skill",
            description="A test skill",
            endpoint="https://example.com/skill",
            owner_account_id=sample_account.id,
            price_per_call=100,
        )
    )
