import os
import sys
from pathlib import Path

# Application Metadata
APP_NAME = "AgeSmart Enterprise"
APP_VERSION = "2026.8.6"
BUILD_DATE = "2026-09-22"
DEFAULT_USER_AGENT = "AgeSmartApp/2.0.0 (Windows NT 10.0; Win64; x64)"

# Default Production Endpoints
SMARTWEB_BASE_URL = os.environ.get("SMARTWEB_URL", "https://smart-web-blue.vercel.app")
AGESMART_BASE_URL = os.environ.get("AGESMART_URL", "https://agesmart.eu")
IMAGE_PROCESSOR_URL = os.environ.get("IMAGE_PROCESSOR_URL", "https://image-processor.agesmart.eu")

# Safe Windows Storage Paths in %LOCALAPPDATA%
def get_base_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base = Path(local_app_data) / "AgeSmart"
    else:
        base = Path.home() / ".agesmart"
    base.mkdir(parents=True, exist_ok=True)
    return base

DATA_DIR = get_base_data_dir()

LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

TEMP_DIR = DATA_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

EXPORTS_DIR = DATA_DIR / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = DATA_DIR / "verification_history.json"
LOG_FILE = LOGS_DIR / "app.log"

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller bundled apps.
    """
    if hasattr(sys, "_MEIPASS"):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
