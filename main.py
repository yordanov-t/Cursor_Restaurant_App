"""
Flet Build Entry Point for Android/iOS.

This is the entry point for `flet build apk/aab/ipa` commands.
Serious Python runs this module and calls our main(page) function.

For desktop development, use:
  python main_app.py       # Flet UI (default)
  python main_app.py -l    # Legacy Tkinter UI
"""

# =============================================================================
# EARLY LOGGING - Before any imports
# =============================================================================
print("[main.py] ===== MODULE IMPORT STARTED =====", flush=True)
print("[main.py] Python version check...", flush=True)

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
import traceback
from pathlib import Path


# =============================================================================
# DIRECT LOGCAT LOGGING (bypasses Python stdout redirect)
# =============================================================================
_android_log_fn = None

def _init_logcat():
    """Initialize direct logcat output via ctypes (Android only)."""
    global _android_log_fn
    try:
        from ctypes import cdll, c_int, c_char_p
        liblog = cdll.LoadLibrary("liblog.so")
        liblog.__android_log_write.argtypes = [c_int, c_char_p, c_char_p]
        liblog.__android_log_write.restype = c_int
        _android_log_fn = liblog.__android_log_write
    except Exception:
        pass

_init_logcat()


def _logcat(msg):
    """Write directly to Android logcat, bypassing Python stdout."""
    if _android_log_fn is not None:
        try:
            _android_log_fn(4, b"py_bootstrap", str(msg).encode("utf-8", errors="replace"))
        except Exception:
            pass


def _is_android():
    """Check if running on Android."""
    return os.environ.get("FLET_APP_STORAGE_DATA") is not None


def _get_app_dir():
    """Get the app directory for crash logs."""
    if _is_android():
        return Path(__file__).resolve().parent
    return Path(".")


def _log(msg):
    """Log message (always on Android, print for debugging)."""
    _logcat(msg)
    print(f"[Bootstrap] {msg}")


def _write_crash_log(error_msg, tb_str):
    """Write crash log to app directory for debugging."""
    try:
        crash_file = _get_app_dir() / "crash.log"
        with open(crash_file, "w") as f:
            f.write(f"=== CRASH LOG ===\n")
            f.write(f"Error: {error_msg}\n\n")
            f.write(f"Traceback:\n{tb_str}\n")
        _log(f"Crash log written to: {crash_file}")
    except Exception as e:
        _log(f"Failed to write crash log: {e}")


def _fix_windows_backslash_paths(app_dir: Path):
    """
    Fix Windows-style backslash paths extracted from zip.
    
    When a zip created on Windows is extracted on Linux/Android,
    entries like "core\\__init__.py" become flat files with backslash
    in the filename instead of proper directories.
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
    
    for filename in backslash_files:
        try:
            proper_path = filename.replace('\\', '/')
            
            if '/' in proper_path:
                dir_part, file_part = proper_path.rsplit('/', 1)
                target_dir = app_dir / dir_part
                target_file = target_dir / file_part
            else:
                target_file = app_dir / proper_path
                target_dir = None
            
            if target_dir and not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
                _log(f"  Created directory: {dir_part}/")
            
            src_file = app_dir / filename
            if src_file.exists():
                if not target_file.exists():
                    os.rename(str(src_file), str(target_file))
                    _log(f"  Moved: {filename} -> {proper_path}")
                    fixed_count += 1
                else:
                    os.remove(str(src_file))
                    _log(f"  Removed duplicate: {filename}")
                    fixed_count += 1
                    
        except Exception as e:
            _log(f"  ERROR fixing {filename}: {e}")
    
    _log(f"Fixed {fixed_count} files")
    return fixed_count > 0


def _check_zip_for_module(zip_path, module_name="core"):
    """Check if a module exists inside a zip file."""
    try:
        import zipfile
        if not os.path.isfile(zip_path):
            return False
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            target = f"{module_name}/__init__.py"
            target_win = f"{module_name}\\__init__.py"
            found = target in names or target_win in names
            
            _log(f"Checking zip {zip_path}")
            _log(f"  Contains {len(names)} entries")
            _log(f"  {target} found: {found}")
            
            return found
    except Exception as e:
        _log(f"Error reading zip {zip_path}: {e}")
        return False


def _find_app_root():
    """Find the app root directory or zip file containing our modules."""
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
    
    # Fix Windows backslash paths if on Android
    if _is_android():
        fixed = _fix_windows_backslash_paths(this_dir)
        if fixed:
            _log("Re-checking after path fix...")
            try:
                contents = sorted(os.listdir(this_dir))
                _log(f"Contents after fix:")
                for item in contents[:30]:
                    item_path = this_dir / item
                    item_type = "DIR" if item_path.is_dir() else "FILE"
                    _log(f"  [{item_type}] {item}")
            except Exception as e:
                _log(f"  ERROR: {e}")
    
    # Check for physical core/ directory
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
    
    _log("Could not find core/ anywhere!")
    _log(f"Using fallback: {this_dir}")
    return (str(this_dir), False)


def _bootstrap_imports():
    """Ensure app root directory (or zip file) is in sys.path for imports."""
    path_to_add, is_zip = _find_app_root()
    
    _log(f"Adding to sys.path: {path_to_add} (is_zip={is_zip})")
    
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
    
def _ensure_single_instance():
    """
    Ensure only one instance of the Flet app is running.
    Uses a lock file to prevent multiple ft.app() calls.
    """
    try:
        lock_file = _get_app_dir() / "app.lock"
        
        # Check if lock file exists
        if lock_file.exists():
            # Read PID from lock file
            try:
                lock_pid = int(lock_file.read_text().strip())
                
                # Check if process is still running
                try:
                    os.kill(lock_pid, 0)  # Signal 0 checks if process exists
                    _log(f"App already running with PID {lock_pid}")
                    return False  # Another instance is running
                except OSError:
                    # Process not running, stale lock file
                    _log(f"Stale lock file found (PID {lock_pid} not running)")
                    lock_file.unlink()
            except (ValueError, OSError) as e:
                _log(f"Invalid lock file, removing: {e}")
                lock_file.unlink()
        
        # Create lock file with current PID
        lock_file.write_text(str(os.getpid()))
        _log(f"Created lock file for PID {os.getpid()}")
        return True
        
    except Exception as e:
        _log(f"Error checking single instance: {e}")
        # If we can't create lock, assume we can run (fail-safe)
        return True


def _count_open_fds():
    """Count open file descriptors (Linux/Android only)."""
    try:
        fd_dir = Path("/proc/self/fd")
        if fd_dir.exists():
            return len(list(fd_dir.iterdir()))
        return -1
    except:
        return -1


# =============================================================================
# MAIN EXECUTION
# =============================================================================
# ft.app(target=main) MUST be called on ALL platforms (desktop AND mobile).
# On Android/iOS the Dart side sets FLET_SERVER_UDS_PATH; ft.app() creates a
# local server on that UDS path and the Dart FletApp widget connects to it.
# Without ft.app(), Python exits immediately, the callback socket sends "0",
# and the Dart side calls exit(0) — killing the whole Flutter process.

_APP_STARTED = False


def _start_app():
    """Bootstrap imports, then start ft.app() on every platform."""
    global _APP_STARTED
    
    if _APP_STARTED:
        _log("App already started, skipping second initialization")
        return
    
    _APP_STARTED = True
    
    _logcat("===== _start_app() BEGIN =====")
    print("[main.py] ===== MODULE EXECUTION STARTED =====", flush=True)
    
    is_mobile = _is_android() or os.environ.get("FLET_PLATFORM") == "iOS"
    platform_tag = "MOBILE (Android/iOS)" if is_mobile else "DESKTOP"
    _log(f"Platform detected: {platform_tag}")
    
    _logcat(f"FLET_SERVER_UDS_PATH={os.environ.get('FLET_SERVER_UDS_PATH', 'NOT SET')}")
    _logcat(f"FLET_APP_STORAGE_DATA={os.environ.get('FLET_APP_STORAGE_DATA', 'NOT SET')}")
    _logcat(f"CWD={os.getcwd()}")
    
    initial_fds = _count_open_fds()
    _log(f"Initial open file descriptors: {initial_fds}")
    
    try:
        _logcat("Running bootstrap...")
        _bootstrap_imports()
        _logcat("Bootstrap complete")
    except Exception as e:
        error_msg = str(e)
        tb_str = traceback.format_exc()
        _logcat(f"FATAL bootstrap error: {error_msg}")
        _log(f"FATAL ERROR during bootstrap: {error_msg}")
        _log(tb_str)
        _write_crash_log(error_msg, tb_str)
        raise
    
    post_bootstrap_fds = _count_open_fds()
    _log(f"Open FDs after bootstrap: {post_bootstrap_fds} (delta: {post_bootstrap_fds - initial_fds if initial_fds > 0 else '?'})")
    
    _log("=" * 60)
    _log(f"{platform_tag}: Starting ft.app() server")
    _log("=" * 60)
    
    try:
        _logcat("Importing flet...")
        import flet as ft
        flet_ver = ft.__version__ if hasattr(ft, '__version__') else 'unknown'
        _logcat(f"Flet imported OK, version={flet_ver}")
        _log(f"Flet version: {flet_ver}")
        
        before_app_fds = _count_open_fds()
        _log(f"Open FDs before ft.app(): {before_app_fds}")
        
        _logcat("Calling ft.app(target=main) NOW")
        ft.app(target=main)
        _logcat("ft.app() returned normally")
        _log("ft.app() returned - app closed normally")
        
    except Exception as e:
        error_msg = str(e)
        tb_str = traceback.format_exc()
        _logcat(f"FATAL ft.app error: {error_msg}\n{tb_str}")
        _log(f"FATAL ERROR starting Flet app: {error_msg}")
        _log(tb_str)
        _write_crash_log(error_msg, tb_str)
        raise


# Flet entry point function
def main(page):
    """Flet application entry point — called by ft.app() on all platforms."""
    try:
        _logcat("===== main(page) CALLED =====")
        _log("=" * 50)
        _log("main(page) called - app starting")
        _log("=" * 50)
        
        page_fds = _count_open_fds()
        _log(f"Open FDs when page ready: {page_fds}")
        
        _logcat("Importing flet_app...")
        from flet_app import main as app_main
        _logcat("flet_app imported OK, calling app_main(page)...")
        app_main(page)
        _logcat("app_main(page) returned OK")
        _log("app_main(page) returned successfully")
        
        final_fds = _count_open_fds()
        _log(f"Open FDs after app_main: {final_fds}")
        
    except Exception as e:
        error_msg = str(e)
        tb_str = traceback.format_exc()
        _logcat(f"EXCEPTION in main(page): {error_msg}")
        _logcat(tb_str)
        _log(f"EXCEPTION in main(page): {error_msg}")
        _log(tb_str)
        _write_crash_log(error_msg, tb_str)
        
        try:
            import flet as ft
            page.clean()
            page.add(
                ft.Column([
                    ft.Text("App Startup Error", size=24, color="red", weight="bold"),
                    ft.Text(f"Error: {error_msg}", size=16, selectable=True),
                    ft.Text("Details saved to crash.log", size=12, color="grey"),
                ], scroll="auto", spacing=20)
            )
            page.update()
            _logcat("Error UI displayed successfully")
        except Exception as ui_error:
            _logcat(f"Failed to show error UI: {ui_error}")
            _log(f"Failed to show error UI: {ui_error}")


# Execute app startup
# This runs when module is imported
_start_app()

