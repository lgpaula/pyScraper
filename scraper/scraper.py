# initializes selenium
# loads imdb page
# clicks button
# passes html to parser.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def start_scraping():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Remove if you want to see the browser
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--start-maximized")

    # Use webdriver-manager to automatically install ChromeDriver
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open IMDb search page
        url = "https://www.imdb.com/search/title/?title_type=feature"
        driver.get(url)

        time.sleep(2)  # A better approach would be WebDriverWait

        # Remove consent banner
        try:
            bannerButton = driver.find_element(By.CSS_SELECTOR, ".icb-btn.sc-bcXHqe.sc-hLBbgP.sc-ftTHYK.dcvrLS.dufgkr.ecppKW")
            bannerButton.click()
            time.sleep(3)
        except Exception as e:
            print("No consent banner found or click failed:", e)

        try:
            button = driver.find_element(By.CLASS_NAME, "ipc-see-more__text")
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)
            button.click()
            time.sleep(1)
        except Exception as e:
            print("No button found or click failed:", e)

        # with open("page_source.txt", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)

        # Extract movie titles
        # titles = driver.find_elements(By.id, "__NEXT_DATA__")
        # for title in titles:
        #     print(title.text)

    finally:
        driver.quit()  # Close browser

if __name__ == "__main__":
    start_scraping()
