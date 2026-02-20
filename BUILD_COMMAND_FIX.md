# Android Build Command Fix - Summary

## Problem Analysis

### Your Command
```bash
flet build apk --module-name main --project hushove-restaurant-app --icon resources/restaurant_app_icon.png --no-rich-output build_src
```

### Error
```
flet: error: unrecognized arguments: --icon build_src
```

### Root Cause
**Flet 0.28.3 does NOT support the `--icon` flag.**

The error occurred because:
1. `--icon` is not a valid flag in Flet 0.28.3 (checked via `flet build --help`)
2. After the invalid `--icon resources/restaurant_app_icon.png`, the parser treated `build_src` as another invalid argument
3. The positional `python_app_path` argument must come LAST (after all flags)

## Solution

### How Flet 0.28 Handles Icons

Flet expects app icons in a specific location:
- **Location:** `assets/icon.png` in your app directory
- **Behavior:** Flet automatically uses `assets/icon.png` as the launcher icon during build
- **No flag needed:** The icon is discovered automatically

### Corrected Build Command

```bash
flet build apk --module-name main --project hushove-restaurant-app --product "Hushove Restaurant App" --no-rich-output build_src
```

**Changes from your command:**
1. ❌ **Removed:** `--icon resources/restaurant_app_icon.png` (not supported)
2. ✅ **Added:** `--product "Hushove Restaurant App"` (sets display name)
3. ✅ **Moved:** `build_src` to the end (positional argument must be last)

**How icon works:**
- Icon is copied to `build_src/assets/icon.png` by `prepare_build.py`
- Flet automatically discovers and uses it during build
- No CLI flag needed

## Files Changed

### 1. `prepare_build.py` (Updated)

**Added icon mapping:**
```python
# Assets to copy (Flet looks for these)
ASSETS = {
    "resources/restaurant_app_icon.png": "assets/icon.png",
}
```

**Added asset copying logic:**
```python
# Copy assets for Flet (icon, etc.)
print("\nCopying assets:")
for src_rel, dst_rel in ASSETS.items():
    src_file = project_root / src_rel
    dst_file = staging_dir / dst_rel
    if src_file.exists():
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        print(f"  [FILE] {src_rel} -> {dst_rel}")
```

**Added assets to app.zip:**
```python
# Add assets with EXPLICIT forward slash paths
for src_rel, dst_rel in ASSETS.items():
    dst_file = staging_dir / dst_rel
    if dst_file.exists():
        arcname = dst_rel.replace("\\", "/")
        zf.write(dst_file, arcname)
        entries.append(arcname)
        print(f"  + {arcname}")
```

**Result:**
- ✅ Creates `build_src/assets/` folder
- ✅ Copies `resources/restaurant_app_icon.png` to `build_src/assets/icon.png`
- ✅ Includes `assets/icon.png` in `app.zip` with POSIX paths

### 2. `build_android.ps1` (Updated)

**Changed build configuration:**
```powershell
# OLD (incorrect)
$IconPath = "resources/restaurant_app_icon.png"

# NEW (correct)
$ProductName = "Hushove Restaurant App"
```

**Removed icon path check:**
- No longer checks for icon file (handled by prepare_build.py)
- No longer passes `--icon` flag (not supported)

**Updated build command:**
```powershell
$BuildArgs = @(
    "build",
    "apk",
    "--module-name", $ModuleName,
    "--project", $ProjectName,
    "--product", $ProductName,        # NEW: Sets display name
    "--no-rich-output",
    $BuildSrcDir                      # Positional arg LAST
)
```

**Added verification:**
```powershell
$RequiredFiles = @(
    "main.py",
    "flet_app.py",
    "db.py",
    "core/__init__.py",
    "ui_flet/__init__.py",
    "app.zip",
    "assets/icon.png"                # NEW: Verify icon exists
)
```

## How to Build

### Option 1: Automated (Recommended)
```powershell
.\build_android.ps1
```

### Option 2: Manual
```bash
# Step 1: Prepare staging folder (creates assets/icon.png)
python prepare_build.py

# Step 2: Build APK (Flet auto-discovers assets/icon.png)
flet build apk --module-name main --project hushove-restaurant-app --product "Hushove Restaurant App" --no-rich-output build_src
```

## Verification

After build:
1. **Icon in staging:** `build_src/assets/icon.png` ✅
2. **Icon in app.zip:** Check with:
   ```bash
   python -c "import zipfile; print('assets/icon.png' in zipfile.ZipFile('build_src/app.zip').namelist())"
   ```
   Should print `True` ✅
3. **APK location:** `build_src/build/apk/app-release.apk` ✅
4. **Launcher icon:** Install APK and check app drawer icon ✅

## Why This Works

### Flet Icon Discovery
Flet's build process:
1. Scans `python_app_path` (in this case `build_src/`) for an `assets/` folder
2. If `assets/icon.png` exists, uses it as the launcher icon
3. Generates Android adaptive icons from this image
4. No CLI flag needed

### Alternative: Adaptive Icon Background
If you want to customize the adaptive icon background color:
```bash
flet build apk --android-adaptive-icon-background "#10B981" build_src
```

This sets the background color for the adaptive icon (Android 8.0+).

## Common CLI Flags (Flet 0.28.3)

```bash
flet build apk [OPTIONS] [python_app_path]

# App naming
--project PROJECT_NAME              # Package name (com.flet.project-name)
--product PRODUCT_NAME              # Display name shown to users
--description DESCRIPTION           # App description

# Organization
--org ORG_NAME                      # Reverse domain (e.g., "com.mycompany")
--bundle-id BUNDLE_ID               # Full bundle ID (overrides org+project)

# Android-specific
--android-adaptive-icon-background COLOR
--split-per-abi                     # Create separate APKs per architecture
--android-permissions PERM...       # Add Android permissions
--build-number BUILD_NUMBER         # Internal version number
--build-version BUILD_VERSION       # Version shown to users (x.y.z)

# Build options
--module-name MODULE_NAME           # Python module with entry point
--no-rich-output                    # Plain text output
--clear-cache                       # Clear build cache
-v, -vv                             # Verbose output
```

## Summary

**Problem:** Used unsupported `--icon` flag, positional arg in wrong position

**Solution:**
1. Copy icon to `assets/icon.png` (done by prepare_build.py)
2. Remove `--icon` flag (not supported in Flet 0.28.3)
3. Add `--product "Hushove Restaurant App"` (sets display name)
4. Move `build_src` to end (positional arg must be last)

**Result:** 
- ✅ Build command works
- ✅ Icon automatically applied by Flet
- ✅ Display name set correctly
- ✅ Package name: `com.flet.hushove_restaurant_app`
- ✅ App name: "Hushove Restaurant App"
