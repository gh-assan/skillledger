"""Skill-related HTTP endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from skillledger.models import skill_schema, skills_schema
from skillledger.services import ExecutionService, SkillService

skills_bp = Blueprint("skills", __name__)


def _init(svc: SkillService, exec_svc: ExecutionService) -> None:
    """Inject service dependencies into the blueprint (called at app factory time)."""
    skills_bp.skill_service = svc  # type: ignore[attr-defined]
    skills_bp.execution_service = exec_svc  # type: ignore[attr-defined]


@skills_bp.route("/skills", methods=["POST"])
def create_skill():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body is required"}), 400
    errors = skill_schema.validate(data)
    if errors:
        return jsonify({"error": "Validation failed", "detail": errors}), 422
    try:
        skill = skills_bp.skill_service.create(data)  # type: ignore[attr-defined]
        return jsonify(skill_schema.dump(skill)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@skills_bp.route("/skills", methods=["GET"])
def list_skills():
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    skills, total = skills_bp.skill_service.list_skills(  # type: ignore[attr-defined]
        status=status, page=page, per_page=per_page
    )
    return jsonify({
        "items": skills_schema.dump(skills),
        "total": total,
        "page": page,
        "per_page": per_page,
    }), 200


@skills_bp.route("/skills/<skill_id>", methods=["GET"])
def get_skill(skill_id: str):
    try:
        skill = skills_bp.skill_service.get_by_id(skill_id)  # type: ignore[attr-defined]
        return jsonify(skill_schema.dump(skill)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@skills_bp.route("/skills/<skill_id>/execute", methods=["POST"])
def execute_skill(skill_id: str):
    data = request.get_json(silent=True) or {}
    requester_id = data.get("requester_account_id")
    if not requester_id:
        return jsonify({"error": "requester_account_id is required"}), 422
    params = data.get("input_params", {})
    if not isinstance(params, dict):
        return jsonify({"error": "input_params must be a JSON object"}), 422
    try:
        execution = skills_bp.execution_service.create(  # type: ignore[attr-defined]
            skill_id=skill_id,
            requester_id=requester_id,
            params=params,
        )
        from skillledger.models import execution_schema
        return jsonify(execution_schema.dump(execution)), 201
    except ValueError as e:
        status = 404 if "not found" in str(e) else 422
        return jsonify({"error": str(e)}), status
