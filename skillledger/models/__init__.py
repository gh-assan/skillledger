"""Domain models and marshmallow schemas for SkillLedger."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from marshmallow import Schema, fields, post_load, validate


# ---------------------------------------------------------------------------
# Domain dataclasses
# ---------------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class Skill:
    """A deployable skill registered on the marketplace."""

    id: str = field(default_factory=_uuid)
    name: str = ""
    description: str = ""
    endpoint: str = ""
    owner_account_id: str = ""
    price_per_call: int = 0
    status: str = "active"
    created_at: datetime = field(default_factory=_now)


@dataclass
class Execution:
    """A single invocation (or task) of a skill."""

    id: str = field(default_factory=_uuid)
    skill_id: str = ""
    requester_account_id: str = ""
    input_params: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: dict[str, Any] | None = None
    cost: int = 0
    created_at: datetime = field(default_factory=_now)
    verified_at: datetime | None = None


@dataclass
class Account:
    """An agent account / wallet on the platform."""

    id: str = field(default_factory=_uuid)
    address: str = ""
    balance: int = 0
    created_at: datetime = field(default_factory=_now)


# ---------------------------------------------------------------------------
# Marshmallow schemas (serialisation / validation)
# ---------------------------------------------------------------------------


class SkillSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=True, validate=validate.Length(min=1))
    endpoint = fields.Url(required=True)
    owner_account_id = fields.String(required=True)
    price_per_call = fields.Integer(
        required=True, validate=validate.Range(min=0), strict=True
    )
    status = fields.String(
        dump_only=True,
        validate=validate.OneOf(["active", "inactive"]),
    )
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make_skill(self, data: dict, **kwargs: Any) -> Skill:
        return Skill(**data)


class ExecutionSchema(Schema):
    id = fields.String(dump_only=True)
    skill_id = fields.String(required=True)
    requester_account_id = fields.String(required=True)
    input_params = fields.Dict(load_default=dict)
    status = fields.String(
        dump_only=True,
        validate=validate.OneOf(["pending", "running", "completed", "failed"]),
    )
    result = fields.Dict(allow_none=True, dump_only=True)
    cost = fields.Integer(dump_only=True, strict=True)
    created_at = fields.DateTime(dump_only=True)
    verified_at = fields.DateTime(allow_none=True, dump_only=True)

    @post_load
    def make_execution(self, data: dict, **kwargs: Any) -> Execution:
        return Execution(**data)


class AccountSchema(Schema):
    id = fields.String(dump_only=True)
    address = fields.String(
        required=True, validate=validate.Length(min=1, max=255)
    )
    balance = fields.Integer(dump_only=True, strict=True)
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make_account(self, data: dict, **kwargs: Any) -> Account:
        return Account(**data)


# ---------------------------------------------------------------------------
# Response wrappers
# ---------------------------------------------------------------------------


class ErrorResponseSchema(Schema):
    error = fields.String(required=True)
    detail = fields.Dict(allow_none=True)


class PaginatedResponseSchema(Schema):
    items = fields.List(fields.Raw(), required=True)
    total = fields.Integer(required=True, strict=True)
    page = fields.Integer(required=True, strict=True)
    per_page = fields.Integer(required=True, strict=True)


# Convenience helpers -------------------------------------------------------

skill_schema = SkillSchema()
skills_schema = SkillSchema(many=True)
execution_schema = ExecutionSchema()
executions_schema = ExecutionSchema(many=True)
account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)
error_schema = ErrorResponseSchema()
