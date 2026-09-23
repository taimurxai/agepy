import requests
import json
import logging
from typing import Dict, Any, Optional

class ApiEndpoints:
    IMAGE_ORIGINAL_UPLOAD = "https://image-processor.agesmart.eu/process/upload_age_smart_image_original"
    IMAGE_ALTERED_UPLOAD = "https://image-processor.agesmart.eu/process/upload_age_smart_image_altered"
    VIDEO_UPLOAD = "https://image-processor.agesmart.eu/process/upload_age_smart_video"

    SUBMIT_DOB = "https://agesmart.eu/verification/submitDob"
    SUBMIT_DOCUMENT = "https://agesmart.eu/verification/submitDocument"
    SUBMIT_SELFIE = "https://agesmart.eu/verification/submitSelfie"
    SUBMIT_VIDEO = "https://agesmart.eu/verification/submitVideo"

    @staticmethod
    def verification_session(token: str) -> str:
        return f"https://agesmart.eu/verification/{token}"

    @staticmethod
    def verification_status(token: str) -> str:
        return f"https://agesmart.eu/verification/status/{token}"


DEFAULT_IPHONE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1"

class AgeSmartApiClient:
    def __init__(self, proxy: Optional[str] = None, user_agent: Optional[str] = None):
        self.session = requests.Session()
        
        # Apply authentic Apple iPhone Safari browser headers
        ua = user_agent or DEFAULT_IPHONE_USER_AGENT
        self.session.headers.update({
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "sec-ch-ua": "",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1"
        })
        
        if proxy:
            self.session.proxies.update({
                "http": proxy,
                "https": proxy
            })
            
        self.csrf_token = None
        self.csrf_header = None
        self.is_complete = False
        self.logger = logging.getLogger(__name__)

    def set_user_agent(self, user_agent: str):
        if user_agent:
            self.session.headers["User-Agent"] = user_agent

    def initialize_session(self, token: str) -> bool:
        try:
            url = ApiEndpoints.verification_session(token)
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            
            # Simple CSRF extraction (assuming standard meta/input tags)
            html = resp.text
            import re
            csrf_token_match = re.search(r'name="_csrf"\s+content="([^"]+)"', html) or re.search(r'name="_csrf"\s+value="([^"]+)"', html)
            csrf_header_match = re.search(r'name="_csrf_header"\s+content="([^"]+)"', html)
            
            if csrf_token_match and csrf_header_match:
                self.csrf_token = csrf_token_match.group(1)
                self.csrf_header = csrf_header_match.group(1)
                self.is_complete = True
                return True
            else:
                self.logger.error("Failed to extract CSRF tokens from session HTML")
                return False
        except Exception as e:
            self.logger.error(f"Failed to initialize session: {e}")
            return False

    def upload_image(self, file_path: str, image_type: str, token: str, filename_hint: str = "") -> Dict[str, Any]:
        url = ApiEndpoints.IMAGE_ORIGINAL_UPLOAD if "ORIGINAL" in image_type.upper() else ApiEndpoints.IMAGE_ALTERED_UPLOAD
        
        try:
            import os
            import random
            
            # Use canonical Apple iOS upload filename (e.g. IMG_5412.JPG)
            upload_name = filename_hint if filename_hint else f"IMG_{random.randint(1000, 9999)}.JPG"
            
            with open(file_path, "rb") as f:
                files = {
                    "file": (upload_name, f, "image/jpeg")
                }
                data = {
                    "type": image_type,
                    "token": token
                }
                if filename_hint:
                    data["filename"] = filename_hint
                else:
                    data["filename"] = upload_name
                    
                resp = self.session.post(url, files=files, data=data, timeout=30)
                resp.raise_for_status()
                
                return {
                    "success": True,
                    "response": resp.json(),
                    "file_name": resp.json().get("UploadedFileName", "")
                }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Image upload network failed: {e}")
            return {"success": False, "error": f"Network Error: {e}"}
        except Exception as e:
            self.logger.error(f"Image upload failed: {e}")
            return {"success": False, "error": str(e)}

    def upload_video(self, file_path: str, token: str, length_seconds: float) -> Dict[str, Any]:
        try:
            import os
            import random
            
            # Use canonical Apple iOS upload filename (e.g. IMG_5413.MOV)
            upload_name = f"IMG_{random.randint(1000, 9999)}.MOV"
            
            with open(file_path, "rb") as f:
                files = {
                    "file": (upload_name, f, "video/mp4")
                }
                data = {
                    "type": "VIDEO",
                    "token": token,
                    "video_length": f"{length_seconds:.2f}",
                    "timecodes": "[]",
                    "filename": upload_name
                }
                
                resp = self.session.post(ApiEndpoints.VIDEO_UPLOAD, files=files, data=data, timeout=45)
                resp.raise_for_status()
                
                return {
                    "success": True,
                    "response": resp.json(),
                    "file_name": resp.json().get("UploadedFileName", "")
                }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Video upload network failed: {e}")
            return {"success": False, "error": f"Network Error: {e}"}
        except Exception as e:
            self.logger.error(f"Video upload failed: {e}")
            return {"success": False, "error": str(e)}

    def _submit_step(self, url: str, data: Dict[str, str]) -> Dict[str, Any]:
        if self.is_complete and self.csrf_header and self.csrf_token:
            self.session.headers.update({self.csrf_header: self.csrf_token})
            
        try:
            resp = self.session.post(url, data=data, timeout=30)
            resp.raise_for_status()
            js = resp.json()
            success = js.get("success", False)
            return {
                "success": success,
                "error": "" if success else js.get("body", "Unknown error")
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Submit step {url} network failed: {e}")
            return {"success": False, "error": f"Network Error: {e}"}
        except Exception as e:
            self.logger.error(f"Submit step {url} failed: {e}")
            return {"success": False, "error": str(e)}

    def submit_final(self, token: str, dob: str, front_hash: str, selfie_hash: str, video_hash: str, timecodes_val: str, log_callback=None) -> Dict[str, Any]:
        import time
        import random
        
        def log(msg):
            if log_callback: log_callback(msg)
            else: self.logger.info(msg)
            
        # DOB
        log("Submitting DOB...")
        res = self._submit_step(ApiEndpoints.SUBMIT_DOB, {"dateOfBirth": dob, "verificationToken": token})
        if not res["success"]: return res
        time.sleep(2) # brief throttle
        
        # Document
        log("Submitting document...")
        res = self._submit_step(ApiEndpoints.SUBMIT_DOCUMENT, {"imageName": front_hash, "verificationToken": token})
        if not res["success"]: return res
        time.sleep(2)
        
        # Selfie
        log("Submitting selfie...")
        res = self._submit_step(ApiEndpoints.SUBMIT_SELFIE, {"imageName": selfie_hash, "verificationToken": token})
        if not res["success"]: return res
        time.sleep(2)
        
        # Video
        log(f"Submitting video (Base Timecode: {timecodes_val}s)...")
        try:
            base_ms = int(float(timecodes_val) * 1000) if timecodes_val else 10000
        except ValueError:
            base_ms = 10000
            
        timecodes = [
            ["CENTER", 0],
            ["LEFT", base_ms + random.randint(0, 500)],
            ["CENTER", base_ms + 7000 + random.randint(0, 500)],
            ["RIGHT", base_ms + 10500 + random.randint(0, 500)],
            ["CENTER", base_ms + 15500 + random.randint(0, 500)]
        ]
        res = self._submit_step(ApiEndpoints.SUBMIT_VIDEO, {
            "imageName": video_hash,
            "verificationToken": token,
            "timecodes": json.dumps(timecodes)
        })
        return res

    def get_verification_status(self, token: str) -> str:
        try:
            resp = self.session.get(ApiEndpoints.verification_status(token), timeout=10)
            resp.raise_for_status()
            return resp.json().get("status", "")
        except Exception as e:
            self.logger.error(f"Get verification status failed: {e}")
            return ""

    @staticmethod
    def check_proxy(proxy_url: str = None, user_agent: str = None) -> Dict[str, Any]:
        """
        Validates proxy visibility by checking against ipwho.is (Ported from IpWhoApiClient).
        """
        try:
            proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
            headers = {"User-Agent": user_agent} if user_agent else None
            resp = requests.get("https://ipwho.is/?utm_source=dev", proxies=proxies, headers=headers, timeout=15)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

