import sys
import customtkinter as ctk

from config import APP_NAME, APP_VERSION
from services.logger import init_production_logger, get_logger
from services.smartweb_service import SmartWebService
from core.workflow import SmartVerificationWorkflow
from services.history_service import HistoryService
from services.telemetry import TelemetryClient
from ui.main_window import MainWindow
from ui.dialogs import AuthLoginDialog

def main():
    init_production_logger()
    logger = get_logger("Main")
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}...")
    
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # 1. Initialize SmartWeb Integration Service
    smartweb_service = SmartWebService()
    
    # Check minimum required version from SmartWeb website
    must_update, min_ver, dl_url = smartweb_service.check_version(APP_VERSION)
    if must_update:
        logger.warning(f"[SmartWeb] Update required: minimum version is {min_ver}. Download: {dl_url}")
        
    telemetry_service = TelemetryClient()
    history_service = HistoryService()
    workflow = SmartVerificationWorkflow(
        smartweb_service=smartweb_service,
        telemetry_service=telemetry_service
    )

    # 2. Launch UI
    app = MainWindow(workflow, history_service, smartweb_service=smartweb_service)
    
    # Show Login Dialog before allowing access to main dashboard
    # Show Login Dialog before allowing access to main dashboard
    login_dialog = AuthLoginDialog(app, smartweb_service)
    app.wait_window(login_dialog)
    
    if not getattr(login_dialog, 'is_authenticated', False):
        logger.info("Login cancelled or unauthenticated. Exiting application.")
        try:
            app.destroy()
        except Exception:
            pass
        sys.exit(0)
    
    email = ""
    if smartweb_service.current_user and smartweb_service.current_user.get("email"):
        email = smartweb_service.current_user.get("email")
        
    if email:
        app.set_authenticated_user(email)
        logger.info(f"User authenticated: {email}")
    
    # Start main event loop
    logger.info("Starting mainloop...")
    app.mainloop()
    logger.info("Mainloop exited.")

if __name__ == "__main__":
    main()
