from flask import Flask, request, jsonify
import json
from scraper import scraper_main
from scraper import scrape_single_title
from scraper import fetch_episode_dates
import logging

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    logging.info("Health check requested.")
    return jsonify({"status": "running"}), 200

@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        data = request.get_json()
        if not data:
            logging.warning("Missing or invalid JSON body in /scrape request.")
            return jsonify({"success": False, "error": "Missing or invalid JSON body"}), 400

        criteria = data.get("criteria", {})
        quantity = int(data.get("quantity", 50))

        logging.info(f"Received /scrape request with criteria: {json.dumps(criteria)} and quantity: {quantity}")
        result = scraper_main(criteria, quantity)

        logging.info(f"Scrape completed. Inserted {result} titles.")
        return jsonify({"success": True, "result": result}), 200

    except Exception as e:
        error_msg = f"Unexpected error in /scrape: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return jsonify({"success": False, "error": error_msg}), 500

@app.route("/scrape/<title_id>", methods=["POST"])
def trigger_scrape(title_id):
    try:
        logging.info(f"Triggering scrape for single title: {title_id}")
        scrape_single_title(title_id)
        logging.info(f"Scraping complete for {title_id}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Error scraping single title {title_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/fetch_episodes', methods=['GET'])
def fetch_episodes():
    title_id = request.args.get('title_id')
    season_count = request.args.get('season_count')

    try:
        logging.info(f"Fetching episode dates for title_id={title_id}, season_count={season_count}")
        episode_data = fetch_episode_dates(title_id, season_count)
        logging.info(f"Fetched {len(episode_data)} episode dates for {title_id}")
        return jsonify({"status": "success", "data": episode_data}), 200
    except Exception as e:
        logging.error(f"Failed to fetch episode dates for {title_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=True, threaded=True)
