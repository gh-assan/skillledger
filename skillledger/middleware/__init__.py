"""Middleware — error handling, request logging, auth."""

from __future__ import annotations

import logging
import time
import traceback
from typing import Any

import flask
from flask import Flask, jsonify

logger = logging.getLogger("skillledger")


def register_error_handlers(app: Flask) -> None:
    """Register consistent JSON error handlers on the Flask app."""

    @app.errorhandler(400)
    def bad_request(e: Any) -> flask.Response:
        return jsonify({"error": "Bad request", "detail": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e: Any) -> flask.Response:
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e: Any) -> flask.Response:
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(422)
    def unprocessable(e: Any) -> flask.Response:
        return jsonify({"error": "Unprocessable entity"}), 422

    @app.errorhandler(500)
    def server_error(e: Any) -> flask.Response:
        logger.error("Internal server error: %s", traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500


def register_request_logging(app: Flask) -> None:
    """Log every request with method, path, status, and duration."""

    @app.before_request
    def _start_timer() -> None:
        flask.g.start_time = time.time()

    @app.after_request
    def _log_request(response: flask.Response) -> flask.Response:
        duration = time.time() - flask.g.get("start_time", time.time())
        logger.info(
            "%s %s -> %s [%.3fs]",
            flask.request.method,
            flask.request.path,
            response.status_code,
            duration,
        )
        return response
