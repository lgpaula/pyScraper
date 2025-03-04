import json
import re
from utils import Title
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def parse_title_list(title_div_list):
    try:
        titles = []

        for item in title_div_list:
            name = item.find_element(By.CLASS_NAME, "ipc-title__text").text  # remove position number
            name = re.sub(r'^\d+\.\s', '', name)
            
            id_element = item.find_element(By.CLASS_NAME, "ipc-lockup-overlay")
            href = id_element.get_attribute("href")
            id = href.split("/title/")[1].split("/")[0]

            yearSpan = item.find_elements(By.CLASS_NAME, "sc-d5ea4b9d-7")[0].text

            try:
                rating = item.find_element(By.XPATH, "//span[@class='ipc-rating-star--rating']").text
            except NoSuchElementException:
                rating = ""

            try:
                plot = item.find_element(By.CLASS_NAME, "ipc-html-content-inner-div").text
            except NoSuchElementException:
                plot = ""

            try:
                img_element = item.find_element(By.XPATH, ".//div[contains(@class, 'ipc-media')]/img")
                srcset = img_element.get_attribute("srcset")
                srcset_links = srcset.split(", ")
                last_link = srcset_links[-1].split(" ")[0]
                poster_url = last_link
            except NoSuchElementException:
                poster_url = ""

            try:
                runtime = item.find_elements(By.CLASS_NAME, "sc-d5ea4b9d-7")[1].text
            except IndexError:
                runtime = ""

            try:
                title_type = item.find_element(By.CLASS_NAME, "sc-d5ea4b9d-4").text
            except NoSuchElementException:
                title_type = "Movie"

            curr_title = Title (
                title_id = id,
                title_name = name,
                title_type = title_type,
                year_span = yearSpan,
                rating = rating,
                plot = plot,
                poster_url = poster_url,
                runtime = runtime
            )

            titles.append(curr_title)

        return titles

    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        return []
    except KeyError as e:
        print("Missing expected key in JSON:", e)
        return []


# add unknown stars to dict(id, stars)
# add unknown genres to dict(id, genre)
# add unknown writer to dict(id, writer)
# add unknown company to dict(id, company)

# stars
# writer
# genres
# director
# schedule
# original title
# producer / company

def get_companies(parent2):
    json_text = parent2.get_attribute("innerHTML")

    # Parse the JSON
    data = json.loads(json_text)

    # Extract production companies
    companies = data["props"]["pageProps"]["aboveTheFoldData"]["production"]["edges"]
    company_names = [company["node"]["company"]["companyText"]["text"] for company in companies]

    # Print the company names
    print(company_names)

def parse_single_title(parent1, parent2):
    companies = get_companies(parent2)


