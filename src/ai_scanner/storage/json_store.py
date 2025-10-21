# src/ai_scanner/storage/json_store.py
from __future__ import annotations
import json, os, time
from typing import Any, Dict, Iterable, Optional

class JSONStore:
    def __init__(self, path: str = "data/scans.jsonl") -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.path = path

    def save(self, target: str, raw: Dict[str, Any], parsed: Optional[Dict[str, Any]] = None) -> None:
        rec = {"ts": int(time.time()), "target": target, "raw": raw, "parsed": parsed}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def load_all(self) -> Iterable[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)

    def find_by_target(self, target: str) -> Iterable[Dict[str, Any]]:
        for rec in self.load_all():
            if rec.get("target") == target:
                yield rec
