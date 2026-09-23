import json
import os
import uuid
from datetime import datetime

class HistoryEntry:
    def __init__(self, run_id, timestamp, status, details):
        self.run_id = run_id
        self.timestamp = timestamp
        self.status = status
        self.details = details

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "details": self.details
        }

from config import HISTORY_FILE, EXPORTS_DIR

class HistoryService:
    def __init__(self, file_path=None):
        self.file_path = str(file_path or HISTORY_FILE)
        self.history = self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save(self):
        temp_path = f"{self.file_path}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
            if os.path.exists(self.file_path):
                os.replace(temp_path, self.file_path)
            else:
                os.rename(temp_path, self.file_path)
        except Exception:
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass

    def add_entry(self, status, details):
        entry = HistoryEntry(
            run_id=uuid.uuid4().hex,
            timestamp=datetime.now().isoformat(),
            status=status,
            details=details
        )
        entry_dict = entry.to_dict()
        self.history.insert(0, entry_dict)
        self._save()
        
        # Export to CSV in exports directory
        try:
            from utilities.export_helper import ExportHelper
            csv_path = str(EXPORTS_DIR / "verification_history.csv")
            ExportHelper.export_to_csv(entry_dict, csv_path)
        except Exception:
            pass

    def get_history(self):
        return self.history
