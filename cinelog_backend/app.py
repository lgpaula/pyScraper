from flask import Flask
from data_scraper.scraper_api import scraping_bp
from db.db_api import db_bp

app = Flask(__name__)
app.register_blueprint(scraping_bp, url_prefix="/scraping")
app.register_blueprint(db_bp, url_prefix="/db")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)