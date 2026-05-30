"""Functional tests — full HTTP flow with real SQLite database."""

from __future__ import annotations

import json
from typing import Any


class TestHealth:
    def test_health_ok(self, client: Any) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}


class TestAccounts:
    def test_create_account(self, client: Any) -> None:
        resp = client.post(
            "/accounts",
            data=json.dumps({"address": "0xdeadbeef"}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["address"] == "0xdeadbeef"
        assert data["balance"] == 1000  # welcome bonus
        assert "id" in data

    def test_create_account_missing_address(self, client: Any) -> None:
        resp = client.post(
            "/accounts",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 422

    def test_create_account_empty_body(self, client: Any) -> None:
        resp = client.post(
            "/accounts",
            data=json.dumps(None),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_get_balance(self, client: Any) -> None:
        # Create first
        create = client.post(
            "/accounts",
            data=json.dumps({"address": "0xaa"}),
            content_type="application/json",
        )
        account_id = create.get_json()["id"]

        resp = client.get(f"/accounts/{account_id}/balance")
        assert resp.status_code == 200
        assert resp.get_json()["balance"] == 1000

    def test_get_balance_not_found(self, client: Any) -> None:
        resp = client.get("/accounts/nonexistent/balance")
        assert resp.status_code == 404


class TestSkills:
    def test_create_skill(self, client: Any, sample_account: Any) -> None:
        resp = client.post(
            "/skills",
            data=json.dumps({
                "name": "data-analyzer",
                "description": "Analyzes data sets",
                "endpoint": "https://api.example.com/analyze",
                "owner_account_id": sample_account.id,
                "price_per_call": 150,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "data-analyzer"
        assert data["price_per_call"] == 150
        assert data["status"] == "active"
        assert "id" in data

    def test_create_skill_no_body(self, client: Any) -> None:
        resp = client.post(
            "/skills",
            data=json.dumps(None),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_skill_validation_error(self, client: Any) -> None:
        resp = client.post(
            "/skills",
            data=json.dumps({"name": ""}),  # missing required fields
            content_type="application/json",
        )
        assert resp.status_code == 422

    def test_create_skill_owner_not_found(self, client: Any) -> None:
        resp = client.post(
            "/skills",
            data=json.dumps({
                "name": "orphan-skill",
                "description": "No owner exists",
                "endpoint": "https://example.com/skill",
                "owner_account_id": "nonexistent",
                "price_per_call": 10,
            }),
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_list_skills(self, client: Any, sample_skill: Any) -> None:
        resp = client.get("/skills")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["name"] == "test-skill"

    def test_get_skill(self, client: Any, sample_skill: Any) -> None:
        resp = client.get(f"/skills/{sample_skill.id}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "test-skill"

    def test_get_skill_not_found(self, client: Any) -> None:
        resp = client.get("/skills/nonexistent")
        assert resp.status_code == 404


class TestExecutions:
    def test_execute_skill(
        self, client: Any, sample_skill: Any, sample_account: Any
    ) -> None:
        resp = client.post(
            f"/skills/{sample_skill.id}/execute",
            data=json.dumps({
                "requester_account_id": sample_account.id,
                "input_params": {"data": "test"},
            }),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["skill_id"] == sample_skill.id
        assert data["requester_account_id"] == sample_account.id
        assert data["status"] == "running"

    def test_execute_skill_not_found(self, client: Any) -> None:
        resp = client.post(
            "/skills/nonexistent/execute",
            data=json.dumps({
                "requester_account_id": "some-account",
                "input_params": {},
            }),
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_execute_skill_missing_requester(
        self, client: Any, sample_skill: Any
    ) -> None:
        resp = client.post(
            f"/skills/{sample_skill.id}/execute",
            data=json.dumps({"input_params": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 422

    def test_list_executions(
        self, client: Any, sample_skill: Any, sample_account: Any
    ) -> None:
        # Create an execution first
        client.post(
            f"/skills/{sample_skill.id}/execute",
            data=json.dumps({
                "requester_account_id": sample_account.id,
                "input_params": {},
            }),
            content_type="application/json",
        )
        resp = client.get("/executions")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] >= 1

    def test_get_execution(
        self, client: Any, sample_skill: Any, sample_account: Any
    ) -> None:
        create = client.post(
            f"/skills/{sample_skill.id}/execute",
            data=json.dumps({
                "requester_account_id": sample_account.id,
                "input_params": {},
            }),
            content_type="application/json",
        )
        exec_id = create.get_json()["id"]
        resp = client.get(f"/executions/{exec_id}")
        assert resp.status_code == 200

    def test_get_execution_not_found(self, client: Any) -> None:
        resp = client.get("/executions/nonexistent")
        assert resp.status_code == 404

    def test_verify_execution(
        self, client: Any, sample_skill: Any, sample_account: Any
    ) -> None:
        create = client.post(
            f"/skills/{sample_skill.id}/execute",
            data=json.dumps({
                "requester_account_id": sample_account.id,
                "input_params": {},
            }),
            content_type="application/json",
        )
        exec_id = create.get_json()["id"]

        # Verify
        resp = client.post(f"/executions/{exec_id}/verify")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "completed"

    def test_verify_execution_not_found(self, client: Any) -> None:
        resp = client.post("/executions/nonexistent/verify")
        assert resp.status_code == 404


class TestFullFlow:
    """End-to-end: create skill → execute → verify."""

    def test_full_flow(self, client: Any) -> None:
        # 1. Create two accounts (requester + owner)
        owner_resp = client.post(
            "/accounts",
            data=json.dumps({"address": "0xowner"}),
            content_type="application/json",
        )
        owner_id = owner_resp.get_json()["id"]

        requester_resp = client.post(
            "/accounts",
            data=json.dumps({"address": "0xrequester"}),
            content_type="application/json",
        )
        requester_id = requester_resp.get_json()["id"]

        # 2. Register a skill
        skill_resp = client.post(
            "/skills",
            data=json.dumps({
                "name": "gold-miner",
                "description": "Mines blockchain data",
                "endpoint": "https://mine.example.com",
                "owner_account_id": owner_id,
                "price_per_call": 200,
            }),
            content_type="application/json",
        )
        skill_id = skill_resp.get_json()["id"]

        # 3. Execute
        exec_resp = client.post(
            f"/skills/{skill_id}/execute",
            data=json.dumps({
                "requester_account_id": requester_id,
                "input_params": {"depth": "full"},
            }),
            content_type="application/json",
        )
        assert exec_resp.status_code == 201
        exec_id = exec_resp.get_json()["id"]

        # 4. Verify and settle
        verify_resp = client.post(f"/executions/{exec_id}/verify")
        assert verify_resp.status_code == 200
        assert verify_resp.get_json()["status"] == "completed"

        # 5. Check balances changed
        owner_bal = client.get(f"/accounts/{owner_id}/balance")
        assert owner_bal.get_json()["balance"] == 1200  # 1000 + 200

        requester_bal = client.get(f"/accounts/{requester_id}/balance")
        assert requester_bal.get_json()["balance"] == 800  # 1000 - 200
