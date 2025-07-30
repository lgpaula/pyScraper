from flask import Blueprint, request, jsonify
import json
import logging

db_bp = Blueprint('database', __name__)

@db_bp.route("/health", methods=["GET"])
def health():
    logging.info("Health check requested.")
    return jsonify({"status": "running"}), 200