"""
Prepare Build Script

Creates a clean staging folder with app.zip containing POSIX-style paths
(forward slashes) for cross-platform compatibility.

CRITICAL: Windows creates zip entries with backslashes which break on Android.
This script explicitly uses forward slashes in all zip paths.

Usage:
    python prepare_build.py
    flet build apk --module-name main --project restaurant-app --no-rich-output build_src

The script creates:
    build_src/
        main.py, main_app.py, etc. (for flet build to find)
        app.zip (with correct forward-slash POSIX paths - what actually gets deployed)
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path


# Files to include at root level
ROOT_FILES = [
    "main.py",          # Android/iOS entry point ONLY
    "flet_app.py",
    "db.py",
    "requirements.txt",
]

# Directories to include (all .py files inside)
PACKAGES = [
    "core",
    "ui_flet",
]

# Resource directories to copy
RESOURCE_DIRS = [
    "resources",
]

# Assets to copy (Flet looks for these)
ASSETS = {
    "resources/restaurant_app_icon.png": "assets/icon.png",
}


def prepare_build():
    """Create clean staging folder with properly formatted files."""
    project_root = Path(__file__).parent
    staging_dir = project_root / "build_src"
    
    print("=" * 60)
    print("PREPARE BUILD - Creating clean staging folder")
    print("=" * 60)
    print(f"\nProject root: {project_root}")
    print(f"Staging dir:  {staging_dir}")
    
    # Remove existing staging dir
    if staging_dir.exists():
        print(f"\nRemoving existing {staging_dir}...")
        shutil.rmtree(staging_dir)
    
    staging_dir.mkdir()
    print(f"Created {staging_dir}")
    
    # Copy root files (flet build needs these to find entry point)
    print("\nCopying root files:")
    for filename in ROOT_FILES:
        src = project_root / filename
        if src.exists():
            shutil.copy2(src, staging_dir / filename)
            print(f"  [FILE] {filename}")
    
    # Copy package directories
    print("\nCopying packages:")
    for pkg_name in PACKAGES:
        src_dir = project_root / pkg_name
        dst_dir = staging_dir / pkg_name
        if src_dir.exists():
            dst_dir.mkdir(exist_ok=True)
            py_files = list(src_dir.glob("*.py"))
            for py_file in py_files:
                shutil.copy2(py_file, dst_dir / py_file.name)
            print(f"  [DIR]  {pkg_name}/ ({len(py_files)} .py files)")
    
    # Copy resource directories
    print("\nCopying resources:")
    for res_dir_name in RESOURCE_DIRS:
        src_dir = project_root / res_dir_name
        dst_dir = staging_dir / res_dir_name
        if src_dir.exists():
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            file_count = len(list(dst_dir.rglob("*")))
            print(f"  [DIR]  {res_dir_name}/ ({file_count} files)")
    
    # Copy assets for Flet (icon, etc.)
    print("\nCopying assets:")
    for src_rel, dst_rel in ASSETS.items():
        src_file = project_root / src_rel
        dst_file = staging_dir / dst_rel
        if src_file.exists():
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            print(f"  [FILE] {src_rel} -> {dst_rel}")
        else:
            print(f"  [SKIP] {src_rel} (not found)")
    
    # Now create app.zip with EXPLICIT POSIX (forward slash) paths
    # This is CRITICAL - Windows creates backslash paths which break on Android!
    print("\n" + "=" * 60)
    print("CREATING app.zip WITH POSIX PATHS (forward slashes)")
    print("=" * 60)
    print("\nThis ensures the zip works on Android/Linux!")
    
    app_zip_path = staging_dir / "app.zip"
    
    with zipfile.ZipFile(app_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        entries = []
        
        # Add root files with simple names (no path separator needed)
        for filename in ROOT_FILES:
            src = staging_dir / filename
            if src.exists():
                # arcname is the name stored in the zip - use forward slash
                arcname = filename
                zf.write(src, arcname)
                entries.append(arcname)
                print(f"  + {arcname}")
        
        # Add package files with EXPLICIT forward slash paths
        for pkg_name in PACKAGES:
            pkg_dir = staging_dir / pkg_name
            if pkg_dir.exists():
                for py_file in sorted(pkg_dir.glob("*.py")):
                    # CRITICAL: Use forward slash explicitly!
                    # Do NOT use os.path.join() on Windows - it uses backslash
                    arcname = f"{pkg_name}/{py_file.name}"  # Forward slash!
                    zf.write(py_file, arcname)
                    entries.append(arcname)
                    print(f"  + {arcname}")
        
        # Add resource files with EXPLICIT forward slash paths
        for res_dir_name in RESOURCE_DIRS:
            res_dir = staging_dir / res_dir_name
            if res_dir.exists():
                for res_file in sorted(res_dir.rglob("*")):
                    if res_file.is_file():
                        # CRITICAL: Use forward slash explicitly!
                        rel_path = res_file.relative_to(staging_dir)
                        arcname = str(rel_path).replace("\\", "/")  # Force forward slash!
                        zf.write(res_file, arcname)
                        entries.append(arcname)
                        print(f"  + {arcname}")
        
        # Add assets with EXPLICIT forward slash paths
        for src_rel, dst_rel in ASSETS.items():
            dst_file = staging_dir / dst_rel
            if dst_file.exists():
                arcname = dst_rel.replace("\\", "/")  # Force forward slash!
                zf.write(dst_file, arcname)
                entries.append(arcname)
                print(f"  + {arcname}")
    
    print(f"\nCreated {app_zip_path}")
    print(f"Total entries: {len(entries)}")
    
    # Verify the zip paths are correct
    print("\n" + "=" * 60)
    print("VERIFICATION - Checking zip paths")
    print("=" * 60)
    
    with zipfile.ZipFile(app_zip_path, 'r') as zf:
        names = zf.namelist()
        
        # Check for any backslashes (BAD!)
        backslash_paths = [n for n in names if '\\' in n]
        
        # Check for expected forward slash paths (GOOD!)
        has_core_init = 'core/__init__.py' in names
        has_ui_init = 'ui_flet/__init__.py' in names
        
        print(f"\nTotal entries: {len(names)}")
        print(f"Backslash paths found: {len(backslash_paths)}")
        print(f"Has core/__init__.py: {has_core_init}")
        print(f"Has ui_flet/__init__.py: {has_ui_init}")
        
        if backslash_paths:
            print("\n[ERROR] Found backslash paths (will break on Android):")
            for p in backslash_paths[:10]:
                print(f"  BAD: {p}")
            return False
        
        if not has_core_init or not has_ui_init:
            print("\n[ERROR] Missing critical package files!")
            return False
        
        print("\n[OK] All paths use forward slashes (POSIX-compatible)")
        print("\nZip contents:")
        for name in sorted(names):
            print(f"  {name}")
    
    # Print build instructions
    print("\n" + "=" * 60)
    print("BUILD INSTRUCTIONS")
    print("=" * 60)
    print("""
The staging folder is ready. Build the APK with:

    flet build apk --module-name main --project hushove-restaurant-app --product "Hushove Restaurant App" --no-rich-output build_src

IMPORTANT: 
- Use --project hushove-restaurant-app to set the Android package name
- Use --product "Hushove Restaurant App" to set the display name
- Icon is at build_src/assets/icon.png (Flet will use it automatically)

After building, verify with:

    python inspect_apk.py build_src\\build\\apk\\app-release.apk

Then copy the APK:

    copy build_src\\build\\apk\\app-release.apk build\\apk\\
""")
    
    return True


if __name__ == "__main__":
    success = prepare_build()
    sys.exit(0 if success else 1)
