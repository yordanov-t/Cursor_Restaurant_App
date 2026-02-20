"""
Build Verification Script for Flet Android APK/AAB.

This script inspects the app.zip produced by `flet build` to verify
that all required modules are present and no unwanted files are included.

Usage:
    python verify_build.py                    # Check default location
    python verify_build.py path/to/app.zip   # Check specific zip

Exit codes:
    0 - All checks passed
    1 - Verification failed
"""

import sys
import os
import zipfile
from pathlib import Path


# Files that MUST be present at the root of app.zip
REQUIRED_FILES = [
    "main.py",
    "flet_app.py",
    "db.py",
    "core/__init__.py",
    "core/storage.py",
    "core/time_utils.py",
    "core/reservation_service.py",
    "core/table_layout_service.py",
    "core/backup_service.py",
    "ui_flet/__init__.py",
    "ui_flet/theme.py",
    "ui_flet/compat.py",
    "ui_flet/i18n.py",
    "ui_flet/app_state.py",
    "ui_flet/action_panel.py",
    "ui_flet/reservations_screen_v3.py",
    "ui_flet/table_layout_screen_v2.py",
    "ui_flet/admin_screen_v2.py",
]

# Patterns that must NOT be present in app.zip (packaging errors)
FORBIDDEN_PATTERNS = [
    ".git/",
    ".git\\",
    ".cursor/",
    ".cursor\\",
    "__pycache__/",
    "__pycache__\\",
    ".pyc",
    "backups/",
    "backups\\",
    "build/",
    "build\\",
    "restaurant.db",
]


def find_app_zip():
    """Find the app.zip file produced by flet build."""
    # Common locations for flet build output
    candidates = [
        Path("build/flutter/app/app.zip"),
        Path("build/app/app.zip"),
        Path("build/apk/app.zip"),
        Path("build/android/app.zip"),
        Path("app.zip"),
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    return None


def verify_app_zip(zip_path: Path) -> bool:
    """
    Verify the contents of app.zip.
    
    Returns True if all checks pass, False otherwise.
    """
    print("=" * 70)
    print("FLET BUILD VERIFICATION")
    print("=" * 70)
    print(f"\nChecking: {zip_path.absolute()}")
    
    if not zip_path.exists():
        print(f"\n[ERROR] File not found: {zip_path}")
        return False
    
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Size: {size_mb:.2f} MB")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            all_entries = zf.namelist()
            
            # --- List contents ---
            print(f"\n{'=' * 70}")
            print(f"ZIP CONTENTS ({len(all_entries)} entries)")
            print("=" * 70)
            
            # Group by directory
            dirs_seen = set()
            files_at_root = []
            
            for entry in sorted(all_entries):
                if "/" in entry:
                    top_dir = entry.split("/")[0]
                    dirs_seen.add(top_dir)
                else:
                    files_at_root.append(entry)
            
            print("\nRoot-level files:")
            for f in sorted(files_at_root):
                print(f"  [FILE] {f}")
            
            print("\nRoot-level directories:")
            for d in sorted(dirs_seen):
                count = len([e for e in all_entries if e.startswith(d + "/")])
                print(f"  [DIR]  {d}/ ({count} files)")
            
            # --- Check required files ---
            print(f"\n{'=' * 70}")
            print("REQUIRED FILES CHECK")
            print("=" * 70)
            
            all_present = True
            for required in REQUIRED_FILES:
                # Normalize path separators
                required_norm = required.replace("\\", "/")
                if required_norm in all_entries:
                    print(f"  [OK]      {required}")
                else:
                    print(f"  [MISSING] {required}")
                    all_present = False
            
            # --- Check forbidden patterns ---
            print(f"\n{'=' * 70}")
            print("FORBIDDEN CONTENT CHECK")
            print("=" * 70)
            
            forbidden_found = []
            for entry in all_entries:
                for pattern in FORBIDDEN_PATTERNS:
                    if pattern in entry:
                        forbidden_found.append(entry)
                        break
            
            if not forbidden_found:
                print("  [OK] No forbidden content found")
            else:
                print(f"  [ERROR] Found {len(forbidden_found)} forbidden entries:")
                for entry in forbidden_found[:20]:  # Show first 20
                    print(f"      - {entry}")
                if len(forbidden_found) > 20:
                    print(f"      ... and {len(forbidden_found) - 20} more")
            
            # --- Verify core package structure ---
            print(f"\n{'=' * 70}")
            print("PACKAGE STRUCTURE CHECK")
            print("=" * 70)
            
            core_files = [e for e in all_entries if e.startswith("core/")]
            ui_files = [e for e in all_entries if e.startswith("ui_flet/")]
            
            print(f"\n  core/ package: {len(core_files)} files")
            for f in sorted(core_files):
                print(f"    - {f}")
            
            print(f"\n  ui_flet/ package: {len(ui_files)} files")
            for f in sorted(ui_files):
                print(f"    - {f}")
            
            # --- Final result ---
            print(f"\n{'=' * 70}")
            print("VERIFICATION RESULT")
            print("=" * 70)
            
            success = all_present and len(forbidden_found) == 0
            
            if success:
                print("\n  [PASS] ALL CHECKS PASSED")
                print("\n  The APK should work correctly on Android.")
                print("  core/ and ui_flet/ are at the zip root level.")
            else:
                print("\n  [FAIL] VERIFICATION FAILED")
                if not all_present:
                    print("  - Some required files are missing")
                if forbidden_found:
                    print("  - Forbidden content was packaged")
                print("\n  Please check pyproject.toml include/exclude patterns.")
            
            return success
            
    except zipfile.BadZipFile:
        print(f"\n[ERROR] Invalid zip file: {zip_path}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        return False


def main():
    """Main entry point."""
    # Get zip path from command line or find automatically
    if len(sys.argv) > 1:
        zip_path = Path(sys.argv[1])
    else:
        zip_path = find_app_zip()
        if not zip_path:
            print("=" * 70)
            print("FLET BUILD VERIFICATION")
            print("=" * 70)
            print("\n[ERROR] app.zip not found")
            print("\nSearched locations:")
            print("  - build/flutter/app/app.zip")
            print("  - build/app/app.zip")
            print("  - build/apk/app.zip")
            print("  - app.zip")
            print("\nRun 'flet build apk --module-name main' first,")
            print("or specify the zip path: python verify_build.py path/to/app.zip")
            return 1
    
    success = verify_app_zip(zip_path)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
