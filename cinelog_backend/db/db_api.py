from flask import Blueprint, request, jsonify
import json
import logging

db_bp = Blueprint('database', __name__)

@db_bp.route("/health", methods=["GET"])
def health():
    logging.info("Database health check requested.")
    return jsonify({"database_status": "running"}), 200

@db_bp.route('/items/<table>', methods=['GET'])
def get_items(table):
    # Your SQLite logic here
    return {"items": [...]}

@db_bp.route('/tables/<table_name>/exists', methods=['GET'])  
def table_exists(table_name):
    # Check if table exists
    return {"exists": True/False}