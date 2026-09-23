import requests
import platform
import uuid
import hashlib
import getpass
import json
from typing import Dict, Any, Tuple, Optional

from config import SMARTWEB_BASE_URL, DEFAULT_USER_AGENT

class SmartWebService:
    """
    Integrates the desktop client with the SmartWeb Next.js backend API.
    Endpoints:
    - /api/auth/login
    - /api/software/verify
    - /api/software/results
    - /api/software/version
    - /api/dashboard/history
    """
    DEFAULT_BASE_URL = SMARTWEB_BASE_URL
    LOCAL_BASE_URL = "http://localhost:3000"

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.auth_token: Optional[str] = None
        self.current_user: Dict[str, Any] = {}
        self.session = requests.Session()
        
        # User-Agent must include 'AgeSmartApp' to satisfy originIsTrusted in SmartWeb RBAC middleware
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def set_base_url(self, new_url: str):
        self.base_url = new_url.rstrip("/")

    def get_hardware_fingerprint(self) -> str:
        """
        Generates a consistent SHA-256 hardware identifier for this machine.
        """
        try:
            import winreg
            registry = winreg.HKEY_LOCAL_MACHINE
            address = r"SOFTWARE\Microsoft\Cryptography"
            key = winreg.OpenKey(registry, address, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            
            system = platform.system()
            raw = f"{system}-{machine_guid}"
            return hashlib.sha256(raw.encode("utf-8")).hexdigest()
        except Exception:
            # Fallback if registry access fails
            try:
                raw = f"{platform.system()}-{platform.node()}-{getpass.getuser()}"
                return hashlib.sha256(raw.encode("utf-8")).hexdigest()
            except Exception:
                return hashlib.sha256(b"fallback_device_hash").hexdigest()

    def check_version(self, current_version: str) -> Tuple[bool, str, str]:
        """
        Checks version against GET /api/software/version.
        Returns: (must_update: bool, min_version: str, download_url: str)
        """
        try:
            url = f"{self.base_url}/api/software/version"
            res = self.session.get(url, timeout=8)
            if res.status_code == 200:
                data = res.json()
                min_ver = data.get("minimumVersion", "0.0.0")
                dl_url = data.get("downloadUrl", "")
                
                # Compare versions
                must_update = self._is_version_below(current_version, min_ver)
                return must_update, min_ver, dl_url
        except Exception as e:
            print(f"[SmartWeb] Version check warning: {e}")
            
        return False, current_version, ""

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Calls POST /api/auth/login.
        Returns: (success: bool, message: str)
        """
        try:
            url = f"{self.base_url}/api/auth/login"
            payload = {
                "email": email.strip().lower(),
                "password": password
            }
            res = self.session.post(url, json=payload, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                self.auth_token = data.get("token")
                self.current_user = data.get("user", {})
                
                # Set Bearer token for subsequent calls
                self.session.headers["Authorization"] = f"Bearer {self.auth_token}"
                return True, "Login successful"
            else:
                try:
                    err = res.json().get("error", f"HTTP {res.status_code}")
                except Exception:
                    err = f"Login failed with status {res.status_code}"
                return False, err
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def verify_device(self) -> Tuple[bool, str]:
        """
        Calls POST /api/software/verify with the machine's hardware hash.
        Returns: (success: bool, message: str)
        """
        if not self.auth_token:
            return False, "Not authenticated. Please log in first."
            
        try:
            url = f"{self.base_url}/api/software/verify"
            hw_hash = self.get_hardware_fingerprint()
            payload = {"deviceHash": hw_hash}
            
            res = self.session.post(url, json=payload, timeout=8)
            
            if res.status_code == 200:
                data = res.json()
                return True, data.get("status", "Verified")
            else:
                try:
                    err = res.json().get("error", f"Device verification failed ({res.status_code})")
                except Exception:
                    err = f"Device verification failed with status {res.status_code}"
                return False, err
        except Exception as e:
            return False, f"Device verification error: {str(e)}"

    def submit_result(self, code: str, status: str) -> Tuple[bool, str]:
        """
        Submits verification result to POST /api/software/results.
        Allowed statuses on the website:
        ["SUCCESS", "FAILED", "SUSPICIOUS", "LIVE_CHAT", "IN_REVIEW"]
        """
        if not self.auth_token:
            return False, "No active session token to submit results."
            
        # Normalize status to website standard
        status_map = {
            "APPROVED": "SUCCESS",
            "VERIFIED": "SUCCESS",
            "PASSED": "SUCCESS",
            "REJECTED": "FAILED",
            "ERROR": "FAILED",
            "EXCEPTION": "FAILED",
            "TIMEOUT": "FAILED",
            "SUSPICIOUS": "SUSPICIOUS",
            "LIVE_CHAT": "LIVE_CHAT",
            "IN_REVIEW": "IN_REVIEW"
        }
        clean_status = status_map.get(status.upper().strip(), "FAILED")
        
        # Code must be between 10 and 100 characters per website schema
        clean_code = str(code).strip()
        if len(clean_code) < 10:
            clean_code = clean_code.ljust(10, "_")
        elif len(clean_code) > 100:
            clean_code = clean_code[:100]
            
        try:
            url = f"{self.base_url}/api/software/results"
            payload = {
                "code": clean_code,
                "status": clean_status
            }
            res = self.session.post(url, json=payload, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                return True, data.get("message", "Results received successfully.")
            else:
                try:
                    err = res.json().get("error", f"HTTP {res.status_code}")
                except Exception:
                    err = f"HTTP {res.status_code}"
                return False, err
        except Exception as e:
            return False, f"Failed to submit result to website: {str(e)}"

    def fetch_online_history(self) -> Tuple[bool, list]:
        """
        Fetches user's history from GET /api/dashboard/history.
        """
        if not self.auth_token:
            return False, []
            
        try:
            url = f"{self.base_url}/api/dashboard/history"
            res = self.session.get(url, timeout=15)
            if res.status_code == 200:
                data = res.json()
                records = data.get("submissions") or data.get("history") or []
                return True, records
            return False, []
        except Exception:
            return False, []

    @staticmethod
    def _is_version_below(current: str, minimum: str) -> bool:
        try:
            c_parts = [int(p) for p in str(current).split(".") if p.isdigit()]
            m_parts = [int(p) for p in str(minimum).split(".") if p.isdigit()]
            while len(c_parts) < 3: c_parts.append(0)
            while len(m_parts) < 3: m_parts.append(0)
            return tuple(c_parts) < tuple(m_parts)
        except Exception:
            return False
