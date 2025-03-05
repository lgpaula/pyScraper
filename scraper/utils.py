from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Title:
    title_id: str
    title_name: str
    year_span: str
    rating: str
    plot: str
    poster_url: str
    runtime: str
    title_type: str = "Movie"
    genres: List[str] = None # get later
    original_title: str = None # get later
    stars: List[str] = None
    writers: str = None
    directors: str = None
    creators: str = None
    schedule: str = None
    companies: str = None

# dicts or nosql?
dict_id_stars = {}
dict_id_genre = {}
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