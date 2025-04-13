import sqlite3
from utils import Title

# Database setup
DB_NAME = "cinelog.db"

def create_table():
    """Creates the 'titles_table' table if it does not exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS titles_table (
                title_id TEXT PRIMARY KEY,
                title_name TEXT,
                poster_url TEXT,
                year_start INTEGER,
                year_end INTEGER,
                rating REAL,
                plot TEXT,
                runtime TEXT,
                title_type TEXT DEFAULT 'Movie',
                genres TEXT,
                original_title TEXT,
                stars TEXT,
                writers TEXT,
                directors TEXT,
                creators TEXT,
                schedule TEXT,
                companies TEXT,
                updated BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()

def title_exists(title_id: str) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM titles_table WHERE title_id = ?", (title_id,))
        return cursor.fetchone() is not None

def insert_title(title: Title):
    if not title_exists(title.title_id):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO titles_table (title_id, title_name, title_type, poster_url) 
                            VALUES (?, ?, ?, ?)""", (title.title_id, title.title_name, title.title_type, title.poster_url))
            conn.commit()
            print(f"Inserted: {title.title_id} - {title.title_name}")
    else:
        print(f"Skipped (already exists): {title.title_id} - {title.title_name}")

def fetch_titles():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM titles_table")
        return cursor.fetchall()

def update_title(title_id: str, title: Title):
    if not title_exists(title_id):
        print(f"Title ID {title_id} not found. Cannot update.")
        return

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE titles_table 
            SET year_start = ?,
                year_end = ?,
                rating = ?,
                plot = ?,
                runtime = ?,
                genres = ?,
                original_title = ?,
                stars = ?,
                writers = ?,
                directors = ?,
                creators = ?,
                companies = ?,
                schedule = ?,
                updated = ?
            WHERE title_id = ?
        """, (
            title.year_start,
            title.year_end,
            title.rating,
            title.plot,
            title.runtime,
            ",".join([g[0] for g in title.genres]) if title.genres else None,
            title.original_title,
            ",".join([s[0] for s in title.stars]) if title.stars else None,
            ",".join([w[0] for w in title.writers]) if title.writers else None,
            ",".join([d[0] for d in title.directors]) if title.directors else None,
            ",".join([c[0] for c in title.creators]) if title.creators else None,
            ",".join([c[0] for c in title.companies]) if title.companies else None,
            title.schedule,
            1,
            title_id
        ))
        conn.commit()
        print(f"Updated: {title_id}")
        print_title(title_id)

def print_title(id):
    """Prints the title with the given title_id."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM titles_table WHERE title_id = ?", (id,))
        title = cursor.fetchone()
        if title:
            print(title)
        else:
            print(f"Title ID {id} not found.")
