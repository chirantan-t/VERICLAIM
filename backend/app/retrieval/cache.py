import json
import os
import sqlite3
from typing import Optional, Dict, Any


class SQLiteCache:
    """A simple SQLite-backed cache for retrieval results to prevent repeated API calls."""

    def __init__(self, db_path: str = "data/retrieval_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    type TEXT
                )
                """
            )
            conn.commit()

    def get(self, key: str, type_ns: str = "general") -> Optional[Dict[str, Any]]:
        full_key = f"{type_ns}:{key}"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM cache WHERE key = ?", (full_key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    def set(self, key: str, value: Dict[str, Any], type_ns: str = "general"):
        full_key = f"{type_ns}:{key}"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO cache (key, value, type) VALUES (?, ?, ?)",
                (full_key, json.dumps(value), type_ns),
            )
            conn.commit()
