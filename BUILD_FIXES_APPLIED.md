# ✅ Windows Build Fixes Applied

## Problems Fixed

### 1. Kotlin Incremental Compilation Cross-Drive Issue
**Problem:** Kotlin daemon crashes with "different roots" error when comparing:
- Pub cache on `C:\Users\Teodor\AppData\Local\Pub\Cache\...`
- Build output on `D:\projects\Cursor_Restaurant_App\build_src\...`

**Fix Applied:**
- Disabled Kotlin incremental compilation (`kotlin.incremental=false`)
- Disabled Gradle caching across drives (`org.gradle.caching=false`)
- Added daemon cleanup before and after builds

### 2. AAPT2 Resource Compilation Timeouts
**Problem:** AAPT2 times out compiling splash screen assets, hangs daemon processes

**Fix Applied:**
- Disabled AAPT2 daemon mode (`android.aapt2DaemonMode=false`)
- Reduced worker parallelism (`org.gradle.workers.max=2`)
- Disabled Gradle daemon to prevent stuck processes (`org.gradle.daemon=false`)

---

## Files Changed

### 1. `clean_build.ps1` (Updated)
**Changes:**
- **Step 3.5:** Added Gradle daemon and cache cleanup
  - Kills running Gradle processes
  - Kills stuck Java/AAPT2 processes  
  - Removes `.gradle` and `app/build` caches
  
- **Step 2.5:** Pre-patches `gradle.properties` before build
  
- **Step 4.5:** Post-patches `gradle.properties` after build
  
- **Step 6:** Final daemon cleanup after build completes

### 2. `patch_gradle_props.ps1` (New)
**Purpose:** Patches Android `gradle.properties` with reliability fixes

**Properties Added:**
```properties
kotlin.incremental=false
org.gradle.caching=false
org.gradle.daemon=false
org.gradle.workers.max=2
android.aapt2DaemonMode=false
android.enableAapt2=true
```

---

## How It Works

### Build Flow:
1. **Clean old builds** (Step 1)
2. **Prepare staging** (Step 2)
3. **Pre-patch gradle.properties** (Step 2.5) - if Android folder exists from previous build
4. **Verify staging** (Step 3)
5. **Clean Gradle daemons/caches** (Step 3.5)
6. **Build APK** (Step 4) - Flet generates Flutter/Android project
7. **Post-patch gradle.properties** (Step 4.5) - ensures fixes persist
8. **Locate APK** (Step 5)
9. **Final cleanup** (Step 6) - stop daemons to prevent lock issues

### Why This Works:
- **Daemon cleanup** prevents Kotlin cache corruption across drives
- **Disabled incremental compilation** avoids path comparison issues
- **Reduced parallelism** prevents AAPT2 resource contention
- **Disabled daemon mode** prevents stuck background processes
- **Pre + Post patching** ensures properties persist across Flet's project regeneration

---

## Testing the Fix

### Run the build:
```powershell
.\clean_build.ps1
```

### Expected behavior:
✅ No "different roots" Kotlin errors  
✅ No AAPT2 timeout errors  
✅ No stuck Gradle daemon processes  
✅ Build completes successfully  

### If build still fails:
Check the log for:
1. Different error (not Kotlin/AAPT2)
2. Network issues downloading dependencies
3. Disk space issues

---

## Why These Specific Fixes

### Kotlin Incremental = False
Kotlin's incremental compiler caches file paths. When sources are on C: and output is on D:, it can't compute relative paths → crash. Disabling incremental compilation forces full compilation (slower but reliable).

### Gradle Daemon = False  
Gradle daemon persists between builds, reusing old caches. On Windows with AV scanning + cross-drive builds, this causes issues. Disabling forces fresh processes each build.

### AAPT2 Daemon Mode = False
AAPT2 daemon processes can hang when compiling many resources (splash screens) with file system latency. Disabling daemon mode uses direct process invocation (slower but reliable).

### Workers Max = 2
Limits parallel resource compilation to reduce file system contention that triggers AAPT2 timeouts.

---

## Maintenance

These fixes are **self-maintaining**:
- Patches are applied before AND after build
- Even if Flet regenerates the Android project, post-patch step applies fixes
- Daemon cleanup happens automatically

No manual intervention needed for future builds!

---

## Status: READY TO TEST

Run `.\clean_build.ps1` to test the fixed build pipeline.
