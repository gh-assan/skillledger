"""Execution-related HTTP endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from skillledger.models import execution_schema, executions_schema
from skillledger.services import ExecutionService

executions_bp = Blueprint("executions", __name__)


def _init(svc: ExecutionService) -> None:
    """Inject service dependencies (called at app factory time)."""
    executions_bp.execution_service = svc  # type: ignore[attr-defined]


@executions_bp.route("/executions", methods=["GET"])
def list_executions():
    skill_id = request.args.get("skill_id")
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    execs, total = executions_bp.execution_service.list_executions(  # type: ignore[attr-defined]
        skill_id=skill_id, status=status, page=page, per_page=per_page
    )
    return jsonify({
        "items": executions_schema.dump(execs),
        "total": total,
        "page": page,
        "per_page": per_page,
    }), 200


@executions_bp.route("/executions/<execution_id>", methods=["GET"])
def get_execution(execution_id: str):
    try:
        execution = executions_bp.execution_service.get_by_id(execution_id)  # type: ignore[attr-defined]
        return jsonify(execution_schema.dump(execution)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@executions_bp.route("/executions/<execution_id>/verify", methods=["POST"])
def verify_execution(execution_id: str):
    try:
        execution = executions_bp.execution_service.verify_and_settle(execution_id)  # type: ignore[attr-defined]
        return jsonify(execution_schema.dump(execution)), 200
    except ValueError as e:
        status = 404 if "not found" in str(e) else 422
        return jsonify({"error": str(e)}), status
