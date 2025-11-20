import sqlite3
import json
import time
from typing import Optional, Dict, Any

DB_PATH = "ai_test_lab.db"

class Storage:
    def __init__(self, path: Optional[str] = None):
        self.path = path or DB_PATH
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        c = self._conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                session_id TEXT,
                model TEXT,
                prompt TEXT,
                response TEXT,
                tokens_in INTEGER,
                tokens_out INTEGER,
                latency_ms REAL,
                metadata TEXT,
                created_at REAL
            )
            """
        )
        self._conn.commit()

    def insert_log(self, session_id: str, model: str, prompt: str, response: str,
                   tokens_in: int, tokens_out: int, latency_ms: float,
                   metadata: Optional[Dict[str, Any]] = None):
        c = self._conn.cursor()
        metadata_json = json.dumps(metadata or {})
        created_at = time.time()
        c.execute(
            "INSERT INTO logs (session_id, model, prompt, response, tokens_in, tokens_out, latency_ms, metadata, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (session_id, model, prompt, response, tokens_in, tokens_out, latency_ms, metadata_json, created_at)
        )
        self._conn.commit()

    def query_logs(self, limit: int = 100):
        c = self._conn.cursor()
        c.execute("SELECT id, session_id, model, prompt, response, tokens_in, tokens_out, latency_ms, metadata, created_at FROM logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "session_id": r[1],
                "model": r[2],
                "prompt": r[3],
                "response": r[4],
                "tokens_in": r[5],
                "tokens_out": r[6],
                "latency_ms": r[7],
                "metadata": json.loads(r[8] or "{}"),
                "created_at": r[9]
            })
        return results
