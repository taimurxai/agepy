import requests
import platform
import uuid
import hashlib
import getpass
import socket
from typing import Dict, Any, Tuple

class DeviceFingerprint:
    def __init__(self, device_id_hash: str, source: str, is_valid: bool):
        self.device_id_hash = device_id_hash
        self.source = source
        self.is_valid = is_valid

class LocalDeviceFingerprintProvider:
    @staticmethod
    def capture() -> DeviceFingerprint:
        try:
            import winreg
            # Fetch the stable Windows MachineGuid which persists across network changes
            registry = winreg.HKEY_LOCAL_MACHINE
            address = r"SOFTWARE\Microsoft\Cryptography"
            key = winreg.OpenKey(registry, address, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            
            system = platform.system()
            raw = f"{system}-{machine_guid}"
            device_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
            return DeviceFingerprint(device_hash, "Windows_Python", True)
        except Exception:
            # Fallback if registry access fails
            try:
                raw = f"{platform.system()}-{platform.node()}-{getpass.getuser()}"
                device_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
                return DeviceFingerprint(device_hash, "Windows_Python", True)
            except Exception:
                return DeviceFingerprint("", "Error", False)

class SupabaseDeviceBindingService:
    def __init__(self):
        self.fingerprint_provider = LocalDeviceFingerprintProvider()
        
    def verify_or_bind(self, supabase_url: str, supabase_anon_key: str, access_token: str) -> Tuple[bool, bool, str]:
        """
        Returns (Allowed, WasBound, Message)
        """
        if not supabase_url or not supabase_anon_key or not access_token:
            return False, False, "Supabase session is required before device binding."
            
        fingerprint = self.fingerprint_provider.capture()
        if not fingerprint.is_valid:
            return False, False, "This device could not produce a valid fingerprint."
            
        payload = {
            "p_device_id_hash": fingerprint.device_id_hash,
            "p_device_source": fingerprint.source
        }
        
        headers = {
            "apikey": supabase_anon_key,
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Build URL properly
        base = supabase_url.rstrip("/")
        rpc_url = f"{base}/rest/v1/rpc/verify_or_bind_device"
        
        try:
            resp = requests.post(rpc_url, json=payload, headers=headers, timeout=25)
            if resp.status_code == 404:
                return False, False, "Supabase device binding RPC is not installed."
                
            resp.raise_for_status()
            
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
                
            allowed = data.get("allowed", False)
            was_bound = data.get("was_bound", False)
            msg = data.get("message", "")
            
            if not allowed and not msg:
                msg = "Access denied. This account is already registered to another Windows device."
                
            return allowed, was_bound, msg
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (401, 403):
                return False, False, "Supabase denied the device binding check. Confirm the RPC grant."
            
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                pass
                
            msg = error_data.get("message") or error_data.get("details") or error_data.get("hint") or f"Supabase device binding failed ({e.response.status_code})"
            return False, False, msg
        except Exception as e:
            return False, False, str(e)
