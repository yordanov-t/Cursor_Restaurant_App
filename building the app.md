# Building the App

Complete guide for building the Hushove Restaurant App for Android.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Build Process Details](#build-process-details)
- [Troubleshooting Black Screen](#troubleshooting-black-screen)
- [Code Changes for Android](#code-changes-for-android)
- [Manual Build Steps](#manual-build-steps)

---

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

2. **Flet package**
   ```bash
   pip install flet
   ```

3. **Flutter SDK** (installed automatically by flet build)
   - First build will download Flutter (~1.5 GB)
   - Subsequent builds reuse the cached SDK

4. **Android SDK with licenses accepted**
   ```bash
   flutter doctor --android-licenses
   ```
   Accept all licenses when prompted.

5. **Java JDK 11 or higher**
   - Download: https://adoptium.net/
   - Verify: `java -version`

### Optional Tools

- **ADB (Android Debug Bridge)** for installing and debugging
  - Comes with Android SDK
  - Verify: `adb version`

---

## Quick Start

### Automated Build (Recommended)

**Windows PowerShell:**
```powershell
.\build_android.ps1
```

**Options:**
```powershell
.\build_android.ps1 -Clean    # Clean build (removes old artifacts)
```

**Output:**
- `dist/apk/latest/app-release.apk` (always the latest build)
- `dist/apk/YYYY-MM-DD_HH-mm-ss/app-release.apk` (timestamped archive)

### Install on Device

```bash
adb install -r dist/apk/latest/app-release.apk
```

Or copy the APK to your device and install manually.

---

## Build Process Details

The build process consists of 7 steps:

### Step 1: Environment Check
- Verifies Python, Flet, and icon file exist
- Fails early if prerequisites are missing

### Step 2: Clean (Optional)
- Removes `build_src/` folder if `-Clean` flag is used
- Ensures fresh build without cached artifacts

### Step 3: Prepare Staging Folder
- Runs `python prepare_build.py`
- Creates `build_src/` with all app source code
- **CRITICAL:** Creates `app.zip` with POSIX-style paths (forward slashes)
  - Windows creates zip entries with backslashes by default
  - These break on Android/Linux
  - Our script explicitly uses forward slashes

**Files copied to staging:**
- Root files: `main.py`, `main_app.py`, `flet_app.py`, `db.py`, `requirements.txt`
- Packages: `core/` (all .py files), `ui_flet/` (all .py files)
- Resources: `resources/` (app icon and other assets)

**Verification:**
- Checks for backslash paths in zip (would break on Android)
- Verifies `core/__init__.py` and `ui_flet/__init__.py` exist

### Step 4: Verify Staging Folder
- Confirms all required files exist in `build_src/`
- Prevents build failures due to missing files

### Step 5: Build APK
Runs:
```bash
flet build apk \
  --module-name main \
  --project hushove-restaurant-app \
  --icon resources/restaurant_app_icon.png \
  --no-rich-output \
  build_src
```

**Build parameters explained:**
- `--module-name main` — Entry point is `main.py` (NOT `main_app.py`)
  - `main.py` bootstraps imports and handles Android-specific path fixes
  - `main_app.py` is for desktop development only
- `--project hushove-restaurant-app` — Sets the Android package name
- `--icon resources/restaurant_app_icon.png` — App icon (launcher icon)
- `--no-rich-output` — Cleaner console output
- `build_src` — Directory containing the app source (staging folder)

**First build:**
- Downloads Flutter SDK (~1.5 GB)
- Takes 5-10 minutes
- Subsequent builds are faster (~2-3 minutes)

### Step 6: Locate and Verify APK
- Finds the APK at `build_src/build/apk/app-release.apk`
- Displays APK size

### Step 7: Copy to Dist Folder
- Creates timestamped folder: `dist/apk/YYYY-MM-DD_HH-mm-ss/`
- Copies APK to timestamped folder for archiving
- Copies APK to `dist/apk/latest/` for easy access

---

## Troubleshooting Black Screen

A black screen on Android means the app started but failed before rendering UI.

### Capture Crash Logs

**Method 1: ADB Logcat (recommended)**
```bash
# Clear old logs, then monitor for errors
adb logcat -c
adb logcat | grep -E "python|flet|crash|FATAL|AndroidRuntime"
```

**Windows PowerShell:**
```powershell
adb logcat -c
adb logcat | Select-String -Pattern "python|flet|crash|FATAL|AndroidRuntime"
```

**Method 2: Check crash.log file**

The app writes a crash log to the device if an exception occurs:
```bash
adb pull /data/data/com.flet.hushove_restaurant_app/files/flet/app/crash.log
```

Then open `crash.log` to see the traceback.

### Common Black Screen Causes

#### 1. Wrong Module Name
**Symptom:** App closes immediately, no errors in log

**Cause:** Used `--module-name main_app` instead of `--module-name main`

**Fix:**
- Use `--module-name main` (correct)
- `main.py` is the Android entry point
- `main_app.py` is for desktop development only

#### 2. Import Errors (ModuleNotFoundError)
**Symptom:** Logcat shows `ModuleNotFoundError: No module named 'core'`

**Cause:** 
- Windows backslash paths in `app.zip`
- Missing files in `build_src/`

**Fix:**
- Ensure `prepare_build.py` creates POSIX-style paths (forward slashes)
- Verify `app.zip` contents don't have backslashes:
  ```bash
  python -c "import zipfile; print([n for n in zipfile.ZipFile('build_src/app.zip').namelist() if '\\\\' in n])"
  ```
  Should print `[]` (empty list)

#### 3. Database Path Issues
**Symptom:** Logcat shows `sqlite3.OperationalError: unable to open database file`

**Cause:** DB path not writable on Android

**Fix:**
- Ensure `core/storage.py` uses `FLET_APP_STORAGE_DATA` environment variable
- Verify in `core/storage.py`:
  ```python
  flet_data_dir = os.environ.get("FLET_APP_STORAGE_DATA")
  if flet_data_dir:
      storage_path = Path(flet_data_dir)
  ```

#### 4. Startup Code Crashes
**Symptom:** Logcat shows exception in `flet_app.py` or service initialization

**Cause:** Code that works on desktop but fails on Android (e.g., file paths, permissions)

**Fix:**
- Check `flet_app.py` startup code
- Add defensive try-except around initialization:
  ```python
  try:
      # Initialization code
  except Exception as e:
      print(f"[ERROR] Startup failed: {e}")
      import traceback
      traceback.print_exc()
  ```

#### 5. Missing Assets
**Symptom:** App crashes after splash screen

**Cause:** Code tries to load files that aren't bundled (fonts, images)

**Fix:**
- Ensure `prepare_build.py` copies `resources/` folder
- Use relative paths, not absolute paths
- Check that `app.zip` contains the resource files

### Debugging Steps

1. **Enable verbose logging:**
   - Check `main.py` — it already logs bootstrap steps
   - Logs print to `adb logcat`

2. **Verify module imports:**
   ```bash
   # Check if core/ exists in app.zip
   python -c "import zipfile; print('core/__init__.py' in zipfile.ZipFile('build_src/app.zip').namelist())"
   ```

3. **Test on desktop first:**
   ```bash
   python main_app.py
   ```
   If it crashes on desktop, fix there first.

4. **Incremental testing:**
   - Comment out sections of startup code
   - Rebuild and test
   - Narrow down the failing code

5. **Check permissions (if needed):**
   Some features may need Android permissions declared.
   See `build_src/build/apk/AndroidManifest.xml` after build.

---

## Code Changes for Android

We made the following changes to support Android builds:

### 1. Created `main.py` (Android Entry Point)
**File:** `main.py`

**Purpose:** Entry point for `flet build apk`. Desktop uses `main_app.py`.

**Key features:**
- **Bootstrap imports** — Ensures `core/` and `ui_flet/` are in `sys.path`
- **Windows backslash path fix** — Detects and corrects zip extraction issues
- **Crash logging** — Writes exceptions to `crash.log` for debugging
- **Unconditional execution** — Calls `ft.app()` at module import time (required by Serious Python)

**Critical logic:**
```python
# Must call ft.app() unconditionally (not under if __name__ == "__main__")
import flet as ft
from flet_app import main as app_main
ft.app(target=app_main)
```

### 2. Cross-Platform Storage (`core/storage.py`)
**Purpose:** Use writable app storage on Android, working directory on desktop.

**Key logic:**
```python
def get_app_storage_path() -> Path:
    flet_data_dir = os.environ.get("FLET_APP_STORAGE_DATA")
    if flet_data_dir:
        return Path(flet_data_dir)  # Android
    return Path.cwd()  # Desktop
```

**Used for:**
- Database: `restaurant.db`
- Backups: `backups/` folder
- Settings: `settings.json`

### 3. Build Preparation Script (`prepare_build.py`)
**Purpose:** Create staging folder with POSIX-compatible `app.zip`.

**Critical:** Windows creates zip entries with backslashes (`core\__init__.py`). On Android, these extract as flat files with backslash in the filename, breaking imports.

**Fix:**
```python
# Explicitly use forward slashes
arcname = f"{pkg_name}/{py_file.name}"  # Force forward slash!
zf.write(py_file, arcname)
```

**Verification:**
```python
backslash_paths = [n for n in names if '\\' in n]
if backslash_paths:
    print("[ERROR] Found backslash paths (will break on Android)")
```

### 4. Fixed Module Entry Point
**Problem:** Used `--module-name main_app` (wrong)

**Fix:** Use `--module-name main` (correct)

`main.py` is the Android entry point. `main_app.py` is for desktop only.

### 5. App Icon Configuration
**Files modified:**
- `pyproject.toml` — Added `resources/restaurant_app_icon.png` to includes
- `prepare_build.py` — Copies `resources/` folder to staging
- Build command — Added `--icon resources/restaurant_app_icon.png`

### 6. Database and Storage Initialization
**File:** `flet_app.py`

**Added:**
```python
from core import ensure_storage_initialized

# Early in main(page):
ensure_storage_initialized()
```

Ensures writable directories exist before creating database on Android.

---

## Manual Build Steps

If you can't use the automated script, follow these manual steps:

### 1. Prepare Staging Folder
```bash
python prepare_build.py
```

**Output:**
- `build_src/` folder with all source files
- `build_src/app.zip` with POSIX paths

### 2. Verify Staging
Check that these files exist:
```bash
build_src/main.py
build_src/flet_app.py
build_src/core/__init__.py
build_src/ui_flet/__init__.py
build_src/app.zip
build_src/resources/restaurant_app_icon.png
```

### 3. Accept Android Licenses (first time only)
```bash
flutter doctor --android-licenses
```

### 4. Build APK
```bash
flet build apk ^
  --module-name main ^
  --project hushove-restaurant-app ^
  --icon resources/restaurant_app_icon.png ^
  --no-rich-output ^
  build_src
```

**Note:** On Linux/macOS, replace `^` with `\` for line continuation.

### 5. Locate APK
```bash
build_src\build\apk\app-release.apk
```

### 6. Install on Device
```bash
adb install -r build_src\build\apk\app-release.apk
```

---

## Build Output Structure

```
project_root/
├── build_src/                     # Staging folder (created by prepare_build.py)
│   ├── main.py                    # Android entry point
│   ├── flet_app.py
│   ├── db.py
│   ├── core/                      # Business logic
│   │   ├── __init__.py
│   │   ├── storage.py
│   │   ├── ...
│   ├── ui_flet/                   # UI components
│   │   ├── __init__.py
│   │   ├── theme.py
│   │   ├── ...
│   ├── resources/                 # Assets
│   │   └── restaurant_app_icon.png
│   ├── app.zip                    # Bundled app (with POSIX paths)
│   └── build/                     # Flet build output
│       └── apk/
│           └── app-release.apk    # Final APK
│
└── dist/                          # Distribution copies
    └── apk/
        ├── latest/
        │   └── app-release.apk    # Always the latest build
        └── YYYY-MM-DD_HH-mm-ss/
            └── app-release.apk    # Timestamped archive
```

---

## Summary Checklist

Before building:
- [ ] Python 3.8+ installed
- [ ] `pip install flet` completed
- [ ] Android SDK licenses accepted (`flutter doctor --android-licenses`)
- [ ] Java JDK 11+ installed
- [ ] Icon file exists at `resources/restaurant_app_icon.png`

To build:
- [ ] Run `.\build_android.ps1` (Windows) or follow manual steps
- [ ] Wait for build to complete (~2-10 minutes)
- [ ] Verify APK at `dist/apk/latest/app-release.apk`

To test:
- [ ] Install: `adb install -r dist/apk/latest/app-release.apk`
- [ ] Launch app on device
- [ ] If black screen, capture logs: `adb logcat`
- [ ] Check for errors in logcat or `crash.log`

---

## Common Commands Reference

```bash
# Build APK (automated)
.\build_android.ps1

# Build APK (manual)
python prepare_build.py
flet build apk --module-name main --project hushove-restaurant-app --icon resources/restaurant_app_icon.png --no-rich-output build_src

# Install on device
adb install -r dist/apk/latest/app-release.apk

# Capture crash logs
adb logcat -c
adb logcat | grep -E "python|flet|crash"

# Pull crash log from device
adb pull /data/data/com.flet.hushove_restaurant_app/files/flet/app/crash.log

# Verify app.zip paths (no backslashes)
python -c "import zipfile; print([n for n in zipfile.ZipFile('build_src/app.zip').namelist() if '\\\\' in n])"

# List connected devices
adb devices

# Uninstall app
adb uninstall com.flet.hushove_restaurant_app
```

---

## Additional Resources

- **Flet Documentation:** https://flet.dev/docs/
- **Flet Packaging Guide:** https://flet.dev/docs/guides/python/packaging-app-for-distribution
- **Android Debug Bridge (ADB):** https://developer.android.com/tools/adb
- **Flutter Doctor:** https://docs.flutter.dev/get-started/install

---

## Change Log

**Latest changes (for Android support):**
- Created `main.py` as Android entry point with bootstrap logic
- Added Windows backslash path fix for zip extraction on Android
- Created `core/storage.py` for cross-platform file storage
- Created `prepare_build.py` to ensure POSIX-compatible `app.zip`
- Created `build_android.ps1` automated build pipeline
- Fixed module name: `main` (correct) instead of `main_app` (wrong)
- Added app icon configuration and bundling
- Added crash logging to `crash.log` for debugging

**Result:** App now builds and runs successfully on Android without black screen.
