import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import logging
from datetime import datetime

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Set log file name with date format: backendYYYYMMDD.log
log_date = datetime.now().strftime('%Y%m%d')
log_file = os.path.join(log_dir, f'backend{log_date}.log')

# Configure logging
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [backend] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

for noisy_module in ['werkzeug', 'selenium', 'urllib3']:
    logging.getLogger(noisy_module).setLevel(logging.WARNING)

from datetime import datetime
from urllib.parse import urlencode
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from parser import *
from utils import XPaths
from db.database import *

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/XX.0.0.0 Safari/537.36")
    chrome_options.add_argument("--start-maximized")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(120)
    return driver

def scrape_multiple_titles(url: str, quantity=50):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    logging.info(f"Starting scrape for multiple titles from URL: {url}")

    try:
        driver.get(url)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        try:
            banner_button = WebDriverWait(driver, 3).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, XPaths.banner_element))
            )
            banner_button.click()
            wait.until_not(ec.presence_of_element_located((By.CSS_SELECTOR, XPaths.banner_element)))
            logging.info("Clicked and removed consent banner.")
        except Exception as e:
            logging.debug("Consent banner not found or couldn't click: %s", e)

        try:
            for _ in range((quantity // 50) - 1):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                button = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, XPaths.see_more_button)))
                driver.execute_script(XPaths.scroll_into_view, button)
                button.click()
                time.sleep(1)
                wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, XPaths.multi_title_item)) > 0)
                logging.debug("Clicked 'See More' to load more results.")
        except Exception as e:
            logging.warning("Scrolling or 'See More' interaction failed: %s", e)

        ul_element = driver.find_element(By.CLASS_NAME, XPaths.multi_title_parent)
        movie_items = ul_element.find_elements(By.CLASS_NAME, XPaths.multi_title_item)
        logging.info(f"Found {len(movie_items)} items. Parsing now.")
        movies = parse_title_list(movie_items)

        return movies

    finally:
        driver.quit()
        logging.debug("Driver quit after scraping multiple titles.")

def scrape_single_title(title_id):
    driver = setup_driver()
    try:
        url = f"https://www.imdb.com/title/{title_id}"
        logging.info(f"Scraping single title page: {url}")
        driver.get(url)
        time.sleep(1)

        parent1 = driver.find_element(By.CLASS_NAME, XPaths.single_title_parent_1)
        parent2 = driver.find_element(By.XPATH, XPaths.single_title_parent_2)

        parse_single_title(parent1, parent2, title_id)
        logging.info(f"Successfully parsed single title {title_id}")

    except Exception as e:
        logging.error(f"Failed scraping single title {title_id}: {e}", exc_info=True)
        raise
    finally:
        driver.quit()
        logging.debug("Driver quit after single title scrape.")

def fetch_episode_dates(title_id, season_count):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        url = f"https://www.imdb.com/title/{title_id}/episodes/?season={season_count}"
        logging.info(f"Fetching episode dates from URL: {url}")
        driver.get(url)

        try:
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "article.episode-item-wrapper")))
        except Exception as e:
            logging.warning(f"Episode items not loaded: {e}")
            return []

        episodes = driver.find_elements(By.CSS_SELECTOR, "article.episode-item-wrapper")
        logging.info(f"Found {len(episodes)} episodes. Extracting air dates.")
        dates = []

        for ep in episodes:
            try:
                date_span = ep.find_element(By.XPATH, ".//span[contains(text(), ',')]")
                date_text = date_span.text.strip()

                try:
                    dt = datetime.strptime(date_text, "%a, %b %d, %Y")
                    dates.append(dt.date().isoformat())
                except ValueError:
                    logging.debug(f"Skipping unparsable date: {date_text}")
            except Exception:
                continue

        add_schedule_to_title(title_id, dates)
        logging.info(f"Stored {len(dates)} dates for title {title_id}")
        return dates

    finally:
        driver.quit()
        logging.debug("Driver quit after fetching episode dates.")

def save_to_file(driver):
    with open("page_source.txt", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

def json_to_string(params: dict) -> str:
    query_params = {}

    # Format type
    type_mapping = {"Movie": "feature", "Series": "tv_series", "Short": "short", "TV Movie": "tv_movie", "TV Special": "tv_special", "TV Mini-Series": "tv_miniseries"}
    query_params["title_type"] = ",".join(type_mapping[t] for t in params.get("types", []) if t in type_mapping)

    # Format date
    year_from = f"{params['yearFrom']}-01-01" if "yearFrom" in params else ""
    year_to = f"{params['yearTo']}-12-31" if "yearTo" in params else ""
    query_params["release_date"] = f"{year_from},{year_to}".rstrip(",")

    # Format user rating
    rating_from = params.get("ratingFrom", "")
    rating_to = params.get("ratingTo", "")
    query_params["user_rating"] = f"{rating_from},{rating_to}".rstrip(",")

    # Format companies
    if params.get("companies"):
        query_params["companies"] = ",".join(c.lower() for c in params["companies"])

    # Format names
    if params.get("role"):
        query_params["role"] = ",".join(n.lower() for n in params["role"])

    # Format genres
    if params.get("genres"):
        query_params["genres"] = ",".join(g.lower() for g in params["genres"])

    # Build query string
    return "?" + urlencode(query_params, doseq=True)

def custom_search_url(params: dict) -> str:
    base_url = "https://www.imdb.com/search/title/"

    print("Params received:", json.dumps(params, indent=2))
    complementary_url = json_to_string(params)

    return base_url + complementary_url

def scraper_main(criteria, quantity):
    criteria_url = custom_search_url(criteria)
    logging.info(f"Generated search URL: {criteria_url}")

    movies = scrape_multiple_titles(criteria_url, quantity)
    create_table()

    inserted = 0
    for movie in movies:
        if insert_title(movie):
            inserted += 1

    logging.info(f"Inserted {inserted} out of {len(movies)} scraped titles into database.")
    return inserted

if __name__ == "__main__":
    # scrape_single_title("tt2085059")

    criteria = {"genres": [], "companies": [], "types": ["Movie", "Series", "Short", "TV Movie", "TV Special", "TV Mini-Series"], "yearFrom": None, "yearTo": None, "ratingFrom": 0.0, "ratingTo": 10.0}
    quantity = 50
    scraper_main(criteria, quantity)

    # print(fetch_episode_dates("tt31510819", 1))


'''
    # scrape_single_title("tt14961016")

    # example of custom search
    # params = {
    #     "title_type": ["feature", "tv_series"],
    #     "user_rating": ["8", "10"],
    #     "genres": ["comedy", "animation", "action"]
    # }

    #"https://www.imdb.com/search/title/?title_type=feature&genres=action"

scrapable:

type { title_type=tv_special,feature,tv_series,short,tv_miniseries,tv_movie,tv_short
    - movie (+tvmovie)
    - tvseries(+shorts + tvminiseries)
}
release_date { release_date=2000-01-01,2010-12-31 OR release_date=2000-01-01,
    - yyyy
    - yyyy - yyyy
}
imdb_rating { user_rating=5, OR user_rating=5,10
    - xx.x
    - xx.x - xx.x
}
genre { genres=action,animation,crime
    - 27 main ones
}
companies { companies=fox,mgm,universal,co0390816
    - 8 main ones
    - discoverable ones
}
keywords {
    - 211 ish discoverable ones
}
'''


'''
eventually:

sort by:
    - popularity
    - user rating
    - number of votes
'''