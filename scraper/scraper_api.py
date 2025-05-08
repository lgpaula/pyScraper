from flask import Flask, request, jsonify
import json
import subprocess
from scraper import scraper_main
from scraper import scrape_single_title
from scraper import fetch_episode_dates

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

@app.route("/scrape", methods=["GET"])
def scrape():
    criteria_str = request.args.get('criteria', '')
    quantity_str = request.args.get('quantity', '50')

    try:
        criteria = json.loads(criteria_str)
        quantity = int(quantity_str)
        new_titles = scraper_main(criteria, quantity)
        return jsonify({"status": "success", "data": new_titles}), 200
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Scraper Error for criteria '{criteria}': {e.stderr}"
        print(error_msg)
        return jsonify({"success": False, "error": error_msg.strip()}), 500

    except Exception as e:
        error_msg = f"Unexpected Error while processing criteria '{criteria}': {str(e)} and quantity '{quantity}'"
        print(error_msg)
        return jsonify({"success": False, "error": error_msg}), 500

@app.route("/scrape/<title_id>", methods=["POST"])
def trigger_scrape(title_id):
    try:
        scrape_single_title(title_id)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/fetch_episodes', methods=['GET'])
def fetch_episodes():
    title_id = request.args.get('title_id')
    season_count = request.args.get('season_count')
    try:
        episode_data = fetch_episode_dates(title_id, season_count)
        return jsonify({"status": "success", "data": episode_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=True, threaded=True)
