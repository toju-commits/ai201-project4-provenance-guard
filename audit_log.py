import json
import os
from datetime import datetime, timezone
from typing import Dict, List


LOG_FILE = "audit_log.json"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_log() -> List[Dict]:
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_log(entries: List[Dict]) -> None:
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(entries, file, indent=2)


def add_log_entry(entry: Dict) -> Dict:
    entries = load_log()
    entry["timestamp"] = utc_timestamp()
    entries.append(entry)
    save_log(entries)
    return entry


def get_recent_entries(limit: int = 20) -> List[Dict]:
    entries = load_log()
    return entries[-limit:]


def find_content(content_id: str) -> Dict | None:
    entries = load_log()

    for entry in reversed(entries):
        if entry.get("content_id") == content_id and entry.get("event_type") == "submission":
            return entry

    return None