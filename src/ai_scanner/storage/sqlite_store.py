# src/ai_scanner/storage/sqlite_store.py
from __future__ import annotations
import os, sqlite3, time, json
from typing import Any, Dict, Iterable, Optional

class SQLiteStore:
    def __init__(self, db_path: str = "data/scans.db") -> None:
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS scans(
              id INTEGER PRIMARY KEY,
              ts INTEGER NOT NULL,
              target TEXT NOT NULL,
              rc INTEGER NOT NULL,
              stdout TEXT,
              stderr TEXT,
              parsed_json TEXT
            )""")
            con.commit()

    def save(self, target: str, raw: Dict[str, Any], parsed: Optional[Dict[str, Any]] = None) -> None:
        with sqlite3.connect(self.db_path) as con:
            con.execute(
                "INSERT INTO scans(ts,target,rc,stdout,stderr,parsed_json) VALUES(?,?,?,?,?,?)",
                (int(time.time()), target, raw.get("rc", -1), raw.get("stdout",""),
                 raw.get("stderr",""), json.dumps(parsed) if parsed else None)
            )
            con.commit()

    def find_by_target(self, target: str) -> Iterable[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as con:
            cur = con.execute(
                "SELECT ts,target,rc,stdout,stderr,parsed_json FROM scans WHERE target=? ORDER BY ts DESC",
                (target,)
            )
            for ts, tgt, rc, out, err, pj in cur.fetchall():
                yield {"ts": ts, "target": tgt, "rc": rc, "stdout": out, "stderr": err,
                       "parsed": json.loads(pj) if pj else None}
