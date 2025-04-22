from dataclasses import dataclass

@dataclass
class Title:
    title_id: str
    title_name: str = ""
    poster_url: str = ""
    year_start: int = ""
    year_end: int = ""
    rating: float = ""
    plot: str = ""
    runtime: str = ""
    title_type: str = "Movie"
    genres: str = ""
    original_title: str = ""
    stars: str = ""
    writers: str = ""
    directors: str = ""
    creators: str = ""
    companies: str = ""
    season_count: str = ""
    schedule_list: str = ""

# x-path & class strings
@dataclass(frozen = True)
class XPaths:
    banner_element = ".icb-btn.sc-bcXHqe.sc-hLBbgP.sc-ftTHYK.dcvrLS.dufgkr.ecppKW"
    see_more_button = "ipc-see-more__text"
    scroll_into_view = "arguments[0].scrollIntoView(true);"
    multi_title_parent = "sc-e22973a9-0"
    multi_title_item = "ipc-metadata-list-summary-item"
    single_title_parent_1 = "ipc-page-section--bp-xs"
    single_title_parent_2 = '//script[@id="__NEXT_DATA__"]'
    title_name = "ipc-title__text"
    title_id = "ipc-lockup-overlay"
    title_poster = ".//div[contains(@class, 'ipc-media')]/img"
    title_type = "dli-title-type-data"
    title_genres = "ipc-chip-list__scroller"
    title_metadata = "ipc-metadata-list__item"
    title_metadata_label = "ipc-metadata-list-item__label"
    title_metadata_container = "ipc-metadata-list-item__content-container"