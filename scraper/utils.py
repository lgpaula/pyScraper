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
    writer: str = None
    director: str = None
    schedule: str = None
    company: str = None