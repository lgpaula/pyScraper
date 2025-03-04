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

dict_id_stars = {}
dict_id_genre = {}
dict_id_writer = {}
dict_id_company = {}
dict_id_creator = {}
dict_id_director = {}