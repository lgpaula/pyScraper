import sqlite3
from utils import Title

# Database setup
DB_NAME = "titles.db"

def create_table():
    """Creates the 'titles' table if it does not exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS titles (
                title_id TEXT PRIMARY KEY,
                title_name TEXT,
                year_span TEXT,
                rating TEXT,
                plot TEXT,
                poster_url TEXT,
                runtime TEXT,
                title_type TEXT DEFAULT 'Movie',
                genres TEXT,  -- Stored as CSV, parsed later
                original_title TEXT
            )
        """)
        conn.commit()

def title_exists(title_id: str) -> bool:
    """Checks if a title with the given title_id exists in the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM titles WHERE title_id = ?", (title_id,))
        return cursor.fetchone() is not None

def insert_title(title: Title):
    """Inserts a title only if its title_id is not already present."""
    if not title_exists(title.title_id):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO titles (title_id, title_name, year_span, rating, plot, poster_url, runtime, title_type, genres, original_title) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                (title.title_id, title.title_name, title.year_span, title.rating, title.plot, title.poster_url, title.runtime, title.title_type, ",".join(title.genres) 
                    if title.genres else None, title.original_title))
            conn.commit()
            print(f"Inserted: {title.title_id} - {title.title_name}")
    else:
        print(f"Skipped (already exists): {title.title_id} - {title.title_name}")

def fetch_titles():
    """Fetches all titles from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM titles")
        return cursor.fetchall()