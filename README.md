# Restaurant Management System

A modern restaurant management application built with Python and Flet, featuring a glassmorphism UI design.

## Features

- **Reservations Management**: Create, edit, and cancel table reservations
- **Table Layout View**: Visual representation of table occupancy with real-time status
- **Multi-language Support**: Bulgarian (default), English, French, Russian
- **Admin Panel**: Manage waiters, sections, tables, and database backups
- **Sections**: Group tables into zones (Main Hall, Garden, etc.)
- **Backup & Restore**: Automatic daily backups with manual restore capability

## Requirements

- Python 3.8+
- Flet 0.21+ (for desktop)
- Flutter SDK (for mobile builds)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Cursor_Restaurant_App

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Desktop (Development)

```bash
# Run with Flet UI (default)
python main_app.py

# Run with legacy Tkinter UI
python main_app.py --legacy
```

### Web

```bash
flet run --web
```

## Building for Mobile

### Prerequisites

1. **Install Flutter SDK**: https://docs.flutter.dev/get-started/install

2. **Accept Android licenses** (required before first build):
   ```bash
   flutter doctor --android-licenses
   ```
   Press `y` to accept all licenses.

3. **Verify setup**:
   ```bash
   flutter doctor
   ```
   Ensure Android toolchain shows no issues.

### Build Android APK

**RECOMMENDED**: Use the staging folder approach for a clean build that excludes all non-essential files:

```powershell
# Windows PowerShell - Clean build (RECOMMENDED)
cd D:\projects\Cursor_Restaurant_App

# Step 1: Create clean staging folder (only Python source files)
python prepare_build.py

# Step 2: Build APK from staging folder
flet build apk --module-name main --clear-cache --no-rich-output build_src

# Step 3: Verify the build contains only code (no .md files)
python inspect_apk.py build_src\build\apk\app-release.apk

# Step 4: Copy APK to main build folder
Copy-Item -Path "build_src\build\apk\app-release.apk" -Destination "build\apk\app-release.apk" -Force
```

```bash
# Linux/macOS - Clean build
cd /path/to/Cursor_Restaurant_App

# Step 1: Create clean staging folder
python prepare_build.py

# Step 2: Build APK from staging folder
flet build apk --module-name main --clear-cache build_src

# Step 3: Verify and copy
python inspect_apk.py build_src/build/apk/app-release.apk
cp build_src/build/apk/app-release.apk build/apk/
```

Output: `build/apk/app-release.apk`

### Quick One-Liner Build

```powershell
# Windows - Single command
python prepare_build.py; flet build apk --module-name main --no-rich-output build_src; Copy-Item build_src\build\apk\app-release.apk build\apk\ -Force
```

### Verify Build (Before Testing)

After building, verify the package contains correct files:

```bash
python verify_build.py
```

This script checks that:
- All required modules (`core/`, `ui_flet/`) are included
- No junk (`.git/`, `.cursor/`, `__pycache__/`) is packaged
- Package structure is correct

### Build Android App Bundle (AAB)

For Google Play Store distribution:

```bash
flet build aab --module-name main --exclude .git .cursor __pycache__ backups build "*.db" "*.pyc" verify_build.py "*.md" settings.json
```

Output: `build/aab/app-release.aab`

### Build iOS (macOS only)

```bash
flet build ipa --exclude .git .cursor __pycache__ backups build "*.db" "*.pyc"
```

### Build Options

| Option | Description |
|--------|-------------|
| `--exclude PATTERNS` | Exclude files/directories from package |
| `--module-name NAME` | Specify entry module (default: main) |
| `--project NAME` | Set project/app name |
| `--org ORG` | Set organization identifier |
| `--build-number N` | Set build number |
| `--build-version X.Y.Z` | Set version string |
| `--clear-cache` | Clear build cache (use if builds fail) |

Example with all options:
```bash
flet build apk \
  --module-name main \
  --exclude .git .cursor __pycache__ backups build "*.db" "*.pyc" "*.md" \
  --project "Restaurant" \
  --org "com.example.restaurant" \
  --build-version "1.0.0" \
  --build-number 1
```

## Project Structure

```
Cursor_Restaurant_App/
├── main.py              # Flet build entry point (Android/iOS)
├── main_app.py          # Desktop entry point (Flet/Tkinter)
├── flet_app.py          # Main Flet application
├── db.py                # Database manager (thread-safe SQLite)
├── pyproject.toml       # Project config
├── verify_build.py      # Build verification script
├── core/                # Business logic services
│   ├── __init__.py      # Package exports
│   ├── reservation_service.py
│   ├── table_layout_service.py
│   ├── backup_service.py
│   ├── storage.py       # Cross-platform storage utilities
│   └── time_utils.py
├── ui_flet/             # Flet UI components
│   ├── __init__.py      # Package exports
│   ├── theme.py         # Glassmorphism design system + touch helpers
│   ├── i18n.py          # Internationalization
│   ├── app_state.py     # Application state
│   ├── action_panel.py  # Right-side action panel
│   ├── compat.py        # Flet version compatibility
│   ├── reservations_screen_v3.py
│   ├── table_layout_screen_v2.py
│   └── admin_screen_v2.py
├── backups/             # Database backups (auto-created at runtime)
├── restaurant.db        # SQLite database (auto-created at runtime)
└── settings.json        # User settings (auto-created at runtime)
```

## Mobile/Android Features

The app is designed to work seamlessly on Android/iOS:

### Cross-Platform Storage

On mobile devices, the app automatically stores data in the correct app-specific directory:
- **Database**: Created in app storage on first run (not bundled)
- **Backups**: Stored in app storage directory
- **Settings**: Language preferences persist correctly

### Touch-Friendly UI

- Touch-friendly tap targets (minimum 48dp)
- Scrollable lists support touch/drag scrolling
- Action panels work on smaller screens

### Import Bootstrap

The app includes a robust bootstrap mechanism (`main.py`) that:
1. Detects if running on Android (Serious-Python runtime)
2. Searches for the correct app root containing `core/`
3. Adds the correct path to `sys.path` for imports
4. Handles both extracted directories and zipimport from `app.zip`

## Admin Access

- **Username**: `admin`
- **Password**: `password`

## Database

The application uses SQLite with automatic schema creation. Data is stored in `restaurant.db`.

### Backup & Restore

- **Automatic**: Daily backup created on app startup
- **Manual**: Create/restore backups from Admin → Архивиране
- **Location**: App storage directory (mobile) or `backups/` folder (desktop)

## Troubleshooting

### SQLite Threading Errors

The application uses per-call database connections to ensure thread safety with Flet's multi-threaded event handlers. If you encounter threading errors, ensure you're using the latest `db.py`.

### Android Build Fails

1. Run `flutter doctor` to check setup
2. Accept licenses: `flutter doctor --android-licenses`
3. Ensure Android SDK is installed and configured
4. Try clearing cache: `flet build apk --clear-cache --module-name main --exclude ...`

### Build Contains Junk Files

If `python verify_build.py` shows `.git/` or other junk in the package:

1. **Use `--exclude` flag** (mandatory for clean builds):
   ```bash
   flet build apk --module-name main --exclude .git .cursor __pycache__ backups build "*.db"
   ```

2. **Clear cache and rebuild**:
   ```bash
   flet build apk --clear-cache --module-name main --exclude .git .cursor __pycache__ backups build "*.db"
   ```

### ModuleNotFoundError (Runtime on Android)

If the app crashes on Android with "ModuleNotFoundError: No module named 'core'":

1. **Check bootstrap logs** (via `adb logcat`):
   ```bash
   adb logcat | findstr Bootstrap
   ```
   
   Expected output:
   ```
   [Bootstrap] FOUND physical core/ at: /data/.../flet/app
   [Bootstrap] SUCCESS: import core -> ...
   ```

2. **If core/ is missing from package**:
   - Verify with: `python verify_build.py`
   - Rebuild with `--clear-cache`

3. **If core/ is inside app.zip**:
   - The bootstrap should handle this automatically by adding `app.zip` to `sys.path`
   - Check logs for: `[Bootstrap] FOUND core/ inside zip: ...`

### Database Issues on Android

The app uses `FLET_APP_STORAGE_DATA` environment variable for Android storage. The database and backups are stored in the app's internal storage, not the bundled assets.

## License

[Add your license here]
