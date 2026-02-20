# ============================================================================
# Android APK Build Pipeline for Hushove Restaurant App
# ============================================================================
# This script automates the complete build process for Android APK.
#
# Prerequisites (must be installed):
# - Python 3.8+ with flet package
# - Flutter SDK (installed via `flet build` if not present)
# - Android SDK with licenses accepted
# - Java JDK 11+
#
# Usage:
#   .\build_android.ps1           # Build APK
#   .\build_android.ps1 -Clean    # Clean build (removes old artifacts first)
#
# Output:
#   build_src\build\apk\app-release.apk  (main output)
#   dist\apk\<timestamp>\app-release.apk (timestamped copy)
# ============================================================================

param(
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Step {
    param([string]$Message)
    Write-Host "`n[BUILD STEP] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# ============================================================================
# Configuration
# ============================================================================
$ProjectRoot = $PSScriptRoot
$BuildSrcDir = Join-Path $ProjectRoot "build_src"
$DistDir = Join-Path $ProjectRoot "dist"
$ApkDistDir = Join-Path $DistDir "apk"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$TimestampedDistDir = Join-Path $ApkDistDir $Timestamp

# Build configuration
$ModuleName = "main"
$ProjectName = "hushove-restaurant-app"
$ProductName = "Hushove Restaurant App"

Write-Host "============================================================================" -ForegroundColor Magenta
Write-Host "  Hushove Restaurant App - Android APK Build Pipeline" -ForegroundColor Magenta
Write-Host "============================================================================" -ForegroundColor Magenta
Write-Host "Project Root:   $ProjectRoot"
Write-Host "Module Name:    $ModuleName"
Write-Host "Project Name:   $ProjectName"
Write-Host "Product Name:   $ProductName"
Write-Host "Timestamp:      $Timestamp"
Write-Host ""

# ============================================================================
# Step 1: Environment Check
# ============================================================================
Write-Step "Checking build environment..."

# Check Python
try {
    $PythonVersion = python --version 2>&1
    Write-Host "  Python: $PythonVersion" -ForegroundColor Gray
} catch {
    Write-Error-Custom "Python not found. Please install Python 3.8+ and add to PATH."
    exit 1
}

# Check Flet
try {
    $FletCheck = python -c "import flet; print(f'Flet {flet.__version__}')" 2>&1
    Write-Host "  $FletCheck" -ForegroundColor Gray
} catch {
    Write-Error-Custom "Flet not installed. Run: pip install flet"
    exit 1
}

Write-Success "Environment check passed"

# ============================================================================
# Step 2: Clean old artifacts (if requested)
# ============================================================================
if ($Clean) {
    Write-Step "Cleaning old build artifacts..."
    
    if (Test-Path $BuildSrcDir) {
        Remove-Item -Recurse -Force $BuildSrcDir
        Write-Host "  Removed: $BuildSrcDir" -ForegroundColor Gray
    }
    
    Write-Success "Clean complete"
}

# ============================================================================
# Step 3: Prepare build staging folder
# ============================================================================
Write-Step "Preparing build staging folder..."

try {
    python prepare_build.py
    if ($LASTEXITCODE -ne 0) {
        throw "prepare_build.py failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Error-Custom "Failed to prepare build: $_"
    exit 1
}

Write-Success "Staging folder prepared"

# ============================================================================
# Step 4: Verify staging folder
# ============================================================================
Write-Step "Verifying staging folder..."

$RequiredFiles = @(
    "main.py",
    "flet_app.py",
    "db.py",
    "core/__init__.py",
    "ui_flet/__init__.py",
    "app.zip",
    "assets/icon.png"
)

$AllFilesExist = $true
foreach ($File in $RequiredFiles) {
    $FilePath = Join-Path $BuildSrcDir $File
    if (Test-Path $FilePath) {
        Write-Host "  [OK] $File" -ForegroundColor Gray
    } else {
        Write-Error-Custom "Missing: $File"
        $AllFilesExist = $false
    }
}

if (-not $AllFilesExist) {
    Write-Error-Custom "Staging folder is missing required files."
    exit 1
}

Write-Success "Staging folder verified"

# ============================================================================
# Step 5: Build APK
# ============================================================================
Write-Step "Building APK..."

# Build the flet build command
$BuildArgs = @(
    "build",
    "apk",
    "--module-name", $ModuleName,
    "--project", $ProjectName,
    "--product", $ProductName,
    "--no-rich-output",
    $BuildSrcDir
)

Write-Host "  Command: flet $($BuildArgs -join ' ')" -ForegroundColor Gray
Write-Host ""
Write-Host "  This may take 5-10 minutes on first build (downloads Flutter SDK)..." -ForegroundColor Yellow
Write-Host ""

try {
    & flet $BuildArgs
    if ($LASTEXITCODE -ne 0) {
        throw "flet build failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Error-Custom "APK build failed: $_"
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Android SDK licenses not accepted - run: flutter doctor --android-licenses"
    Write-Host "  2. Java JDK not installed or not in PATH"
    Write-Host "  3. Flutter SDK download failed - check internet connection"
    Write-Host ""
    exit 1
}

Write-Success "APK build complete"

# ============================================================================
# Step 6: Locate and verify APK
# ============================================================================
Write-Step "Locating APK..."

$ApkPath = Join-Path $BuildSrcDir "build\apk\app-release.apk"
if (-not (Test-Path $ApkPath)) {
    Write-Error-Custom "APK not found at expected location: $ApkPath"
    Write-Host ""
    Write-Host "Check the build output above for errors."
    exit 1
}

$ApkSize = (Get-Item $ApkPath).Length / 1MB
Write-Host "  APK Location: $ApkPath" -ForegroundColor Gray
Write-Host "  APK Size:     $([math]::Round($ApkSize, 2)) MB" -ForegroundColor Gray

Write-Success "APK found and verified"

# ============================================================================
# Step 7: Copy to timestamped dist folder
# ============================================================================
Write-Step "Copying APK to dist folder..."

try {
    # Create dist folder structure
    New-Item -ItemType Directory -Force -Path $TimestampedDistDir | Out-Null
    
    # Copy APK
    $DistApkPath = Join-Path $TimestampedDistDir "app-release.apk"
    Copy-Item $ApkPath $DistApkPath -Force
    
    # Create a "latest" symlink/copy
    $LatestDir = Join-Path $ApkDistDir "latest"
    if (Test-Path $LatestDir) {
        Remove-Item -Recurse -Force $LatestDir
    }
    New-Item -ItemType Directory -Force -Path $LatestDir | Out-Null
    Copy-Item $ApkPath (Join-Path $LatestDir "app-release.apk") -Force
    
    Write-Host "  Timestamped: $DistApkPath" -ForegroundColor Gray
    Write-Host "  Latest:      $(Join-Path $LatestDir 'app-release.apk')" -ForegroundColor Gray
    
} catch {
    Write-Warning-Custom "Failed to copy APK to dist folder: $_"
    Write-Warning-Custom "APK is still available at: $ApkPath"
}

Write-Success "APK copied to dist folder"

# ============================================================================
# Build Complete
# ============================================================================
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "APK Location:" -ForegroundColor Cyan
Write-Host "  $DistApkPath" -ForegroundColor White
Write-Host ""
Write-Host "To install on device:" -ForegroundColor Cyan
Write-Host "  adb install -r `"$DistApkPath`"" -ForegroundColor White
Write-Host ""
Write-Host "Or copy to device and install manually." -ForegroundColor Gray
Write-Host ""

# ============================================================================
# Optional: Show next steps
# ============================================================================
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Connect Android device with USB debugging enabled"
Write-Host "  2. Run: adb install -r `"$DistApkPath`""
Write-Host "  3. If black screen occurs, capture logs:"
Write-Host "     adb logcat -c && adb logcat | Select-String -Pattern 'python|flet|crash'"
Write-Host ""
