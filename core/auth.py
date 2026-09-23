import os
from supabase import create_client, Client
import platform
import hashlib
import uuid

class AuthSession:
    def __init__(self, access_token, user_id, user_email):
        self.access_token = access_token
        self.user_id = user_id
        self.user_email = user_email

class SupabaseAuthService:
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.client: Client = create_client(url, key)
        self.current_session = None

    def get_device_fingerprint(self):
        # Match the LocalDeviceFingerprintProvider logic in C# and helper.py in PY APP
        raw = platform.node() + platform.system() + platform.machine() + str(uuid.getnode())
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def get_mac_address(self):
        try:
            mac = uuid.getnode()
            return ':'.join(f'{((mac >> ele) & 255):02x}' for ele in range(40, -1, -8))
        except Exception:
            return None

    def login(self, email, password):
        try:
            res = self.client.auth.sign_in_with_password({"email": email, "password": password})
            self.current_session = AuthSession(
                res.session.access_token,
                res.user.id,
                res.user.email
            )
            return True, "Success"
        except Exception as e:
            return False, str(e)

    def verify_device_binding(self):
        """
        Replicates device binding logic: 
        Ensures the current device fingerprint or MAC is authorized for this user.
        """
        if not self.current_session:
            return False, "Not logged in"
            
        try:
            from core.device_binding import SupabaseDeviceBindingService
            service = SupabaseDeviceBindingService()
            # The verify_or_bind requires supabase_url, supabase_anon_key, access_token
            allowed, was_bound, msg = service.verify_or_bind(
                self.url, 
                self.key, 
                self.current_session.access_token
            )
            if not allowed:
                return False, msg
                
            return True, "Device authorized"
        except Exception as e:
            return False, str(e)
