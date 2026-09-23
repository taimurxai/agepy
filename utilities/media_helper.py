import os
import sys
import subprocess
import uuid
import random
import json
import time
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional

# Try importing image libraries; allow graceful fallback if not installed.
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

try:
    import piexif
except ImportError:
    piexif = None

try:
    import cv2
except ImportError:
    cv2 = None

from config import TEMP_DIR, resource_path

# ==============================================================================
# iPhone Hardware & Camera Profiles (iPhone 13, 14, 15, 16, 17, 18)
# ==============================================================================

IPHONE_PROFILES = [
    {
        "model": "iPhone 13",
        "software": "iOS 17.5.1",
        "lens_back": "iPhone 13 back dual wide camera 5.1mm f/1.6",
        "lens_front": "iPhone 13 front camera 2.71mm f/2.2",
        "f_number_back": (16, 10),
        "f_number_front": (22, 10),
        "focal_length_back": (51, 10),
        "focal_length_front": (271, 100),
        "focal_35mm_back": 26,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 13 Pro",
        "software": "iOS 17.6.1",
        "lens_back": "iPhone 13 Pro back triple camera 5.7mm f/1.5",
        "lens_front": "iPhone 13 Pro front camera 2.71mm f/2.2",
        "f_number_back": (15, 10),
        "f_number_front": (22, 10),
        "focal_length_back": (57, 10),
        "focal_length_front": (271, 100),
        "focal_35mm_back": 26,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 14",
        "software": "iOS 18.0",
        "lens_back": "iPhone 14 back dual wide camera 5.7mm f/1.5",
        "lens_front": "iPhone 14 front camera 2.69mm f/1.9",
        "f_number_back": (15, 10),
        "f_number_front": (19, 10),
        "focal_length_back": (57, 10),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 26,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 14 Pro",
        "software": "iOS 18.1",
        "lens_back": "iPhone 14 Pro back triple camera 6.86mm f/1.78",
        "lens_front": "iPhone 14 Pro front camera 2.69mm f/1.9",
        "f_number_back": (178, 100),
        "f_number_front": (19, 10),
        "focal_length_back": (686, 100),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 24,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 15",
        "software": "iOS 18.1.1",
        "lens_back": "iPhone 15 back dual wide camera 5.96mm f/1.6",
        "lens_front": "iPhone 15 front camera 2.69mm f/1.9",
        "f_number_back": (16, 10),
        "f_number_front": (19, 10),
        "focal_length_back": (596, 100),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 26,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 15 Pro",
        "software": "iOS 18.2",
        "lens_back": "iPhone 15 Pro back triple camera 6.765mm f/1.78",
        "lens_front": "iPhone 15 Pro front camera 2.69mm f/1.9",
        "f_number_back": (178, 100),
        "f_number_front": (19, 10),
        "focal_length_back": (6765, 1000),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 24,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 15 Pro Max",
        "software": "iOS 18.2.1",
        "lens_back": "iPhone 15 Pro Max back triple camera 6.765mm f/1.78",
        "lens_front": "iPhone 15 Pro Max front camera 2.69mm f/1.9",
        "f_number_back": (178, 100),
        "f_number_front": (19, 10),
        "focal_length_back": (6765, 1000),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 24,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 16",
        "software": "iOS 18.3",
        "lens_back": "iPhone 16 back dual camera 5.96mm f/1.6",
        "lens_front": "iPhone 16 front camera 2.69mm f/1.9",
        "f_number_back": (16, 10),
        "f_number_front": (19, 10),
        "focal_length_back": (596, 100),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 26,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 16 Pro",
        "software": "iOS 18.3.1",
        "lens_back": "iPhone 16 Pro back triple camera 6.765mm f/1.78",
        "lens_front": "iPhone 16 Pro front camera 2.69mm f/1.9",
        "f_number_back": (178, 100),
        "f_number_front": (19, 10),
        "focal_length_back": (6765, 1000),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 24,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 16 Pro Max",
        "software": "iOS 18.3.1",
        "lens_back": "iPhone 16 Pro Max back triple camera 6.765mm f/1.78",
        "lens_front": "iPhone 16 Pro Max front camera 2.69mm f/1.9",
        "f_number_back": (178, 100),
        "f_number_front": (19, 10),
        "focal_length_back": (6765, 1000),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 24,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 17 Pro",
        "software": "iOS 19.0",
        "lens_back": "iPhone 17 Pro back triple camera 6.765mm f/1.78",
        "lens_front": "iPhone 17 Pro front camera 2.69mm f/1.9",
        "f_number_back": (178, 100),
        "f_number_front": (19, 10),
        "focal_length_back": (6765, 1000),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 24,
        "focal_35mm_front": 23,
    },
    {
        "model": "iPhone 18 Pro",
        "software": "iOS 20.0",
        "lens_back": "iPhone 18 Pro back triple camera 6.765mm f/1.78",
        "lens_front": "iPhone 18 Pro front camera 2.69mm f/1.9",
        "f_number_back": (178, 100),
        "f_number_front": (19, 10),
        "focal_length_back": (6765, 1000),
        "focal_length_front": (269, 100),
        "focal_35mm_back": 24,
        "focal_35mm_front": 23,
    }
]

def get_iphone_profile(user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Returns an iPhone profile matching the User-Agent, or selects a realistic recent iPhone."""
    if user_agent:
        ua_lower = user_agent.lower()
        for p in IPHONE_PROFILES:
            if p["model"].lower() in ua_lower:
                return p
    # Default to a random recent model (iPhone 14 Pro, 15 Pro, 16 Pro, 17 Pro)
    preferred = [p for p in IPHONE_PROFILES if "Pro" in p["model"]]
    return random.choice(preferred if preferred else IPHONE_PROFILES)

def generate_iphone_exif(profile: Dict[str, Any], is_selfie: bool = False) -> bytes:
    """Generates authentic Apple iPhone EXIF binary bytes for piexif."""
    if not piexif:
        return b""
        
    now = datetime.now() - timedelta(seconds=random.randint(10, 80))
    now_str = now.strftime("%Y:%m:%d %H:%M:%S")
    subsec = str(random.randint(100, 999))
    
    lens_model = profile["lens_front"] if is_selfie else profile["lens_back"]
    f_num = profile["f_number_front"] if is_selfie else profile["f_number_back"]
    focal = profile["focal_length_front"] if is_selfie else profile["focal_length_back"]
    focal_35 = profile["focal_35mm_front"] if is_selfie else profile["focal_35mm_back"]
    iso = random.choice([50, 64, 80, 100, 125, 160])
    exposure = random.choice([(1, 120), (1, 60), (1, 100), (1, 180)])
    
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: b"Apple",
            piexif.ImageIFD.Model: profile["model"].encode("utf-8"),
            piexif.ImageIFD.Software: profile["software"].encode("utf-8"),
            piexif.ImageIFD.DateTime: now_str.encode("utf-8"),
            piexif.ImageIFD.Orientation: 1,
            piexif.ImageIFD.XResolution: (72, 1),
            piexif.ImageIFD.YResolution: (72, 1),
            piexif.ImageIFD.ResolutionUnit: 2,
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: now_str.encode("utf-8"),
            piexif.ExifIFD.DateTimeDigitized: now_str.encode("utf-8"),
            piexif.ExifIFD.SubSecTimeOriginal: subsec.encode("utf-8"),
            piexif.ExifIFD.SubSecTimeDigitized: subsec.encode("utf-8"),
            piexif.ExifIFD.ExposureTime: exposure,
            piexif.ExifIFD.FNumber: f_num,
            piexif.ExifIFD.ExposureProgram: 2,
            piexif.ExifIFD.ISOSpeedRatings: iso,
            piexif.ExifIFD.ExifVersion: b"0232",
            piexif.ExifIFD.ShutterSpeedValue: (random.randint(58, 68), 10),
            piexif.ExifIFD.ApertureValue: (int((f_num[0] / f_num[1]) * 100), 100),
            piexif.ExifIFD.BrightnessValue: (random.randint(10, 80), 10),
            piexif.ExifIFD.ExposureBiasValue: (0, 1),
            piexif.ExifIFD.MeteringMode: 5,
            piexif.ExifIFD.Flash: 16,
            piexif.ExifIFD.FocalLength: focal,
            piexif.ExifIFD.ColorSpace: 1,
            piexif.ExifIFD.SensingMethod: 2,
            piexif.ExifIFD.SceneType: b"\x01",
            piexif.ExifIFD.ExposureMode: 0,
            piexif.ExifIFD.WhiteBalance: 0,
            piexif.ExifIFD.FocalLengthIn35mmFilm: focal_35,
            piexif.ExifIFD.SceneCaptureType: 0,
            piexif.ExifIFD.LensMake: b"Apple",
            piexif.ExifIFD.LensModel: lens_model.encode("utf-8"),
            piexif.ExifIFD.LensSpecification: (
                focal, focal, f_num, f_num
            ),
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None
    }
    return piexif.dump(exif_dict)

# ==============================================================================
# Binary Resolvers (ffmpeg & ffprobe)
# ==============================================================================

def get_ffmpeg_path() -> str:
    """Find ffmpeg in bundled tools, app directory, local data, or system path."""
    candidates = [
        resource_path("tools/ffmpeg.exe"),
        resource_path("tools/bin/ffmpeg.exe"),
        resource_path("ffmpeg.exe"),
        resource_path("ffmpeg/ffmpeg.exe"),
        resource_path("ffmpeg/bin/ffmpeg.exe"),
        os.path.join(os.path.dirname(sys.executable), "tools", "ffmpeg.exe"),
        os.path.join(os.path.dirname(sys.executable), "ffmpeg.exe"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "ffmpeg.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "AgeSmart", "bin", "ffmpeg.exe"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
            
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return which_ffmpeg
        
    return "ffmpeg"

def get_ffprobe_path() -> str:
    """Find ffprobe in bundled tools, app directory, local data, or system path."""
    candidates = [
        resource_path("tools/ffprobe.exe"),
        resource_path("tools/bin/ffprobe.exe"),
        resource_path("ffprobe.exe"),
        resource_path("ffprobe/ffprobe.exe"),
        resource_path("ffprobe/bin/ffprobe.exe"),
        os.path.join(os.path.dirname(sys.executable), "tools", "ffprobe.exe"),
        os.path.join(os.path.dirname(sys.executable), "ffprobe.exe"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "ffprobe.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "AgeSmart", "bin", "ffprobe.exe"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
            
    which_ffprobe = shutil.which("ffprobe")
    if which_ffprobe:
        return which_ffprobe
        
    return "ffprobe"

def run_ffmpeg(args) -> subprocess.CompletedProcess:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def run_ffprobe(args) -> subprocess.CompletedProcess:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# ==============================================================================
# Temp Storage & Housekeeping
# ==============================================================================

def _sanitized_dir() -> str:
    path = str(TEMP_DIR)
    os.makedirs(path, exist_ok=True)
    _cleanup_old_temp_files(path)
    return path

def _cleanup_old_temp_files(dir_path: str, max_age_hours: int = 24):
    """Purge temporary media files older than max_age_hours."""
    try:
        now = time.time()
        for f in os.listdir(dir_path):
            fp = os.path.join(dir_path, f)
            if os.path.isfile(fp) and (now - os.path.getmtime(fp)) > (max_age_hours * 3600):
                try:
                    os.remove(fp)
                except Exception:
                    pass
    except Exception:
        pass

# ==============================================================================
# Media Standardization & Inspection Service (ffmpeg & ffprobe)
# ==============================================================================

class MediaStandardizationService:
    """
    Handles media validation, probing with ffprobe, video standardization (H.264/AAC MP4)
    with ffmpeg, and image standardization to clean JPEG with authentic Apple iPhone EXIF.
    """
    MP4_BRANDS = {
        "isom", "iso2", "iso3", "iso4", "iso5", "iso6",
        "mp41", "mp42", "avc1", "M4V ", "MSNV", "dash", "qt  "
    }
    
    SUPPORTED_IMAGE_FORMATS = {
        "JPEG", "JPG", "PNG", "WEBP", "BMP", "TIFF", "TIF", "GIF", "HEIC", "HEIF", "AVIF"
    }

    @classmethod
    def probe_video(cls, video_path: str) -> Dict[str, Any]:
        """
        Uses ffprobe to inspect video stream codec, format, duration, and major brand.
        Falls back to cv2/ffmpeg if ffprobe fails.
        """
        info = {
            "has_video": False,
            "format_name": "",
            "major_brand": "",
            "codec_name": "",
            "duration": 0.0,
            "width": 0,
            "height": 0,
            "is_mp4": False,
            "mime_type": "video/mp4"
        }
        
        ffprobe_bin = get_ffprobe_path()
        try:
            cmd = [
                ffprobe_bin,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name,width,height,duration:format=format_name,duration:format_tags=major_brand",
                "-of", "json",
                video_path
            ]
            res = run_ffprobe(cmd)
            if res.returncode == 0 and res.stdout:
                data = json.loads(res.stdout.decode("utf-8", errors="ignore"))
                streams = data.get("streams", [])
                if streams:
                    stream = streams[0]
                    info["has_video"] = True
                    info["codec_name"] = stream.get("codec_name", "")
                    info["width"] = stream.get("width", 0)
                    info["height"] = stream.get("height", 0)
                    if stream.get("duration"):
                        try:
                            info["duration"] = float(stream["duration"])
                        except ValueError:
                            pass
                            
                fmt = data.get("format", {})
                info["format_name"] = fmt.get("format_name", "")
                if not info["duration"] and fmt.get("duration"):
                    try:
                        info["duration"] = float(fmt["duration"])
                    except ValueError:
                        pass
                        
                tags = fmt.get("tags", {})
                info["major_brand"] = tags.get("major_brand", "").strip()
                
                # Check MP4 / QuickTime compatibility
                if info["major_brand"] in cls.MP4_BRANDS or "mp4" in info["format_name"] or "mov" in info["format_name"]:
                    info["is_mp4"] = True
                    
                return info
        except Exception:
            pass
            
        # Fallback to OpenCV / ffmpeg
        duration = get_video_duration(video_path)
        info["duration"] = duration
        info["has_video"] = duration > 0
        ext = os.path.splitext(video_path)[1].lower()
        info["is_mp4"] = ext in [".mp4", ".m4v", ".mov"]
        return info

    @classmethod
    def standardize_video(cls, input_path: str, profile: Optional[Dict[str, Any]] = None, log_callback=None) -> Tuple[str, bool]:
        """
        Ensures video is valid H.264/AAC MP4 with iPhone camera tags and +faststart.
        Returns (output_path, was_converted).
        """
        def log(msg):
            if log_callback:
                log_callback(msg)
                
        active_profile = profile or get_iphone_profile()
        probe = cls.probe_video(input_path)
        
        # Transcode or remux with iPhone tags
        log(f"Processing video into iPhone standard format ({active_profile['model']})...")
        output_path = os.path.join(_sanitized_dir(), f"std_{uuid.uuid4().hex}.mp4")
        
        now = datetime.now()
        now_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000000Z")
        now_iso_tz = now.strftime("%Y-%m-%dT%H:%M:%S%z") or f"{now.strftime('%Y-%m-%dT%H:%M:%S')}+0600"
        
        cmd = [
            get_ffmpeg_path(),
            "-hide_banner", "-loglevel", "error", "-y",
            "-i", input_path,
            "-map", "0:v:0", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            "-metadata", f"creation_time={now_utc}",
            "-metadata", "handler_name=Core Media Data Handler",
            "-metadata", "encoder=Apple QuickTime",
            "-metadata", "com.apple.quicktime.make=Apple",
            "-metadata", f"com.apple.quicktime.model={active_profile['model']}",
            "-metadata", f"com.apple.quicktime.software={active_profile['software']}",
            "-metadata", f"com.apple.quicktime.creationdate={now_iso_tz}",
            "-metadata:s:v:0", "handler_name=Core Media Video Handler",
            "-metadata:s:a:0", "handler_name=Core Media Audio Handler",
            output_path
        ]
        
        res = run_ffmpeg(cmd)
        if res.returncode == 0 and os.path.isfile(output_path):
            log(f"Video standardized successfully to Apple {active_profile['model']} MP4.")
            return output_path, True
            
        log(f"Warning: ffmpeg conversion returned code {res.returncode}. Using original video.")
        return input_path, False

    @classmethod
    def standardize_image(cls, input_path: str, profile: Optional[Dict[str, Any]] = None, is_selfie: bool = False) -> Tuple[str, bool]:
        """
        Standardizes any image (PNG, HEIC, HEIF, WEBP, BMP, etc.) into high-quality JPEG
        and injects authentic Apple iPhone EXIF metadata.
        Returns (output_path, was_converted).
        """
        if not Image:
            return input_path, False
            
        active_profile = profile or get_iphone_profile()
        try:
            with Image.open(input_path) as img:
                # Convert to RGB (removing alpha channel onto white background if present)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    alpha_img = img.convert("RGBA")
                    background.paste(alpha_img, mask=alpha_img.split()[3])
                    clean_img = background
                else:
                    clean_img = img.convert("RGB")
                    
                output_path = os.path.join(_sanitized_dir(), f"std_{uuid.uuid4().hex}.jpg")
                exif_bytes = generate_iphone_exif(active_profile, is_selfie=is_selfie)
                
                if exif_bytes:
                    clean_img.save(output_path, format="JPEG", quality=95, exif=exif_bytes)
                else:
                    clean_img.save(output_path, format="JPEG", quality=95)
                    
                return output_path, True
        except Exception:
            return input_path, False

# ==============================================================================
# Privacy & Anti-Fingerprint Processors (with iPhone EXIF Injection)
# ==============================================================================

class ImagePrivacyProcessor:
    @staticmethod
    def create_altered_image(input_path: str, profile: Optional[Dict[str, Any]] = None, is_selfie: bool = False) -> str:
        """
        Creates an altered image (subtle pixel perturbation + authentic iPhone EXIF)
        and saves it to a temp path.
        Returns the new file path.
        """
        if not Image or not piexif:
            raise RuntimeError("PIL and piexif are required for image alteration.")
            
        active_profile = profile or get_iphone_profile()
        file_name = os.path.basename(input_path)
        out_path = os.path.join(_sanitized_dir(), f"altered_{uuid.uuid4().hex}_{file_name}")
        
        img = Image.open(input_path).convert("RGB")
        width, height = img.size
        pixels = img.load()
        
        # Add slight noise to random pixels to alter cryptographic hash
        for _ in range(4):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            r, g, b = pixels[x, y]
            ch = random.choice([0, 1, 2])
            if ch == 0: r = (r + 1) % 256
            elif ch == 1: g = (g + 1) % 256
            else: b = (b + 1) % 256
            pixels[x, y] = (r, g, b)

        exif_bytes = generate_iphone_exif(active_profile, is_selfie=is_selfie)
        img.save(out_path, format="JPEG", exif=exif_bytes, quality=92)
        return out_path

    @staticmethod
    def sanitize_image_metadata(input_path: str, prefix: str = "original", profile: Optional[Dict[str, Any]] = None, is_selfie: bool = False) -> str:
        """
        Sanitizes image by injecting authentic Apple iPhone EXIF metadata (overwriting any previous device info).
        """
        if not Image:
            return input_path
            
        active_profile = profile or get_iphone_profile()
        out_path = os.path.join(_sanitized_dir(), f"{prefix}_{uuid.uuid4().hex}.jpg")
        try:
            img = Image.open(input_path).convert("RGB")
            exif_bytes = generate_iphone_exif(active_profile, is_selfie=is_selfie)
            if exif_bytes:
                img.save(out_path, format="JPEG", quality=95, exif=exif_bytes)
            else:
                img.save(out_path, format="JPEG", quality=95)
            return out_path
        except Exception:
            return input_path

    @staticmethod
    def sanitize_video_metadata(input_path: str, prefix: str = "video", profile: Optional[Dict[str, Any]] = None) -> str:
        """
        Strips old metadata and injects authentic Apple iPhone QuickTime/MP4 metadata using ffmpeg.
        """
        active_profile = profile or get_iphone_profile()
        ext = os.path.splitext(input_path)[1].lower() or ".mp4"
        out_path = os.path.join(_sanitized_dir(), f"{prefix}_{uuid.uuid4().hex}{ext}")
        
        now = datetime.now()
        now_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000000Z")
        now_iso_tz = now.strftime("%Y-%m-%dT%H:%M:%S%z") or f"{now.strftime('%Y-%m-%dT%H:%M:%S')}+0600"
        
        cmd = [
            get_ffmpeg_path(), "-y", "-i", input_path,
            "-map", "0",
            "-map_metadata", "-1",
            "-metadata", f"creation_time={now_utc}",
            "-metadata", "handler_name=Core Media Data Handler",
            "-metadata", "encoder=Apple QuickTime",
            "-metadata", "com.apple.quicktime.make=Apple",
            "-metadata", f"com.apple.quicktime.model={active_profile['model']}",
            "-metadata", f"com.apple.quicktime.software={active_profile['software']}",
            "-metadata", f"com.apple.quicktime.creationdate={now_iso_tz}",
            "-metadata:s:v:0", "handler_name=Core Media Video Handler",
            "-metadata:s:a:0", "handler_name=Core Media Audio Handler",
            "-c", "copy",
            out_path
        ]
        try:
            res = run_ffmpeg(cmd)
            if res.returncode == 0 and os.path.isfile(out_path):
                return out_path
        except Exception:
            pass
        return input_path

# ==============================================================================
# Helper functions for duration and bitrate
# ==============================================================================

def get_video_duration(input_path: str) -> float:
    try:
        if cv2:
            cap = cv2.VideoCapture(input_path)
            if cap and cap.isOpened():
                fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
                frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
                cap.release()
                if fps > 0 and frames > 0:
                    return max(0.0, frames / fps)
    except Exception:
        pass
    
    # Fallback to ffprobe/ffmpeg
    try:
        result = run_ffmpeg([get_ffmpeg_path(), "-i", input_path])
        stderr = (result.stderr or b"").decode("utf-8", errors="ignore")
        marker = "Duration: "
        i = stderr.find(marker)
        if i >= 0:
            chunk = stderr[i + len(marker):i + len(marker) + 16]
            hh, mm, ss = chunk.split(",")[0].split(":")
            return int(hh) * 3600 + int(mm) * 60 + float(ss)
    except Exception:
        pass
    return 0.0

def get_video_bitrate(input_path: str) -> int:
    try:
        size_bytes = os.path.getsize(input_path)
        duration = get_video_duration(input_path)
        if duration > 0:
            return max(200000, int(size_bytes * 8 / duration))
        return 1000000
    except Exception:
        return 1000000
