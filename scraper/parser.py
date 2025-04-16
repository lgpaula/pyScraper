import json
import re
from utils import *
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from db.database import update_title

def parse_title_list(title_div_list):
    try:
        titles = []

        for item in title_div_list:
            name = item.find_element(By.CLASS_NAME, XPaths.title_name).text
            name = re.sub(r'^\d+\.\s', '', name)
            
            id_element = item.find_element(By.CLASS_NAME, XPaths.title_id)
            href = id_element.get_attribute("href")
            id = href.split("/title/")[1].split("/")[0]

            try:
                img_element = item.find_element(By.XPATH, XPaths.title_poster)
                srcset = img_element.get_attribute("srcset")
                srcset_links = srcset.split(", ")
                last_link = srcset_links[-1].split(" ")[0]
                poster_url = last_link
                # update link's ending so it's bigger
                # ex:
                # https://m.media-amazon.com/images/M/MV5BYzFjMzNjOTktNDBlNy00YWZhLWExYTctZDcxNDA4OWVhOTJjXkEyXkFqcGc@._V1_QL75_UX280_CR0,0,280,414_.jpg
                # to
                # https://m.media-amazon.com/images/M/MV5BYzFjMzNjOTktNDBlNy00YWZhLWExYTctZDcxNDA4OWVhOTJjXkEyXkFqcGc@._V1_QL75_UX560_CR0,0,560,828_.jpg
            except NoSuchElementException:
                poster_url = ""

            try:
                title_type = item.find_element(By.CLASS_NAME, XPaths.title_type).text
            except NoSuchElementException:
                title_type = "Movie"

            curr_title = Title (
                title_id = id,
                title_name = name,
                title_type = title_type,
                poster_url = poster_url
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

def get_companies(parent2):
    json_text = parent2.get_attribute("innerHTML")
    data = json.loads(json_text)

    companies = data["props"]["pageProps"]["aboveTheFoldData"]["production"]["edges"]
    company_info = [
        (company["node"]["company"]["companyText"]["text"], company["node"]["company"]["id"])
        for company in companies
    ]

    return company_info

def get_genres(parent1):
    genre_container = parent1.find_element(By.CLASS_NAME, XPaths.title_genres)
    genre_elements = genre_container.find_elements(By.TAG_NAME, "a")
    genres = []
    for genre in genre_elements:
        genre_name = genre.text.strip()
        genre_id = genre.get_attribute("href").split("/")[-2]  # Extract unique identifier
        genres.append((genre_name, genre_id))

    return genres

def get_original_title(parent2):
    json_text = parent2.get_attribute("innerHTML")
    data = json.loads(json_text)

    original_title = data["props"]["pageProps"]["aboveTheFoldData"]["originalTitleText"]["text"]
    return original_title

def get_year_start(parent2):
    json_text = parent2.get_attribute("innerHTML")
    data = json.loads(json_text)

    year_start = data["props"]["pageProps"]["aboveTheFoldData"]["releaseYear"]["year"]
    return year_start

def get_year_end(parent2):
    json_text = parent2.get_attribute("innerHTML")
    data = json.loads(json_text)

    year_end = data["props"]["pageProps"]["aboveTheFoldData"]["releaseYear"]["endYear"]
    return year_end

def get_rating(parent2):
    json_text = parent2.get_attribute("innerHTML")
    data = json.loads(json_text)

    rating = data["props"]["pageProps"]["aboveTheFoldData"]["ratingsSummary"]["aggregateRating"]
    return rating

def get_plot(parent2):
    json_text = parent2.get_attribute("innerHTML")
    data = json.loads(json_text)

    plot = data["props"]["pageProps"]["aboveTheFoldData"]["plot"]["plotText"]["plainText"]
    return plot

def get_runtime(parent2):
    json_text = parent2.get_attribute("innerHTML")
    data = json.loads(json_text)

    try:
        runtime_data = data.get("props", {}) \
                           .get("pageProps", {}) \
                           .get("aboveTheFoldData", {}) \
                           .get("runtime") or {}

        displayable_property = runtime_data.get("displayableProperty")
        if displayable_property:
            return displayable_property["value"]["plainText"]
        else:
            return ""
    except (KeyError, TypeError, AttributeError):
        return ""

def get_season_count(parent2, year_end):
    json_text = parent2.get_attribute("innerHTML")
    data = json.loads(json_text)

    canHaveEpisodes = data["props"]["pageProps"]["aboveTheFoldData"]["canHaveEpisodes"]

    if not canHaveEpisodes and not year_end: return ""

    seasons = data["props"]["pageProps"]["mainColumnData"]["episodes"]["seasons"]
    seasonCount = seasonCount = len(seasons)

    return seasonCount

def parse_single_title(parent1, parent2, title_id):
    companies = get_companies(parent2)
    genres = get_genres(parent1)
    original_title = get_original_title(parent2)
    year_start = get_year_start(parent2)
    year_end = get_year_end(parent2)
    rating = get_rating(parent2)
    plot = get_plot(parent2)
    runtime = get_runtime(parent2)
    season_count = get_season_count(parent2, year_end)

    # Extract creators and stars
    metadata_items = parent1.find_elements(By.CLASS_NAME, XPaths.title_metadata)

    stars = []
    writers = []
    creators = []
    directors = []

    for item in metadata_items:
        try:
            try:
                label_element = item.find_element(By.CLASS_NAME, XPaths.title_metadata_label)
                label_text = label_element.text.strip()
            except NoSuchElementException:
                continue

            try:
                content_container = item.find_element(By.CLASS_NAME, XPaths.title_metadata_container)
                name_elements = content_container.find_elements(By.TAG_NAME, "a")

                extracted_data = [
                    (name.text.strip(), name.get_attribute("href").split("/")[-2]) 
                    for name in name_elements if name.text.strip()
                ]
            except NoSuchElementException:
                extracted_data = []

            if "Creator" in label_text:
                creators.extend(extracted_data)
            elif "Director" in label_text:
                directors.extend(extracted_data)
            elif "Writer" in label_text:
                writers.extend(extracted_data)
            elif "Stars" in label_text:
                stars.extend(extracted_data)

        except Exception as e:
            print(f"Error processing item: {e}")

    #update title in database
    curr_title = Title (
        title_id = title_id,
        year_start = year_start,
        year_end = year_end,
        rating = rating,
        plot = plot,
        runtime = runtime,
        genres = genres,
        original_title = original_title,
        stars = stars,
        writers = writers,
        directors = directors,
        creators = creators,
        companies = companies,
        season_count = season_count,
    )

    update_title(title_id, curr_title)