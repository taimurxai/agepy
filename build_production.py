import os
import sys
import shutil
import hashlib
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DIST_DIR = BASE_DIR / "dist"
DIST_EXE = DIST_DIR / "AgeSmartEnterprise.exe"
RELEASE_DIR = BASE_DIR / "release"
SPEC_FILE = BASE_DIR / "AgeSmartEnterprise.spec"

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def log(msg):
    try:
        print(f"[BUILD] {msg}")
    except Exception:
        clean = msg.encode("ascii", errors="replace").decode("ascii")
        print(f"[BUILD] {clean}")

def check_imports():
    log("Validating application modules...")
    modules = [
        "config",
        "services.logger",
        "services.smartweb_service",
        "services.history_service",
        "services.telemetry",
        "core.api_client",
        "core.workflow",
        "ui.theme",
        "ui.dialogs",
        "ui.main_window",
        "utilities.media_helper",
    ]
    for mod in modules:
        try:
            __import__(mod)
            log(f"  [OK] {mod}")
        except Exception as e:
            log(f"  [FAIL] Failed to import {mod}: {e}")
            return False
            
    # Verify tools
    from utilities.media_helper import get_ffmpeg_path, get_ffprobe_path
    ffmpeg_p = get_ffmpeg_path()
    ffprobe_p = get_ffprobe_path()
    log(f"  [OK] ffmpeg binary resolved: {ffmpeg_p}")
    log(f"  [OK] ffprobe binary resolved: {ffprobe_p}")
    return True

def clean_previous_builds():
    log("Cleaning previous build artifacts...")
    build_dir = BASE_DIR / "build"
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir, ignore_errors=True)
        except Exception:
            pass
    if DIST_DIR.exists():
        try:
            shutil.rmtree(DIST_DIR, ignore_errors=True)
        except Exception:
            pass
    DIST_DIR.mkdir(parents=True, exist_ok=True)

def run_pyinstaller():
    log("Running PyInstaller single-file build (this may take 1-2 minutes)...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(SPEC_FILE),
        "--clean",
        "--noconfirm",
    ]
    res = subprocess.run(cmd, cwd=str(BASE_DIR))
    if res.returncode != 0:
        log("PyInstaller single-file build FAILED.")
        return False
    log("PyInstaller build finished successfully.")
    return True

def verify_and_package():
    if not DIST_EXE.is_file():
        log(f"Single-file executable NOT found at: {DIST_EXE}")
        return False
        
    size_mb = DIST_EXE.stat().st_size / (1024 * 1024)
    log(f"Single-file executable generated: {DIST_EXE.name} ({size_mb:.2f} MB)")
    
    # Compute SHA-256 of the standalone executable
    sha256 = hashlib.sha256()
    with open(DIST_EXE, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    checksum = sha256.hexdigest()
    log(f"SHA-256 Checksum: {checksum}")
    
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    release_exe = RELEASE_DIR / "AgeSmartEnterprise.exe"
    shutil.copy2(DIST_EXE, release_exe)
    
    checksum_file = RELEASE_DIR / "checksums.txt"
    with open(checksum_file, "w") as f:
        f.write(f"{checksum} *{DIST_EXE.name}\n")
        
    # Copy to SmartWeb public downloads if directory exists
    web_downloads = Path("D:/AGE UP/SmartWeb/Web/public/downloads")
    if web_downloads.is_dir():
        try:
            target_web_exe = web_downloads / "AgeSmartEnterprise.exe"
            shutil.copy2(DIST_EXE, target_web_exe)
            log(f"Copied single-file executable to web downloads: {target_web_exe}")
        except Exception as e:
            log(f"Notice: Could not copy to web downloads: {e}")
            
    return True

def main():
    log("==================================================")
    log(" AgeSmart Enterprise - Single-File Executable Build")
    log("==================================================")
    
    if not check_imports():
        sys.exit(1)
        
    clean_previous_builds()
    
    if not run_pyinstaller():
        sys.exit(1)
        
    if not verify_and_package():
        sys.exit(1)
        
    log("==================================================")
    log(" BUILD SUCCESSFUL! Single standalone .exe is ready.")
    log("==================================================")

if __name__ == "__main__":
    main()
