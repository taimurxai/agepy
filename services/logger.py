import logging
import logging.handlers
import sys
import threading
import traceback
from config import LOG_FILE

_is_initialized = False

def init_production_logger(level=logging.INFO):
    global _is_initialized
    if _is_initialized:
        return
        
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Rotating File Handler (5 MB max, 3 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        str(LOG_FILE),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler (only if stdout is available)
    if sys.stdout and not getattr(sys, "frozen", False):
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
    # Set global exception hook
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        root_logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
        
    sys.excepthook = handle_exception
    
    # Threading exception hook (Python 3.8+)
    if hasattr(threading, "excepthook"):
        def handle_thread_exception(args):
            root_logger.critical(
                f"Uncaught thread exception in {args.thread.name}:",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
            )
        threading.excepthook = handle_thread_exception
        
    _is_initialized = True
    root_logger.info("Production logger initialized successfully.")

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
