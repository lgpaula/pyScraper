from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Title:
    title_id: str
    title_name: str = ""
    poster_url: str = ""
    year_start: int = ""
    year_end: int = ""
    rating: float = ""
    plot: str = ""
    runtime: str = None
    title_type: str = "Movie"
    genres: List[str] = ""
    original_title: str = ""
    stars: List[str] = ""
    writers: str = ""
    directors: str = ""
    creators: str = ""
    schedule: str = ""
    companies: str = ""

# dicts or nosql?
dict_id_stars = {}
dict_id_writer = {}
dict_id_company = {}
dict_id_creator = {}
dict_id_director = {}

# x-path & class strings
@dataclass(frozen = True)
class XPaths:
    banner_element = ".icb-btn.sc-bcXHqe.sc-hLBbgP.sc-ftTHYK.dcvrLS.dufgkr.ecppKW"
    see_more_button = "ipc-see-more__text"
    scroll_into_view = "arguments[0].scrollIntoView(true);"
    multi_title_parent = "sc-e22973a9-0"
    multi_title_item = "ipc-metadata-list-summary-item"
    single_title_parent_1 = "sc-9a2a0028-0"
    single_title_parent_2 = '//script[@id="__NEXT_DATA__"]'
    title_name = "ipc-title__text"
    title_id = "ipc-lockup-overlay"
    title_year = "hvVhYi" #sc-e8bccfea-7
    title_rating = "ipc-rating-star--rating"
    title_plot = "ipc-html-content-inner-div"
    title_poster = ".//div[contains(@class, 'ipc-media')]/img"
    title_runtime = "hvVhYi" #sc-e8bccfea-7
    title_type = "sc-d5ea4b9d-4"
    title_genres = "ipc-chip-list__scroller"
    title_metadata = "ipc-metadata-list__item"
    title_metadata_label = "ipc-metadata-list-item__label"
    title_metadata_container = "ipc-metadata-list-item__content-container"
    title_schedule = "sc-5766672e-2"
    title_original_title = "sc-ec65ba05-1"