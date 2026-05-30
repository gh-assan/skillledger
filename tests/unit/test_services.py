"""Unit tests for service layer — all repositories mocked."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from skillledger.models import Account, Execution, Skill
from skillledger.services import AccountService, ExecutionService, SkillService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_mock_repos() -> dict[str, MagicMock]:
    return {
        "skill": MagicMock(),
        "execution": MagicMock(),
        "account": MagicMock(),
    }


# ---------------------------------------------------------------------------
# SkillService
# ---------------------------------------------------------------------------


class TestSkillService:
    def test_create_skill_ok(self) -> None:
        repos = make_mock_repos()
        repos["account"].find_by_id.return_value = Account(
            id="acc-1", address="0xabc"
        )
        repos["skill"].create.return_value = Skill(
            id="skill-1", name="my-skill", endpoint="https://example.com/skill"
        )
        svc = SkillService(repos["skill"], repos["account"])
        data: dict[str, Any] = {
            "name": "my-skill",
            "description": "desc",
            "endpoint": "https://example.com/skill",
            "owner_account_id": "acc-1",
            "price_per_call": 50,
        }
        result = svc.create(data)
        assert result.name == "my-skill"
        repos["skill"].create.assert_called_once()

    def test_create_skill_account_not_found(self) -> None:
        repos = make_mock_repos()
        repos["account"].find_by_id.return_value = None
        svc = SkillService(repos["skill"], repos["account"])
        data: dict[str, Any] = {
            "name": "my-skill",
            "description": "desc",
            "endpoint": "https://example.com/skill",
            "owner_account_id": "missing",
            "price_per_call": 50,
        }
        with pytest.raises(ValueError, match="missing"):
            svc.create(data)

    def test_get_by_id_found(self) -> None:
        repos = make_mock_repos()
        repos["skill"].find_by_id.return_value = Skill(
            id="s-1", name="test", endpoint="https://example.com/skill"
        )
        svc = SkillService(repos["skill"], repos["account"])
        skill = svc.get_by_id("s-1")
        assert skill.id == "s-1"

    def test_get_by_id_not_found(self) -> None:
        repos = make_mock_repos()
        repos["skill"].find_by_id.return_value = None
        svc = SkillService(repos["skill"], repos["account"])
        with pytest.raises(ValueError, match="not found"):
            svc.get_by_id("missing")

    def test_list_skills(self) -> None:
        repos = make_mock_repos()
        repos["skill"].list_all.return_value = ([], 0)
        svc = SkillService(repos["skill"], repos["account"])
        skills, total = svc.list_skills()
        assert skills == []
        assert total == 0


# ---------------------------------------------------------------------------
# ExecutionService
# ---------------------------------------------------------------------------


class TestExecutionService:
    def test_create_execution_ok(self) -> None:
        repos = make_mock_repos()
        repos["skill"].find_by_id.return_value = Skill(
            id="s-1",
            name="test",
            status="active",
            price_per_call=100,
            endpoint="https://example.com/skill",
        )
        repos["account"].find_by_id.return_value = Account(id="acc-1")
        repos["execution"].create.return_value = Execution(
            id="exec-1", skill_id="s-1", requester_account_id="acc-1"
        )
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        result = svc.create("s-1", "acc-1", {"key": "val"})
        assert result.id == "exec-1"
        repos["execution"].create.assert_called_once()

    def test_create_execution_skill_not_found(self) -> None:
        repos = make_mock_repos()
        repos["skill"].find_by_id.return_value = None
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        with pytest.raises(ValueError, match="not found"):
            svc.create("missing", "acc-1", {})

    def test_create_execution_skill_inactive(self) -> None:
        repos = make_mock_repos()
        repos["skill"].find_by_id.return_value = Skill(
            id="s-1",
            name="test",
            status="inactive",
            endpoint="https://example.com/skill",
        )
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        with pytest.raises(ValueError, match="not active"):
            svc.create("s-1", "acc-1", {})

    def test_create_execution_requester_not_found(self) -> None:
        repos = make_mock_repos()
        repos["skill"].find_by_id.return_value = Skill(
            id="s-1",
            name="test",
            status="active",
            endpoint="https://example.com/skill",
        )
        repos["account"].find_by_id.return_value = None
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        with pytest.raises(ValueError, match="not found"):
            svc.create("s-1", "acc-1", {})

    def test_verify_and_settle_ok(self) -> None:
        repos = make_mock_repos()
        repos["execution"].find_by_id.return_value = Execution(
            id="exec-1",
            skill_id="s-1",
            requester_account_id="acc-req",
            status="running",
            cost=100,
        )
        repos["skill"].find_by_id.return_value = Skill(
            id="s-1",
            name="test",
            owner_account_id="acc-owner",
            price_per_call=100,
            endpoint="https://example.com/skill",
        )
        repos["account"].update_balance.side_effect = [
            Account(id="acc-req", balance=900),
            Account(id="acc-owner", balance=1100),
        ]
        repos["execution"].verify.return_value = Execution(
            id="exec-1",
            skill_id="s-1",
            requester_account_id="acc-req",
            status="completed",
            cost=100,
        )
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        result = svc.verify_and_settle("exec-1")
        assert result.status == "completed"
        assert repos["account"].update_balance.call_count == 2

    def test_verify_and_settle_not_found(self) -> None:
        repos = make_mock_repos()
        repos["execution"].find_by_id.return_value = None
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        with pytest.raises(ValueError, match="not found"):
            svc.verify_and_settle("missing")

    def test_verify_and_settle_wrong_status(self) -> None:
        repos = make_mock_repos()
        repos["execution"].find_by_id.return_value = Execution(
            id="exec-1",
            skill_id="s-1",
            requester_account_id="acc-req",
            status="completed",
        )
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        with pytest.raises(ValueError, match="expected 'running'"):
            svc.verify_and_settle("exec-1")

    def test_get_by_id_found(self) -> None:
        repos = make_mock_repos()
        repos["execution"].find_by_id.return_value = Execution(
            id="exec-1", skill_id="s-1"
        )
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        execution = svc.get_by_id("exec-1")
        assert execution.id == "exec-1"

    def test_get_by_id_not_found(self) -> None:
        repos = make_mock_repos()
        repos["execution"].find_by_id.return_value = None
        svc = ExecutionService(repos["execution"], repos["skill"], repos["account"])
        with pytest.raises(ValueError, match="not found"):
            svc.get_by_id("missing")


# ---------------------------------------------------------------------------
# AccountService
# ---------------------------------------------------------------------------


class TestAccountService:
    def test_create_account(self) -> None:
        repos = make_mock_repos()
        repos["account"].create.return_value = Account(
            id="acc-1", address="0xabc", balance=1000
        )
        svc = AccountService(repos["account"])
        account = svc.create("0xabc")
        assert account.balance == 1000
        repos["account"].create.assert_called_once()

    def test_get_balance_found(self) -> None:
        repos = make_mock_repos()
        repos["account"].find_by_id.return_value = Account(
            id="acc-1", address="0xabc", balance=500
        )
        svc = AccountService(repos["account"])
        account = svc.get_balance("acc-1")
        assert account.balance == 500

    def test_get_balance_not_found(self) -> None:
        repos = make_mock_repos()
        repos["account"].find_by_id.return_value = None
        svc = AccountService(repos["account"])
        with pytest.raises(ValueError, match="not found"):
            svc.get_balance("missing")
