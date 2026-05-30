"""Business-logic layer — all rules & orchestration live here.

Controllers must NOT import repositories directly; they go through services.
"""

from __future__ import annotations

from typing import Any

from skillledger.models import Account, Execution, Skill
from skillledger.repositories import (
    AccountRepository,
    ExecutionRepository,
    SkillRepository,
)


# ---------------------------------------------------------------------------
# SkillService
# ---------------------------------------------------------------------------


class SkillService:
    """Business rules for skill lifecycle."""

    def __init__(
        self,
        skill_repo: SkillRepository,
        account_repo: AccountRepository,
    ) -> None:
        self._skill_repo = skill_repo
        self._account_repo = account_repo

    def create(self, data: dict[str, Any]) -> Skill:
        """Register a new skill. Owner account must exist."""
        owner_id = data["owner_account_id"]
        if self._account_repo.find_by_id(owner_id) is None:
            raise ValueError(f"Account {owner_id} not found")
        skill = Skill(
            name=data["name"],
            description=data["description"],
            endpoint=data["endpoint"],
            owner_account_id=owner_id,
            price_per_call=data["price_per_call"],
        )
        return self._skill_repo.create(skill)

    def get_by_id(self, skill_id: str) -> Skill:
        """Fetch a skill by ID or raise ValueError."""
        skill = self._skill_repo.find_by_id(skill_id)
        if skill is None:
            raise ValueError(f"Skill {skill_id} not found")
        return skill

    def list_skills(
        self, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> tuple[list[Skill], int]:
        """List skills with optional status filter and pagination."""
        return self._skill_repo.list_all(status=status, page=page, per_page=per_page)


# ---------------------------------------------------------------------------
# ExecutionService
# ---------------------------------------------------------------------------


class ExecutionService:
    """Business rules for execution lifecycle."""

    def __init__(
        self,
        execution_repo: ExecutionRepository,
        skill_repo: SkillRepository,
        account_repo: AccountRepository,
    ) -> None:
        self._execution_repo = execution_repo
        self._skill_repo = skill_repo
        self._account_repo = account_repo

    def create(self, skill_id: str, requester_id: str, params: dict[str, Any]) -> Execution:
        """Initiate an execution. Validates skill is active and requester exists."""
        skill = self._skill_repo.find_by_id(skill_id)
        if skill is None:
            raise ValueError(f"Skill {skill_id} not found")
        if skill.status != "active":
            raise ValueError(f"Skill {skill_id} is not active")
        if self._account_repo.find_by_id(requester_id) is None:
            raise ValueError(f"Account {requester_id} not found")

        execution = Execution(
            skill_id=skill_id,
            requester_account_id=requester_id,
            input_params=params,
            status="running",
            cost=skill.price_per_call,
        )
        return self._execution_repo.create(execution)

    def get_by_id(self, execution_id: str) -> Execution:
        """Fetch an execution by ID or raise ValueError."""
        execution = self._execution_repo.find_by_id(execution_id)
        if execution is None:
            raise ValueError(f"Execution {execution_id} not found")
        return execution

    def list_executions(
        self,
        skill_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Execution], int]:
        """List executions with optional filters and pagination."""
        return self._execution_repo.list_all(
            skill_id=skill_id, status=status, page=page, per_page=per_page
        )

    def update_status(
        self,
        execution_id: str,
        status: str,
        result: dict[str, Any] | None = None,
    ) -> Execution:
        """Update execution status and result."""
        execution = self._execution_repo.update_status(
            execution_id, status, result=result
        )
        if execution is None:
            raise ValueError(f"Execution {execution_id} not found")
        return execution

    def verify_and_settle(self, execution_id: str) -> Execution:
        """Verify an execution and settle payment from requester to skill owner."""
        execution = self._execution_repo.find_by_id(execution_id)
        if execution is None:
            raise ValueError(f"Execution {execution_id} not found")
        if execution.status != "running":
            raise ValueError(
                f"Execution {execution_id} is {execution.status}, expected 'running'"
            )

        skill = self._skill_repo.find_by_id(execution.skill_id)
        if skill is None:
            raise ValueError(f"Skill {execution.skill_id} not found")

        # Deduct from requester
        requester = self._account_repo.update_balance(
            execution.requester_account_id, -skill.price_per_call
        )
        if requester is None:
            raise ValueError(
                f"Requester account {execution.requester_account_id} not found"
            )
        if requester.balance < 0:
            raise ValueError(
                f"Insufficient balance in account {execution.requester_account_id}"
            )

        # Credit to owner
        self._account_repo.update_balance(
            skill.owner_account_id, skill.price_per_call
        )

        # Mark verified
        verified = self._execution_repo.verify(execution_id)
        if verified is None:
            raise ValueError(f"Execution {execution_id} not found after verify")
        return verified


# ---------------------------------------------------------------------------
# AccountService
# ---------------------------------------------------------------------------


class AccountService:
    """Business rules for account management."""

    def __init__(self, account_repo: AccountRepository) -> None:
        self._account_repo = account_repo

    def create(self, address: str) -> Account:
        """Create a new account with a welcome bonus."""
        account = Account(address=address, balance=1000)
        return self._account_repo.create(account)

    def get_balance(self, account_id: str) -> Account:
        """Fetch account balance or raise ValueError."""
        account = self._account_repo.find_by_id(account_id)
        if account is None:
            raise ValueError(f"Account {account_id} not found")
        return account
