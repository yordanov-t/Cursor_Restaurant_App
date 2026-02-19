# ============================================================================
# Android APK Clean Build Script for Hushove Restaurant App
# ============================================================================
# This script performs a complete clean build of the Android APK.
#
# Fixes applied:
# 1. Module name: Uses ONLY main.py (removed main_app.py from build)
# 2. Icon: Embeds icon via assets/icon.png (Flet auto-discovers)
# 3. Double-init: Added guard in main.py to prevent double initialization
#
# Usage:
#   .\clean_build.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  Hushove Restaurant App - CLEAN BUILD" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Step 1: Clean ALL build artifacts
# ============================================================================
Write-Host "[1/7] Cleaning build artifacts..." -ForegroundColor Yellow

# Kill any stuck build processes FIRST
Write-Host "  Killing stuck build daemons..." -ForegroundColor Gray
powershell -ExecutionPolicy Bypass -File kill_build_daemons.ps1

$FoldersToClean = @(
    "build_src",
    "build",
    "dist"
)

foreach ($Folder in $FoldersToClean) {
    if (Test-Path $Folder) {
        Write-Host "  Removing: $Folder" -ForegroundColor Gray
        Remove-Item -Recurse -Force $Folder
    }
}

Write-Host "  Clean complete" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 2: Prepare staging folder
# ============================================================================
Write-Host "[2/7] Preparing staging folder..." -ForegroundColor Yellow

try {
    python prepare_build.py
    if ($LASTEXITCODE -ne 0) {
        throw "prepare_build.py failed"
    }
} catch {
    Write-Host "  ERROR: Failed to prepare build" -ForegroundColor Red
    exit 1
}

Write-Host "  Staging ready" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 2.5: Pre-patch gradle.properties if Android folder exists
# ============================================================================
Write-Host "[2.5/6] Pre-patching Gradle properties..." -ForegroundColor Yellow

if (Test-Path "build_src\build\flutter\android") {
    try {
        powershell -ExecutionPolicy Bypass -File patch_gradle_props.ps1 -AndroidPath "build_src\build\flutter\android"
    } catch {
        Write-Host "  Pre-patch not possible yet (Android folder not generated)" -ForegroundColor Gray
    }
} else {
    Write-Host "  Android folder not yet generated, will patch after build" -ForegroundColor Gray
}

Write-Host ""

# ============================================================================
# Step 3: Verify staging contents
# ============================================================================
Write-Host "[3/5] Verifying staging folder..." -ForegroundColor Yellow

$CriticalFiles = @(
    "build_src\main.py",
    "build_src\flet_app.py",
    "build_src\assets\icon.png",
    "build_src\app.zip"
)

$AllExist = $true
foreach ($File in $CriticalFiles) {
    if (Test-Path $File) {
        Write-Host "  [OK] $File" -ForegroundColor Gray
    } else {
        Write-Host "  [MISSING] $File" -ForegroundColor Red
        $AllExist = $false
    }
}

# Verify main_app.py is NOT in build_src
if (Test-Path "build_src\main_app.py") {
    Write-Host "  [ERROR] main_app.py should NOT be in build_src!" -ForegroundColor Red
    $AllExist = $false
}

if (-not $AllExist) {
    Write-Host ""
    Write-Host "  ERROR: Staging folder is missing critical files" -ForegroundColor Red
    exit 1
}

Write-Host "  Verification passed" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 4: Build APK (with post-bootstrap patching)
# ============================================================================
Write-Host "[4/7] Building APK..." -ForegroundColor Yellow
Write-Host "  This may take 5-10 minutes on first build..." -ForegroundColor Gray
Write-Host ""

# Set NO_SPLASH env var if requested (commented out by default)
# Uncomment next line to disable splash generation and avoid AAPT2 timeout:
# $env:NO_SPLASH = "1"

try {
    # ---- Phase 1: Flet generates Flutter project + builds first APK ----
    $FletCmd = 'flet build apk --module-name main --project hushove-restaurant-app --product "Hushove Restaurant App" --android-adaptive-icon-background "#10B981" --no-rich-output build_src'
    Write-Host "  CMD: $FletCmd" -ForegroundColor Magenta
    
    Invoke-Expression $FletCmd
    if ($LASTEXITCODE -ne 0) {
        throw "flet build failed with exit code $LASTEXITCODE"
    }
    Write-Host "  Flet build complete" -ForegroundColor Green
    Write-Host ""

    # ---- Phase 2: Patch AndroidManifest.xml ----
    Write-Host "[5/7] Patching AndroidManifest.xml..." -ForegroundColor Yellow
    $ManifestPath = "build_src\build\flutter\android\app\src\main\AndroidManifest.xml"
    if (Test-Path $ManifestPath) {
        $content = Get-Content $ManifestPath -Raw
        $changed = $false
        if ($content -notmatch 'extractNativeLibs') {
            $content = $content -replace '(<application\b)', '$1 android:extractNativeLibs="true"'
            $changed = $true
            Write-Host "  Added: android:extractNativeLibs=true" -ForegroundColor Gray
        }
        if ($content -notmatch 'usesCleartextTraffic') {
            $content = $content -replace '(<application\b)', '$1 android:usesCleartextTraffic="true"'
            $changed = $true
            Write-Host "  Added: android:usesCleartextTraffic=true" -ForegroundColor Gray
        }
        if ($changed) {
            Set-Content -Path $ManifestPath -Value $content -NoNewline
            Write-Host "  Manifest patched" -ForegroundColor Green
        } else {
            Write-Host "  Manifest already has required attributes" -ForegroundColor Gray
        }
    } else {
        Write-Host "  WARNING: AndroidManifest.xml not found" -ForegroundColor Yellow
    }
    Write-Host ""

    # ---- Phase 3: Re-build APK with patched manifest ----
    Write-Host "[6/7] Re-building APK with patched manifest..." -ForegroundColor Yellow

    $FlutterProject = "build_src\build\flutter"
    $AndroidPath = "$FlutterProject\android"
    $GradlewPath = Join-Path $AndroidPath "gradlew.bat"
    $SitePackages = Join-Path $PWD "build_src\build\site-packages"

    if ((Test-Path $GradlewPath) -and (Test-Path $SitePackages)) {
        $env:SERIOUS_PYTHON_SITE_PACKAGES = $SitePackages
        Write-Host "  SERIOUS_PYTHON_SITE_PACKAGES=$SitePackages" -ForegroundColor Gray
        Write-Host "  Running gradlew assembleRelease..." -ForegroundColor Gray

        Push-Location $AndroidPath
        & .\gradlew.bat app:assembleRelease --no-daemon 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
        $GradleExit = $LASTEXITCODE
        Pop-Location

        if ($GradleExit -eq 0) {
            $RebuiltApk = "$FlutterProject\build\app\outputs\flutter-apk\app-release.apk"
            $TargetApk = "build_src\build\apk\app-release.apk"
            if (Test-Path $RebuiltApk) {
                Copy-Item $RebuiltApk $TargetApk -Force
                Write-Host "  Patched APK ready" -ForegroundColor Green
            } else {
                Write-Host "  Rebuilt APK not at expected path, using original" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  Gradle re-build failed (exit $GradleExit), using original APK" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  Cannot re-build: gradlew or site-packages missing, using original APK" -ForegroundColor Yellow
    }
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "  ERROR: APK build failed - $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "  APK build complete" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 5: Locate and copy APK
# ============================================================================
Write-Host "[5/7] Locating APK..." -ForegroundColor Yellow

$ApkPath = "build_src\build\apk\app-release.apk"
if (-not (Test-Path $ApkPath)) {
    Write-Host "  ERROR: APK not found at: $ApkPath" -ForegroundColor Red
    exit 1
}

$ApkSize = (Get-Item $ApkPath).Length / 1MB
Write-Host "  APK Location: $ApkPath" -ForegroundColor Gray
Write-Host "  APK Size:     $([math]::Round($ApkSize, 2)) MB" -ForegroundColor Gray

# Copy to dist folder
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$DistDir = "dist\apk\$Timestamp"
New-Item -ItemType Directory -Force -Path $DistDir | Out-Null
Copy-Item $ApkPath "$DistDir\app-release.apk" -Force

# Create latest symlink
$LatestDir = "dist\apk\latest"
if (Test-Path $LatestDir) {
    Remove-Item -Recurse -Force $LatestDir
}
New-Item -ItemType Directory -Force -Path $LatestDir | Out-Null
Copy-Item $ApkPath "$LatestDir\app-release.apk" -Force

Write-Host "  APK copied to: $DistDir\app-release.apk" -ForegroundColor Gray
Write-Host ""
Write-Host "  Build complete" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 6: Final cleanup - stop build daemons
# ============================================================================
Write-Host "[6/7] Final daemon cleanup..." -ForegroundColor Yellow

powershell -ExecutionPolicy Bypass -File kill_build_daemons.ps1

Write-Host "  Cleanup complete" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Step 7: Verification
# ============================================================================
Write-Host "[7/7] Verifying APK..." -ForegroundColor Yellow

$LatestApkPath = "$LatestDir\app-release.apk"
if (Test-Path $LatestApkPath) {
    $ApkSize = (Get-Item $LatestApkPath).Length / 1MB
    Write-Host "  APK verified: $([math]::Round($ApkSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "  Warning: APK not found at expected location" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "APK Location:" -ForegroundColor Cyan
Write-Host "  $LatestDir\app-release.apk" -ForegroundColor White
Write-Host ""
Write-Host "Install on device:" -ForegroundColor Cyan
Write-Host "  adb install -r dist\apk\latest\app-release.apk" -ForegroundColor White
Write-Host ""
Write-Host "Monitor logs (if issues occur):" -ForegroundColor Cyan
Write-Host "  adb logcat -c" -ForegroundColor White
Write-Host "  adb logcat | findstr /i `"python flet serious_python Bootstrap crash`"" -ForegroundColor White
Write-Host ""
Write-Host "Pull crash log (if white screen):" -ForegroundColor Cyan
Write-Host "  adb pull /data/data/com.flet.hushove_restaurant_app/files/flet/app/crash.log" -ForegroundColor White
Write-Host ""
