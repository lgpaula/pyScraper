import json
from .database import Database
from data_scraper.utils import Title

class TitleRepository:
    def __init__(self, db: Database):
        self.db = db

    # --- Helpers ---
    def exists(self, title_id: str) -> bool:
        return self.db.run(
            "SELECT 1 FROM titles_table WHERE title_id = ?",
            (title_id,), fetch="one"
        ) is not None

    def fetch_all(self):
        return self.db.run("SELECT * FROM titles_table", fetch="all")

    def fetch_one(self, title_id: str):
        return self.db.run(
            "SELECT * FROM titles_table WHERE title_id = ?",
            (title_id,), fetch="one"
        )

    # --- Insert / Update ---
    def insert(self, title: Title):
        if self.exists(title.title_id):
            # scrape season_count and eps and update
            self.update_created_on(title.title_id)
            print(f"Skipped (already exists): {title.title_id} - {title.title_name}")
            return False
        self.db.run(
            """INSERT INTO titles_table (title_id, title_name, title_type, poster_url)
               VALUES (?, ?, ?, ?)""",
            (title.title_id, title.title_name, title.title_type, title.poster_url),
            commit=True
        )
        return True

    def update_created_on(self, title_id: str):
        self.db.run(
            """UPDATE titles_table
               SET created_on = strftime('%Y-%m-%d %H:%M', 'now')
               WHERE title_id = ?""",
            (title_id,), commit=True
        )

    def update(self, title_id: str, title: Title):
        if not self.exists(title_id):
            raise ValueError(f"Title {title_id} does not exist")

        self.db.run("""
            UPDATE titles_table 
            SET year_start=?, year_end=?, rating=?, plot=?, runtime=?,
                original_title=?, season_count=?, updated=1
            WHERE title_id=?""",
            (title.year_start, title.year_end, title.rating, title.plot,
             title.runtime, title.original_title, title.season_count, title_id),
            commit=True
        )

        # Update relations
        self._upsert_relations(title_id, "genres_table", title.genres)
        self._upsert_relations(title_id, "cast_table", title.stars)
        self._upsert_relations(title_id, "writers_table", title.writers)
        self._upsert_relations(title_id, "creators_table", title.creators)
        self._upsert_relations(title_id, "directors_table", title.directors)
        self._upsert_relations(title_id, "companies_table", title.companies)

    def set_schedule(self, title_id: str, dates: list):
        self.db.run(
            "UPDATE titles_table SET schedule_list = ? WHERE title_id = ?",
            (json.dumps(dates), title_id), commit=True
        )

    # --- Private helpers ---
    def _upsert_relations(self, title_id: str, table_name: str, entries):
        self._smart_upsert_extras(table_name, entries)
        self._update_title_relations(title_id, table_name, entries)

    def _smart_upsert_extras(self, table_name: str, entries):
        for name, entry_id in entries:
            result = self.db.run(
                f"SELECT name FROM {table_name} WHERE id = ?", (entry_id,), fetch="one"
            )
            if result is None:
                self.db.run(
                    f"INSERT INTO {table_name} (id, name) VALUES (?, ?)",
                    (entry_id, name), commit=True
                )
            elif result[0] != name:
                self.db.run(
                    f"UPDATE {table_name} SET name = ? WHERE id = ?",
                    (name, entry_id), commit=True
                )

    def _update_title_relations(self, title_id: str, table_name: str, entries):
        join_tables = {
            'genres_table': 'title_genre',
            'cast_table': 'title_cast',
            'writers_table': 'title_writer',
            'creators_table': 'title_creator',
            'directors_table': 'title_director',
            'companies_table': 'title_company'
        }
        join_table = join_tables[table_name]
        col = table_name.replace('_table', '')

        # Clear old relations
        self.db.run(
            f"DELETE FROM {join_table} WHERE title_id = ?",
            (title_id,), commit=True
        )

        # Insert new ones
        for _, entry_id in entries:
            self.db.run(
                f"""INSERT OR IGNORE INTO {join_table} (title_id, {col}_id)
                    VALUES (?, ?)""",
                (title_id, entry_id), commit=True
            )

    def get_season_count(self, title_id):
        return self.db.run("SELECT season_count FROM titles_table WHERE title_id = ?", (title_id,), fetch="one")
        
    def add_schedule_to_title(self, title_id, dates):
        self.db.run("UPDATE titles_table SET schedule_list = ? WHERE title_id = ?",
                (json.dumps(dates), title_id), commit=True)
        
    def get_all_items(self, table: str):
        # Check if the table exists
        if self.exists(table) is None:
            return []

        # Fetch id and name
        rows = self.db.run(
            f"SELECT id, name FROM {table}",
            fetch="all"
        )

        # Convert rows to list of dicts
        return [{"Id": str(row["id"]), "Name": str(row["name"])} for row in rows]
    
    def get_all_lists(self):
        # Check if there are lists
        check = self.db.run("SELECT name FROM sqlite_master WHERE type='table' AND name='lists_table';", fetch="all")
        if check is None:
            return []

        # Fetch lists
        lists = self.db.run("SELECT name, uuid FROM lists_table;", fetch="all")

        # Convert
        return [{"name": list["name"], "uuid": list["uuid"]} for list in lists]
