"""
APK Inspection Script

Inspects the actual APK file to verify what Python code is embedded.
This is the SOURCE OF TRUTH - not build/flutter/app/app.zip.

Usage:
    python inspect_apk.py                      # Check default APK location
    python inspect_apk.py path/to/app.apk      # Check specific APK
"""

import sys
import os
import zipfile
import tempfile
import shutil
from pathlib import Path


def find_apk():
    """Find the APK file."""
    candidates = [
        Path("build/apk/app-release.apk"),
        Path("build/apk/app-debug.apk"),
        Path("build/apk/app.apk"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def inspect_apk(apk_path: Path):
    """
    Inspect APK contents to find the Python app payload.
    """
    print("=" * 70)
    print("APK INSPECTION - SOURCE OF TRUTH")
    print("=" * 70)
    print(f"\nAPK Path: {apk_path.absolute()}")
    
    if not apk_path.exists():
        print(f"\n[ERROR] APK not found: {apk_path}")
        return False
    
    apk_size = apk_path.stat().st_size / (1024 * 1024)
    print(f"APK Size: {apk_size:.2f} MB")
    
    try:
        with zipfile.ZipFile(apk_path, 'r') as apk:
            all_entries = apk.namelist()
            
            print(f"\nTotal entries in APK: {len(all_entries)}")
            
            # Find app-related assets
            print("\n" + "=" * 70)
            print("SEARCHING FOR PYTHON APP PAYLOAD")
            print("=" * 70)
            
            # Look for common locations where Flet/Serious-Python stores app code
            search_patterns = [
                "app.zip",
                "app/",
                "assets/app",
                "flutter_assets/app",
                "assets/flutter_assets/app",
                "lib/",
                ".py",
                "core/",
                "ui_flet/",
            ]
            
            # Find all potential app payload locations
            app_related = []
            for entry in all_entries:
                entry_lower = entry.lower()
                for pattern in search_patterns:
                    if pattern in entry_lower:
                        app_related.append(entry)
                        break
            
            if app_related:
                print(f"\nFound {len(app_related)} app-related entries:")
                for entry in sorted(set(app_related))[:50]:
                    size = apk.getinfo(entry).file_size
                    print(f"  {entry} ({size:,} bytes)")
            
            # Look specifically for app.zip
            print("\n" + "=" * 70)
            print("LOOKING FOR app.zip INSIDE APK")
            print("=" * 70)
            
            # Find app.zip (not .hash files)
            app_zip_candidates = [e for e in all_entries if e.endswith("app.zip")]
            
            if not app_zip_candidates:
                print("\n[WARNING] No app.zip found inside APK!")
                print("Looking for alternative Python payload locations...")
                
                # Check for .py files directly
                py_files = [e for e in all_entries if e.endswith('.py')]
                if py_files:
                    print(f"\nFound {len(py_files)} .py files directly in APK:")
                    for f in py_files[:20]:
                        print(f"  {f}")
                else:
                    print("\nNo .py files found directly in APK either.")
                
                # Show all assets
                print("\nAll 'assets' entries:")
                assets = [e for e in all_entries if 'assets' in e.lower()]
                for a in sorted(assets)[:30]:
                    print(f"  {a}")
                
                return False
            
            print(f"\nFound app.zip at: {app_zip_candidates}")
            
            # Extract and inspect app.zip
            for app_zip_path in app_zip_candidates:
                print(f"\n--- Inspecting: {app_zip_path} ---")
                
                # Extract app.zip to temp
                temp_dir = tempfile.mkdtemp()
                try:
                    app_zip_data = apk.read(app_zip_path)
                    temp_app_zip = Path(temp_dir) / "app.zip"
                    temp_app_zip.write_bytes(app_zip_data)
                    
                    app_zip_size = len(app_zip_data) / 1024
                    print(f"app.zip size: {app_zip_size:.1f} KB")
                    
                    # Open the nested app.zip
                    with zipfile.ZipFile(temp_app_zip, 'r') as inner_zip:
                        inner_entries = inner_zip.namelist()
                        
                        print(f"\napp.zip contains {len(inner_entries)} entries:")
                        
                        # Categorize entries
                        py_files = []
                        md_files = []
                        core_files = []
                        ui_files = []
                        other_files = []
                        
                        for entry in inner_entries:
                            if entry.startswith("core/"):
                                core_files.append(entry)
                            elif entry.startswith("ui_flet/"):
                                ui_files.append(entry)
                            elif entry.endswith(".py"):
                                py_files.append(entry)
                            elif entry.endswith(".md"):
                                md_files.append(entry)
                            else:
                                other_files.append(entry)
                        
                        print(f"\n  Python files at root: {len(py_files)}")
                        for f in sorted(py_files):
                            print(f"    - {f}")
                        
                        print(f"\n  core/ package files: {len(core_files)}")
                        for f in sorted(core_files):
                            print(f"    - {f}")
                        
                        print(f"\n  ui_flet/ package files: {len(ui_files)}")
                        for f in sorted(ui_files):
                            print(f"    - {f}")
                        
                        print(f"\n  Markdown files: {len(md_files)}")
                        if md_files:
                            for f in sorted(md_files)[:10]:
                                print(f"    - {f}")
                            if len(md_files) > 10:
                                print(f"    ... and {len(md_files) - 10} more")
                        
                        print(f"\n  Other files: {len(other_files)}")
                        for f in sorted(other_files)[:10]:
                            print(f"    - {f}")
                        
                        # Verify critical files
                        print("\n" + "=" * 70)
                        print("CRITICAL FILE CHECK")
                        print("=" * 70)
                        
                        critical = [
                            "main.py",
                            "flet_app.py",
                            "db.py",
                            "core/__init__.py",
                            "core/storage.py",
                            "core/reservation_service.py",
                            "ui_flet/__init__.py",
                            "ui_flet/theme.py",
                        ]
                        
                        all_present = True
                        for cf in critical:
                            if cf in inner_entries:
                                print(f"  [OK] {cf}")
                            else:
                                print(f"  [MISSING] {cf}")
                                all_present = False
                        
                        # Final verdict
                        print("\n" + "=" * 70)
                        print("VERDICT")
                        print("=" * 70)
                        
                        if all_present and len(core_files) >= 5 and len(ui_files) >= 5:
                            print("\n  [PASS] APK contains valid Python app payload")
                            print(f"         core/ has {len(core_files)} files")
                            print(f"         ui_flet/ has {len(ui_files)} files")
                            if md_files:
                                print(f"         (also has {len(md_files)} unnecessary .md files)")
                            return True
                        else:
                            print("\n  [FAIL] APK is missing critical Python code!")
                            if not core_files:
                                print("         - core/ package is MISSING")
                            if not ui_files:
                                print("         - ui_flet/ package is MISSING")
                            if md_files and not py_files:
                                print("         - Contains only .md files, no .py files!")
                                print("         => Build is packaging docs instead of code!")
                            return False
                
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
    except zipfile.BadZipFile:
        print(f"\n[ERROR] Invalid APK/zip file: {apk_path}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        return False
    
    return False


def main():
    if len(sys.argv) > 1:
        apk_path = Path(sys.argv[1])
    else:
        apk_path = find_apk()
        if not apk_path:
            print("=" * 70)
            print("APK INSPECTION")
            print("=" * 70)
            print("\n[ERROR] No APK found in build/apk/")
            print("\nRun 'flet build apk' first.")
            return 1
    
    success = inspect_apk(apk_path)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

