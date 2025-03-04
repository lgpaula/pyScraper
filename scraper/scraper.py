from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from parser import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db.database import *

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    chrome_options.add_argument("--start-maximized")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_multiple_titles():
    driver = setup_driver()

    try:
        url = "https://www.imdb.com/search/title/?title_type=tv_series"
        driver.get(url)
        time.sleep(1)  # A better approach would be WebDriverWait

        # Remove consent banner
        try:
            bannerButton = driver.find_element(By.CSS_SELECTOR, ".icb-btn.sc-bcXHqe.sc-hLBbgP.sc-ftTHYK.dcvrLS.dufgkr.ecppKW")
            bannerButton.click()
            time.sleep(1)
        except Exception as e:
            print("No consent banner found or click failed:", e)

        # Click "See more" button (maybe multiple times)
        try:
            button = driver.find_element(By.CLASS_NAME, "ipc-see-more__text")
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            # time.sleep(1)
            # button.click()
            # time.sleep(1)
        except Exception as e:
            print("No button found or click failed:", e)

        # with open("page_source.txt", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)

        ul_element = driver.find_element(By.CLASS_NAME, "sc-e22973a9-0")  # Parent <ul>
        movie_items = ul_element.find_elements(By.CLASS_NAME, "ipc-metadata-list-summary-item")
        movies = parse_title_list(movie_items)

        return movies

    finally:
        driver.quit()

def scrape_single_title():
    driver = setup_driver()

    try:
        url = "https://www.imdb.com/title/tt11280740/"
        driver.get(url)
        time.sleep(1)

        # get parent element no.1
        parent1 = driver.find_element(By.CLASS_NAME, "sc-9a2a0028-6")
        # get parent element no.2
        parent2 = driver.find_element(By.XPATH, '//script[@id="__NEXT_DATA__"]')

        title = parse_single_title(parent1, parent2)

        return title

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_single_title()


    # movies = scrape_multiple_titles()
    # create_table()
    # for movie in movies:
    #     insert_title(movie)

    # print(fetch_titles())
