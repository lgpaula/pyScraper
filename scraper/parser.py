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

    print(company_names)

def parse_single_title(parent1, parent2, title_id):
    companies = get_companies(parent2)

    # Extract genres
    genre_container = parent1.find_element(By.CLASS_NAME, "ipc-chip-list__scroller")
    genre_elements = genre_container.find_elements(By.TAG_NAME, "a")
    genres = []
    for genre in genre_elements:
        genre_name = genre.text.strip()
        genre_id = genre.get_attribute("href").split("/")[-2]  # Extract unique identifier
        genres.append((genre_name, genre_id))

    print("\nGenres:")
    for name, imdb_id in genres:
        print(f"- {name} (ID: {imdb_id})")

    # Extract creators and stars
    metadata_items = parent1.find_elements(By.CLASS_NAME, "ipc-metadata-list__item")

    stars = []
    writers = []
    creators = []
    directors = []

    # Loop through each metadata item to check its label
    for item in metadata_items:
        try:
            # Find the label (if it exists)
            try:
                label_element = item.find_element(By.CLASS_NAME, "ipc-metadata-list-item__label")
                label_text = label_element.text.strip()
            except NoSuchElementException:
                continue  # Skip if no label is found

            # Find the container holding the names
            try:
                content_container = item.find_element(By.CLASS_NAME, "ipc-metadata-list-item__content-container")
                name_elements = content_container.find_elements(By.TAG_NAME, "a")  # Select all <a> tags inside it

                # Extract name and IMDb ID for all entries
                extracted_data = [
                    (name.text.strip(), name.get_attribute("href").split("/")[-2]) 
                    for name in name_elements if name.text.strip()
                ]
            except NoSuchElementException:
                extracted_data = []  # No names found, set empty list

            # Categorize based on label text
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

    # Print results
    print("\nCreators (TV Shows Only):")
    for name, imdb_id in creators:
        print(f"- {name} (ID: {imdb_id})")

    print("\nDirectors (Movies Only):")
    for name, imdb_id in directors:
        print(f"- {name} (ID: {imdb_id})")

    print("\nWriters (If Available):")
    for name, imdb_id in writers:
        print(f"- {name} (ID: {imdb_id})")

    print("\nStars:")
    for name, imdb_id in stars:
        print(f"- {name} (ID: {imdb_id})")

    # Extract schedule
    try:
        schedule = parent1.find_element(By.CLASS_NAME, "sc-5766672e-2")
    except NoSuchElementException:
        schedule = None

    print("\nSchedule:")
    print(schedule.text if schedule else "Not available")

    # Extract original title
    try:
        original_title = parent1.find_element(By.CLASS_NAME, "sc-ec65ba05-1").text
        original_title = original_title.replace("Original title: ", "").strip()
    except NoSuchElementException:
        original_title = None
    
    print("\nOriginal Title:")
    print(original_title if original_title else "Not available")

