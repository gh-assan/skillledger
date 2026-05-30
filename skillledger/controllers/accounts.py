"""Account-related HTTP endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from skillledger.models import account_schema
from skillledger.services import AccountService

accounts_bp = Blueprint("accounts", __name__)


def _init(svc: AccountService) -> None:
    """Inject service dependencies (called at app factory time)."""
    accounts_bp.account_service = svc  # type: ignore[attr-defined]


@accounts_bp.route("/accounts", methods=["POST"])
def create_account():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body is required"}), 400
    address = data.get("address")
    if not address:
        return jsonify({"error": "address is required"}), 422
    try:
        account = accounts_bp.account_service.create(address)  # type: ignore[attr-defined]
        return jsonify(account_schema.dump(account)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@accounts_bp.route("/accounts/<account_id>/balance", methods=["GET"])
def get_balance(account_id: str):
    try:
        account = accounts_bp.account_service.get_balance(account_id)  # type: ignore[attr-defined]
        return jsonify(account_schema.dump(account)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
