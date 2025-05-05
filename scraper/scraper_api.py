from flask import Flask, request, jsonify
import subprocess
from scraper import scrape_single_title
from scraper import fetch_episode_dates

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

@app.route("/scrape", methods=["GET"])
def scrape():
    criteria = request.args.get('criteria', '')
    quantity_str = request.args.get('quantity', '50')
    print(f"Received request with criteria: {criteria} and quantity: {quantity_str}")

    try:
        quantity = int(quantity_str)
        result = subprocess.run(
            ["python3", "scraper.py", criteria, str(quantity)],
            capture_output=True,
            text=True,
            check=True,
            timeout=(quantity / 3)
        )
        print(f"Scraper Output: {result.stdout}")
        return jsonify({"success": True, "output": result.stdout.strip()})
    
    except subprocess.CalledProcessError as e:
        print(f"Scraper Error: {e.stderr}")
        return jsonify({"success": False, "error": e.stderr.strip()}), 500

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

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
