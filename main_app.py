"""
Flet Application Entry Point (Desktop/Development).

Usage:
    python main_app.py       # Run Flet UI (default)
    python main_app.py -l    # Run Legacy Tkinter UI

For Android/iOS builds, use main.py with flet build command:
    flet build apk --module-name main --project hushove-restaurant-app --icon resources/restaurant_app_icon.png
    flet build aab --module-name main --project hushove-restaurant-app --icon resources/restaurant_app_icon.png
"""

# =============================================================================
# IMPORT BOOTSTRAP - Must run BEFORE any local module imports
# =============================================================================
# On Android (Serious-Python runtime), app code may be inside app.zip.
# Python supports importing from zip files (zipimport), but we need to
# ensure the correct path is in sys.path.
#
# WINDOWS BACKSLASH FIX:
# When a zip is created on Windows with backslash paths (e.g., "core\__init__.py"),
# extracting on Linux/Android creates flat FILES with backslash in the name
# instead of proper directories. This bootstrap detects and fixes that.

import sys
import os
from pathlib import Path


def _is_android():
    """Check if running on Android."""
    return os.environ.get("FLET_APP_STORAGE_DATA") is not None


def _log(msg):
    """Log message on Android only."""
    if _is_android():
        print(f"[Bootstrap] {msg}")


def _fix_windows_backslash_paths(app_dir: Path):
    """
    Fix Windows-style backslash paths extracted from zip.
    
    When a zip created on Windows is extracted on Linux/Android,
    entries like "core\\__init__.py" become flat files with backslash
    in the filename instead of proper directories.
    
    This function detects and fixes that by:
    1. Finding files with backslashes in names
    2. Creating proper directory structure
    3. Moving files to correct locations
    """
    _log("Checking for Windows backslash path issues...")
    
    try:
        contents = os.listdir(app_dir)
    except Exception as e:
        _log(f"Cannot list {app_dir}: {e}")
        return False
    
    # Find files with backslashes in names (Windows path artifacts)
    backslash_files = [f for f in contents if '\\' in f]
    
    if not backslash_files:
        _log("No backslash files found - paths are correct")
        return False
    
    _log(f"FOUND {len(backslash_files)} files with Windows backslash paths!")
    _log("Fixing directory structure...")
    
    fixed_count = 0
    errors = []
    
    for filename in backslash_files:
        try:
            # Convert backslash to forward slash for proper path
            proper_path = filename.replace('\\', '/')
            
            # Split into directory and filename
            if '/' in proper_path:
                dir_part, file_part = proper_path.rsplit('/', 1)
                target_dir = app_dir / dir_part
                target_file = target_dir / file_part
            else:
                target_file = app_dir / proper_path
                target_dir = None
            
            # Create directory if needed
            if target_dir and not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
                _log(f"  Created directory: {dir_part}/")
            
            # Move/rename file from flat name to proper path
            src_file = app_dir / filename
            if src_file.exists():
                if not target_file.exists():
                    os.rename(str(src_file), str(target_file))
                    _log(f"  Moved: {filename} -> {proper_path}")
                    fixed_count += 1
                else:
                    # Target already exists, just remove the backslash file
                    os.remove(str(src_file))
                    _log(f"  Removed duplicate: {filename}")
                    fixed_count += 1
                    
        except Exception as e:
            errors.append(f"{filename}: {e}")
            _log(f"  ERROR fixing {filename}: {e}")
    
    _log(f"Fixed {fixed_count} files")
    
    if errors:
        _log(f"Errors: {len(errors)}")
        for err in errors[:5]:
            _log(f"  {err}")
    
    return fixed_count > 0


def _check_zip_for_module(zip_path, module_name="core"):
    """
    Check if a module exists inside a zip file.
    """
    try:
        import zipfile
        if not os.path.isfile(zip_path):
            return False
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            # Check for module/__init__.py (forward slash)
            target = f"{module_name}/__init__.py"
            # Also check for Windows-style backslash (shouldn't happen but check anyway)
            target_win = f"{module_name}\\__init__.py"
            found = target in names or target_win in names
            
            if _is_android():
                _log(f"Checking zip {zip_path}")
                _log(f"  Contains {len(names)} entries")
                _log(f"  First 20: {names[:20]}")
                _log(f"  {target} found: {found}")
            
            return found
    except Exception as e:
        _log(f"Error reading zip {zip_path}: {e}")
        return False


def _find_app_root():
    """
    Find the actual app root directory or zip file containing our modules.
    
    Returns:
        Tuple of (path_to_add_to_sys_path, is_zip_file)
    """
    this_file = Path(__file__).resolve()
    this_dir = this_file.parent
    
    _log("=" * 50)
    _log("BOOTSTRAP DIAGNOSTICS")
    _log("=" * 50)
    _log(f"__file__ = {__file__}")
    _log(f"Resolved: {this_file}")
    _log(f"Parent dir: {this_dir}")
    _log(f"FLET_APP_STORAGE_DATA = {os.environ.get('FLET_APP_STORAGE_DATA', 'not set')}")
    _log(f"CWD = {os.getcwd()}")
    
    # List contents
    _log(f"Contents of {this_dir}:")
    try:
        contents = sorted(os.listdir(this_dir))
        for item in contents[:50]:
            item_path = this_dir / item
            item_type = "DIR" if item_path.is_dir() else "FILE"
            _log(f"  [{item_type}] {item}")
    except Exception as e:
        _log(f"  ERROR listing: {e}")
    
    # FIRST: Check and fix Windows backslash paths if on Android
    if _is_android():
        fixed = _fix_windows_backslash_paths(this_dir)
        if fixed:
            _log("Re-checking after path fix...")
            # Re-list contents after fix
            try:
                contents = sorted(os.listdir(this_dir))
                _log(f"Contents after fix:")
                for item in contents[:30]:
                    item_path = this_dir / item
                    item_type = "DIR" if item_path.is_dir() else "FILE"
                    _log(f"  [{item_type}] {item}")
            except Exception as e:
                _log(f"  ERROR: {e}")
    
    # Now check for physical core/ directory
    dir_candidates = [
        this_dir,
        this_dir.parent,
        this_dir / "app",
        this_dir.parent / "app",
        Path(os.getcwd()),
    ]
    
    for candidate in dir_candidates:
        try:
            core_dir = candidate / "core"
            core_init = core_dir / "__init__.py"
            
            if core_dir.is_dir() and core_init.is_file():
                _log(f"FOUND physical core/ at: {candidate}")
                try:
                    core_contents = os.listdir(core_dir)
                    _log(f"  core/ contains: {core_contents}")
                except:
                    pass
                return (str(candidate), False)
        except Exception as e:
            _log(f"Error checking {candidate}: {e}")
    
    _log("No physical core/ directory found, checking for app.zip...")
    
    # Check for app.zip
    zip_candidates = [
        this_dir / "app.zip",
        this_dir.parent / "app.zip",
        this_dir.parent / "app" / "app.zip",
        Path(os.getcwd()) / "app.zip",
    ]
    
    flet_storage = os.environ.get("FLET_APP_STORAGE_DATA", "")
    if flet_storage:
        flet_base = Path(flet_storage).parent
        zip_candidates.extend([
            flet_base / "flet" / "app" / "app.zip",
            flet_base / "flet" / "app.zip",
            flet_base / "app.zip",
        ])
    
    for zip_path in zip_candidates:
        zip_str = str(zip_path)
        if _check_zip_for_module(zip_str, "core"):
            _log(f"FOUND core/ inside zip: {zip_str}")
            return (zip_str, True)
    
    # Log failure details
    _log("Could not find core/ anywhere!")
    for candidate in dir_candidates:
        try:
            if candidate.exists():
                contents = os.listdir(candidate)
                _log(f"Contents of {candidate}: {sorted(contents)[:30]}")
        except Exception as e:
            _log(f"Cannot list {candidate}: {e}")
    
    _log(f"Using fallback: {this_dir}")
    return (str(this_dir), False)


def _bootstrap_imports():
    """
    Ensure app root directory (or zip file) is in sys.path for imports.
    """
    path_to_add, is_zip = _find_app_root()
    
    _log(f"Adding to sys.path: {path_to_add} (is_zip={is_zip})")
    
    # Add to sys.path
    if path_to_add not in sys.path:
        sys.path.insert(0, path_to_add)
    elif sys.path[0] != path_to_add:
        try:
            sys.path.remove(path_to_add)
        except ValueError:
            pass
        sys.path.insert(0, path_to_add)
    
    _log(f"sys.path[0] = {sys.path[0]}")
    _log(f"sys.path[:5] = {sys.path[:5]}")
    
    # Try import
    try:
        import core
        _log(f"SUCCESS: import core -> {core.__file__}")
    except ImportError as e:
        _log(f"FAILED: import core -> {e}")
        # Last resort: try adding zip path
        if not is_zip:
            for candidate in [Path(__file__).resolve().parent / "app.zip"]:
                if os.path.isfile(candidate):
                    _log(f"Last resort: trying zip {candidate}")
                    sys.path.insert(0, str(candidate))
                    try:
                        import core
                        _log(f"SUCCESS with zip: {core.__file__}")
                    except ImportError as e2:
                        _log(f"Still failed: {e2}")
    
    _log("Bootstrap complete")


# Run bootstrap immediately
_bootstrap_imports()

# =============================================================================
# Now safe to import local modules
# =============================================================================

import flet as ft
from flet_app import main as flet_main


def run_flet_app():
    """Launch the Flet-based UI."""
    ft.app(target=flet_main)


def run_legacy_app():
    """Launch the legacy Tkinter UI."""
    try:
        from legacy_tk_ui import run_legacy_ui
        run_legacy_ui()
    except ImportError:
        print("Legacy UI module not found. Please use the Flet UI.")
        print("Run: python main_app.py")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Restaurant Management System")
    parser.add_argument(
        "-l", "--legacy",
        action="store_true",
        help="Use legacy Tkinter UI instead of Flet"
    )
    args = parser.parse_args()
    
    if args.legacy:
        run_legacy_app()
    else:
        run_flet_app()
