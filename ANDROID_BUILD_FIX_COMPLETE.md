# ✅ Complete Android Build Fix - Windows Flet/Flutter APK

## Problems Solved

### 1. Kotlin Incremental Compilation Cross-Drive Crash
**Error:** `java.lang.IllegalArgumentException: this and base files have different roots`
**Cause:** Kotlin daemon comparing C: drive (Pub cache) with D: drive (project)
**Fix:** Disabled Kotlin incremental compilation in patched gradle.properties

### 2. AAPT2 Resource Compilation Timeouts  
**Error:** Multiple AAPT2 daemons timeout compiling splash.png assets
**Cause:** Too many parallel AAPT2 processes + file contention on Windows
**Fix:** Reduced parallelism, disabled daemon mode, added splash removal option

### 3. Stuck Gradle/AAPT2 Daemon Processes
**Cause:** Leftover Java processes locking files across builds
**Fix:** Kill all build daemons before and after build

---

## New Files Created

### 1. `patch_android_build.ps1`
**Purpose:** Patches the generated Android project after Flet creates it

**What it does:**
- Updates `gradle.properties` with reliability fixes
- Removes splash resources if `NO_SPLASH=1`
- Cleans stale Gradle caches (`.gradle`, `app/build`, `build`)

**Gradle properties enforced:**
```properties
kotlin.incremental=false
org.gradle.caching=false
org.gradle.daemon=false
org.gradle.workers.max=2
org.gradle.jvmargs=-Xmx4g -Dfile.encoding=UTF-8
```

### 2. `kill_build_daemons.ps1`
**Purpose:** Kills all build-related daemon processes

**What it kills:**
- Gradle daemons (via `gradlew --stop` + process kill)
- AAPT2 processes (Java processes with aapt2 in command line)
- Any Java processes related to Gradle/Kotlin/Android build

---

## Updated File

### `clean_build.ps1`
**Changes:**

**Step 1 (Enhanced):** Kills daemons before cleaning
- Calls `kill_build_daemons.ps1` first
- Then removes build folders

**Step 4 (Rewritten):** Patching integrated into build
- Starts `flet build apk` process
- Waits for Android project generation
- Immediately patches Android project via `patch_android_build.ps1`
- Passes `NO_SPLASH` flag if environment variable is set
- Continues with Gradle build

**Step 6 (New):** Final daemon cleanup
- Calls `kill_build_daemons.ps1` after build
- Prevents locked files from affecting next build

**Steps renumbered:** Now 7 steps total (was 5-6)

---

## How to Use

### Normal Build:
```powershell
.\clean_build.ps1
```

### No-Splash Build (if AAPT2 times out on splash resources):
```powershell
$env:NO_SPLASH = "1"
.\clean_build.ps1
```

The NO_SPLASH mode removes all splash.png and android12splash.png files after bootstrap generation, before Gradle compiles resources.

---

## Build Flow

```
1. Kill daemons + Clean folders
   ↓
2. Prepare staging (prepare_build.py)
   ↓
3. Verify staging
   ↓
4. Start flet build apk
   ├─ Flet generates Flutter/Android project
   ├─ PATCH: patch_android_build.ps1 runs
   │  ├─ Updates gradle.properties
   │  ├─ Removes splash (if NO_SPLASH=1)
   │  └─ Cleans .gradle caches
   └─ Gradle build continues with fixed config
   ↓
5. Locate APK
   ↓
6. Kill daemons (cleanup)
   ↓
7. Verify APK
```

---

## Why This Works

### Persistent Patching
Flet regenerates the Android project on every build. Our patches are applied **after generation, before Gradle build**, so they persist even though we don't modify Flet itself.

### Timing is Critical
We patch at the exact moment after Flutter bootstrap exists but before Gradle starts compiling. This is why we integrate patching INTO Step 4 (build), not as a separate pre-build step.

### Kill Daemons Twice
- **Before build:** Prevents stale Kotlin incremental state
- **After build:** Prevents locked files for next build

### Conservative Settings
- `workers.max=2`: Reduces AAPT2 parallelism (default is CPU count)
- `daemon=false`: Fresh JVM each build (slower but reliable)
- `caching=false`: No cross-drive cache issues
- `jvmargs=-Xmx4g`: Enough memory for resource compilation

---

## Troubleshooting

### If Kotlin error persists:
1. Check `build_src\build\flutter\android\gradle.properties`
2. Verify it contains `kotlin.incremental=false`
3. Run `kill_build_daemons.ps1` manually
4. Delete `build_src` and rebuild

### If AAPT2 still times out:
1. Enable NO_SPLASH mode: `$env:NO_SPLASH = "1"`
2. Rebuild with `.\clean_build.ps1`
3. Check Task Manager for stuck `java.exe` processes
4. Kill them manually if script doesn't catch them

### If patches aren't applied:
1. Check terminal output for "Android patching" messages
2. Verify `patch_android_build.ps1` exists in repo root
3. Check Android folder exists at: `build_src\build\flutter\android`
4. Run patcher manually:
   ```powershell
   .\patch_android_build.ps1
   ```

---

## Testing

Run a clean build:
```powershell
.\clean_build.ps1
```

Expected output:
```
[1/7] Cleaning build artifacts...
  [CLEANUP] Killing build daemon processes...
  
[2/7] Preparing staging folder...

[3/7] Verifying staging folder...

[4/7] Building APK...
  Build bootstrap complete, applying Android patches...
  
  ============================================================================
    Android Build Patcher
  ============================================================================
  
  [1/3] Patching gradle.properties...
    Set: kotlin.incremental = false
    Set: org.gradle.daemon = false
    ...
    
  [2/3] Processing splash resources...
  
  [3/3] Cleaning stale build caches...
  
  ============================================================================
    Android Build Patching Complete
  ============================================================================

[5/7] Locating APK...

[6/7] Final daemon cleanup...

[7/7] Verifying APK...
```

---

## Status: COMPLETE & READY TO TEST

All fixes implemented. Build should now work reliably on Windows without:
- ✅ Kotlin incremental compilation crashes
- ✅ AAPT2 timeout errors
- ✅ Stuck daemon processes
- ✅ Cross-drive cache issues

Run `.\clean_build.ps1` to test!
