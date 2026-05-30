"""Repository layer — abstracts all data access behind a clean interface."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

from skillledger.models import Account, Execution, Skill


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a sqlite3.Row to a plain dict, parsing JSON and datetime fields."""
    from datetime import datetime

    data = dict(row)
    # Parse datetime fields from ISO strings (only if key exists in row)
    for key in ("created_at", "verified_at"):
        if key not in data:
            continue
        val = data[key]
        if isinstance(val, str) and val.strip():
            try:
                # Remove trailing Z or +00:00 for Python 3.9 compat
                clean = val.replace("T", " ").split(".")[0].rstrip("Z").replace("+00:00", "").replace("-00:00", "").strip()
                data[key] = datetime.fromisoformat(clean) if clean else None
            except ValueError:
                pass
        elif val is None:
            data[key] = None
    # Parse JSON fields
    for key in ("input_params", "result"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            try:
                data[key] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return data


class DatabaseManager:
    """Manages the SQLite connection and provides a context manager for transactions."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


class SkillRepository:
    """Data access for the ``skills`` table."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, skill: Skill) -> Skill:
        with self._db.connect() as conn:
            conn.execute(
                """INSERT INTO skills (id, name, description, endpoint,
                   owner_account_id, price_per_call, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    skill.id,
                    skill.name,
                    skill.description,
                    skill.endpoint,
                    skill.owner_account_id,
                    skill.price_per_call,
                    skill.status,
                    skill.created_at.isoformat(),
                ),
            )
        return skill

    def find_by_id(self, skill_id: str) -> Skill | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM skills WHERE id = ?", (skill_id,)
            ).fetchone()
        if row is None:
            return None
        data = _row_to_dict(row)
        return Skill(**data)

    def list_all(
        self, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> tuple[list[Skill], int]:
        with self._db.connect() as conn:
            where = "WHERE status = ?" if status else ""
            params: tuple = (status,) if status else ()
            total = conn.execute(
                f"SELECT COUNT(*) FROM skills {where}", params
            ).fetchone()[0]
            offset = (page - 1) * per_page
            rows = conn.execute(
                f"SELECT * FROM skills {where} ORDER BY created_at DESC "
                f"LIMIT ? OFFSET ?",
                params + (per_page, offset),
            ).fetchall()
        skills = [Skill(**_row_to_dict(r)) for r in rows]
        return skills, total


class ExecutionRepository:
    """Data access for the ``executions`` table."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, execution: Execution) -> Execution:
        with self._db.connect() as conn:
            conn.execute(
                """INSERT INTO executions
                   (id, skill_id, requester_account_id, input_params,
                    status, result, cost, created_at, verified_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    execution.id,
                    execution.skill_id,
                    execution.requester_account_id,
                    json.dumps(execution.input_params or {}),
                    execution.status,
                    json.dumps(execution.result or {}),
                    execution.cost,
                    execution.created_at.isoformat(),
                    None,
                ),
            )
        return execution

    def find_by_id(self, execution_id: str) -> Execution | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM executions WHERE id = ?", (execution_id,)
            ).fetchone()
        if row is None:
            return None
        data = _row_to_dict(row)
        return Execution(**data)

    def list_all(
        self,
        skill_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Execution], int]:
        with self._db.connect() as conn:
            conditions: list[str] = []
            params: list[Any] = []
            if skill_id:
                conditions.append("skill_id = ?")
                params.append(skill_id)
            if status:
                conditions.append("status = ?")
                params.append(status)
            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            total = conn.execute(
                f"SELECT COUNT(*) FROM executions {where}", params
            ).fetchone()[0]
            offset = (page - 1) * per_page
            rows = conn.execute(
                f"SELECT * FROM executions {where} ORDER BY created_at DESC "
                f"LIMIT ? OFFSET ?",
                params + [per_page, offset],
            ).fetchall()
        exs = [Execution(**_row_to_dict(r)) for r in rows]
        return exs, total

    def update_status(
        self,
        execution_id: str,
        status: str,
        result: dict[str, Any] | None = None,
        cost: int | None = None,
    ) -> Execution | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM executions WHERE id = ?", (execution_id,)
            ).fetchone()
            if row is None:
                return None
            data = _row_to_dict(row)
            execution = Execution(**data)
            execution.status = status
            if result is not None:
                execution.result = result
            if cost is not None:
                execution.cost = cost
            conn.execute(
                """UPDATE executions SET status=?, result=?, cost=?
                   WHERE id=?""",
                (
                    execution.status,
                    json.dumps(execution.result or {}),
                    execution.cost,
                    execution_id,
                ),
            )
        return execution

    def verify(self, execution_id: str) -> Execution | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM executions WHERE id = ?", (execution_id,)
            ).fetchone()
            if row is None:
                return None
            data = _row_to_dict(row)
            execution = Execution(**data)
            execution.status = "completed"
            execution.verified_at = datetime.now(timezone.utc)
            conn.execute(
                """UPDATE executions SET status=?, verified_at=?
                   WHERE id=?""",
                (execution.status, execution.verified_at.isoformat(), execution_id),
            )
        return execution


class AccountRepository:
    """Data access for the ``accounts`` table."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, account: Account) -> Account:
        with self._db.connect() as conn:
            conn.execute(
                """INSERT INTO accounts (id, address, balance, created_at)
                   VALUES (?, ?, ?, ?)""",
                (
                    account.id,
                    account.address,
                    account.balance,
                    account.created_at.isoformat(),
                ),
            )
        return account

    def find_by_id(self, account_id: str) -> Account | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM accounts WHERE id = ?", (account_id,)
            ).fetchone()
        if row is None:
            return None
        data = _row_to_dict(row)
        return Account(**data)

    def update_balance(self, account_id: str, delta: int) -> Account | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM accounts WHERE id = ?", (account_id,)
            ).fetchone()
            if row is None:
                return None
            data = _row_to_dict(row)
            account = Account(**data)
            account.balance += delta
            conn.execute(
                "UPDATE accounts SET balance=? WHERE id=?",
                (account.balance, account_id),
            )
        return account
