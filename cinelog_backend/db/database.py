import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def run(self, query, params=(), fetch=None, commit=False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            if fetch == "one":
                return cursor.fetchone()
            elif fetch == "all":
                return cursor.fetchall()
    
    # Schema methods (called at startup)
    def create_schema(self):
        self._create_main_table()
        self._create_extras_tables()

    def _create_main_table(self):
        self.run("""
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
            """, commit=True)

    def _create_extras_tables(self):
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

        # Create entity tables
        for table in entity_tables:
            self.run(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id TEXT PRIMARY KEY,
                    name TEXT
                )
            """, commit=True)

        # Create join tables
        for join_table, entity_table in join_tables.items():
            col = entity_table.replace('_table', '')
            self.run(f"""
                CREATE TABLE IF NOT EXISTS {join_table} (
                    title_id TEXT,
                    {col}_id TEXT,
                    PRIMARY KEY (title_id, {col}_id),
                    FOREIGN KEY (title_id) REFERENCES titles_table(title_id),
                    FOREIGN KEY ({col}_id) REFERENCES {entity_table}(id)
                )
            """, commit=True)