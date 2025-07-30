from flask import Blueprint, request, jsonify
import json
import logging

db_bp = Blueprint('database', __name__)

@db_bp.route("/health", methods=["GET"])
def health():
    logging.info("Database health check requested.")
    return jsonify({"database_status": "running"}), 200