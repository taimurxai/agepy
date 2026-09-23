import requests
import platform

class TelemetryClient:
    def __init__(self, endpoint="https://telemetry.example.com"):
        self.endpoint = endpoint

    def log_event(self, event_name, metadata=None):
        payload = {
            "event": event_name,
            "os": platform.system(),
            "metadata": metadata or {}
        }
        # try:
        #     requests.post(f"{self.endpoint}/log", json=payload, timeout=5)
        # except:
        #     pass
        print(f"[Telemetry] {event_name}: {metadata}")
