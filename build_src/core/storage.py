"""
Cross-platform storage utilities for mobile and desktop.

Provides consistent paths for database and settings storage that work on:
- Desktop (Windows, macOS, Linux)
- Android (Flet packaged app)
- iOS (Flet packaged app)

Handles first-run initialization on mobile where app storage starts empty.
"""

import os
import sys
from pathlib import Path

# Track initialization state
_storage_initialized = False
_is_first_run = False


def get_app_storage_path() -> Path:
    """
    Get the writable app storage directory.
    
    On mobile (Android/iOS), uses Flet's app storage directory.
    On desktop, uses the current working directory or user's app data.
    
    Returns:
        Path to writable storage directory
    """
    # Check for Flet mobile environment
    flet_data_dir = os.environ.get("FLET_APP_STORAGE_DATA")
    if flet_data_dir:
        # Mobile: Use Flet's app data directory
        storage_path = Path(flet_data_dir)
    else:
        # Desktop: Use current working directory
        # This maintains backward compatibility with existing installations
        storage_path = Path.cwd()
    
    # Ensure directory exists
    storage_path.mkdir(parents=True, exist_ok=True)
    
    return storage_path


def get_database_path(db_name: str = "restaurant.db") -> str:
    """
    Get the full path to the database file.
    
    Args:
        db_name: Database filename (default: restaurant.db)
        
    Returns:
        Full path to database file as string
    """
    storage = get_app_storage_path()
    return str(storage / db_name)


def get_backup_folder() -> Path:
    """
    Get the path to the backup folder.
    
    Returns:
        Path to backup folder (created if doesn't exist)
    """
    storage = get_app_storage_path()
    backup_path = storage / "backups"
    backup_path.mkdir(parents=True, exist_ok=True)
    return backup_path


def get_settings_path(settings_name: str = "settings.json") -> str:
    """
    Get the full path to the settings file.
    
    Args:
        settings_name: Settings filename (default: settings.json)
        
    Returns:
        Full path to settings file as string
    """
    storage = get_app_storage_path()
    return str(storage / settings_name)


def is_mobile() -> bool:
    """
    Check if running on mobile platform.
    
    Returns:
        True if running on Android/iOS
    """
    return os.environ.get("FLET_APP_STORAGE_DATA") is not None


def is_first_run() -> bool:
    """
    Check if this is the first run of the app.
    
    Determined by checking if the database file exists in app storage.
    
    Returns:
        True if database doesn't exist (first run)
    """
    global _is_first_run
    return _is_first_run


def ensure_storage_initialized() -> bool:
    """
    Ensure all required storage directories exist.
    Call this at app startup.
    
    Returns:
        True if this is the first run (database doesn't exist yet)
    """
    global _storage_initialized, _is_first_run
    
    if _storage_initialized:
        return _is_first_run
    
    # Get storage paths
    storage = get_app_storage_path()
    db_path = storage / "restaurant.db"
    
    # Check if this is first run (no database yet)
    _is_first_run = not db_path.exists()
    
    if _is_first_run:
        print(f"[Storage] First run detected - database will be created at: {db_path}")
        if is_mobile():
            print("[Storage] Running on mobile - using app storage directory")
    else:
        print(f"[Storage] Existing database found at: {db_path}")
    
    # Ensure backup folder exists
    get_backup_folder()
    
    _storage_initialized = True
    return _is_first_run

