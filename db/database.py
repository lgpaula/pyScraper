import json
import sqlite3
import scraper
from utils import Title

# Database setup
def get_data_dir():
    if os.name == 'nt':  # Windows
        return Path(os.getenv('LOCALAPPDATA')) / 'CineLog'
    elif os.name == 'posix':
        if sys.platform == 'darwin':  # macOS
            return Path.home() / 'Library' / 'Application Support' / 'CineLog'
        else:  # Linux
            return Path.home() / '.local' / 'share' / 'CineLog'

    return None

DB_NAME = get_data_dir() + "cinelog.db"
data_dir.mkdir(parents=True, exist_ok=True)

def create_table():
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
                original_title TEXT,
                season_count TEXT,
                schedule_list TEXT,
                created_on TEXT DEFAULT (strftime('%Y-%m-%d %H:%M', 'now')),
                updated BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()

    create_extras_tables()

def create_extras_tables():
    entity_tables = [
        'genres_table',
        'cast_table',
        'writers_table',
        'creators_table',
        'directors_table',
        'companies_table'
    ]

    join_tables = {
        'title_genre': 'genres_table',
        'title_cast': 'cast_table',
        'title_writer': 'writers_table',
        'title_creator': 'creators_table',
        'title_director': 'directors_table',
        'title_company': 'companies_table'
    }

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Create entity tables
        for table in entity_tables:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id TEXT PRIMARY KEY,
                    name TEXT
                )
            """)

        # Create join tables
        for join_table, entity_table in join_tables.items():
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {join_table} (
                    title_id TEXT,
                    {entity_table.replace('_table', '')}_id TEXT,
                    PRIMARY KEY (title_id, {entity_table.replace('_table', '')}_id),
                    FOREIGN KEY (title_id) REFERENCES titles_table(title_id),
                    FOREIGN KEY ({entity_table.replace('_table', '')}_id) REFERENCES {entity_table}(id)
                )
            """)

        conn.commit()

def title_exists(title_id: str) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM titles_table WHERE title_id = ?", (title_id,))
        return cursor.fetchone() is not None

    return None

def insert_title(title: Title):
    if not title_exists(title.title_id):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO titles_table (title_id, title_name, title_type, poster_url) 
                            VALUES (?, ?, ?, ?)""", (title.title_id, title.title_name, title.title_type, title.poster_url))
            conn.commit()
            print(f"Inserted: {title.title_id} - {title.title_name}")
        return True
    else:
        # scrape season_count and eps
        update_title_date(title.title_id)
        print(f"Skipped (already exists): {title.title_id} - {title.title_name}")
        return False

def update_title_date(title_id: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE titles_table
            SET created_on = strftime('%Y-%m-%d %H:%M', 'now')
            WHERE title_id = ?""", (title_id,))
        conn.commit()
        print(f"Updated 'created_on' for: {title_id}")

def fetch_titles():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM titles_table")
        return cursor.fetchall()

    return None

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
                original_title = ?,
                season_count = ?,
                updated = ?
            WHERE title_id = ?
        """, (
            title.year_start,
            title.year_end,
            title.rating,
            title.plot,
            title.runtime,
            title.original_title,
            title.season_count,
            1,
            title_id
        ))
        conn.commit()
        print(f"Updated: {title_id}")
        print_title(title_id)

        smart_upsert_extras("genres_table", title.genres)
        update_title_relations(title_id, "genres_table", title.genres)

        smart_upsert_extras("cast_table", title.stars)
        update_title_relations(title_id, "cast_table", title.stars)

        smart_upsert_extras("writers_table", title.writers)
        update_title_relations(title_id, "writers_table", title.writers)

        smart_upsert_extras("creators_table", title.creators)
        update_title_relations(title_id, "creators_table", title.creators)

        smart_upsert_extras("directors_table", title.directors)
        update_title_relations(title_id, "directors_table", title.directors)

        smart_upsert_extras("companies_table", title.companies)
        update_title_relations(title_id, "companies_table", title.companies)

def smart_upsert_extras(table_name: str, entries: list[list[str]]):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        for name, entry_id in entries:
            cursor.execute(
                f"SELECT name FROM {table_name} WHERE id = ?",
                (entry_id,)
            )
            result = cursor.fetchone()

            if result is None:
                cursor.execute(
                    f"INSERT INTO {table_name} (id, name) VALUES (?, ?)",
                    (entry_id, name)
                )
            elif result[0] != name:
                cursor.execute(
                    f"UPDATE {table_name} SET name = ? WHERE id = ?",
                    (name, entry_id)
                )
        conn.commit()

def update_title_relations(title_id: str, table_name: str, entries: list[list[str]]):
    """Insert title-to-entity relations in join tables."""
    join_tables = {
        'genres_table': 'title_genre',
        'cast_table': 'title_cast',
        'writers_table': 'title_writer',
        'creators_table': 'title_creator',
        'directors_table': 'title_director',
        'companies_table': 'title_company'
    }

    join_table = join_tables[table_name]
    column = f"{table_name.replace('_table', '')}_id"

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM {join_table} WHERE title_id = ?", (title_id,))

        for name, entry_id in entries:
            cursor.execute(f"""
                INSERT OR IGNORE INTO {join_table} (title_id, {column})
                VALUES (?, ?)
            """, (title_id, entry_id))
        conn.commit()

def print_title(title_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM titles_table WHERE title_id = ?", (title_id,))
        title = cursor.fetchone()
        if title:
            print(title)
        else:
            print(f"Title ID {title_id} not found.")

def get_season_count(title_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT season_count FROM titles_table WHERE title_id = ?", (title_id,))
        count = cursor.fetchone()
        return count
    
def add_schedule_to_title(title_id, dates):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE titles_table SET schedule_list = ? WHERE title_id = ?",
            (json.dumps(dates), title_id)
        )
        conn.commit()