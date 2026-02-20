# ==============================================================================
# Gradle Properties Patcher for Android Builds
# ==============================================================================
# This script patches gradle.properties BEFORE the build to prevent:
# 1. Kotlin incremental compilation issues across drive roots (C: vs D:)
# 2. AAPT2 daemon timeouts and resource compilation hangs
#
# Usage: Called automatically by clean_build.ps1 before flet build
# ==============================================================================

param(
    [string]$AndroidPath = "build_src\build\flutter\android"
)

$GradlePropsPath = Join-Path $AndroidPath "gradle.properties"

Write-Host "[GRADLE PATCHER] Checking gradle.properties..." -ForegroundColor Cyan

# If gradle.properties doesn't exist yet, create it
if (-not (Test-Path $GradlePropsPath)) {
    # Create the android folder if it doesn't exist
    $AndroidDir = Split-Path $GradlePropsPath -Parent
    if (-not (Test-Path $AndroidDir)) {
        Write-Host "  Android folder not yet generated, will patch after build" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "  Creating gradle.properties..." -ForegroundColor Gray
    New-Item -ItemType File -Path $GradlePropsPath -Force | Out-Null
}

# Read existing content
$Content = ""
if ((Test-Path $GradlePropsPath) -and ((Get-Item $GradlePropsPath).Length -gt 0)) {
    $Content = Get-Content $GradlePropsPath -Raw
}

# Define reliability fixes
$RequiredProps = @{
    "kotlin.incremental" = "false"
    "org.gradle.caching" = "false"
    "org.gradle.daemon" = "false"
    "org.gradle.workers.max" = "2"
    "android.aapt2DaemonMode" = "false"
    "android.enableAapt2" = "true"
}

# Build new content
$NewLines = @()
$Modified = $false

# Add header if empty
if ([string]::IsNullOrWhiteSpace($Content)) {
    $NewLines += "# Generated gradle.properties for Flet Android build"
    $NewLines += "# Patched by patch_gradle_props.ps1 for build reliability"
    $NewLines += ""
    $Modified = $true
}

# Parse existing properties
$ExistingProps = @{}
if (-not [string]::IsNullOrWhiteSpace($Content)) {
    foreach ($Line in $Content -split "`n") {
        $Trimmed = $Line.Trim()
        if ($Trimmed -and -not $Trimmed.StartsWith("#")) {
            if ($Trimmed -match "^([^=]+)=(.*)$") {
                $ExistingProps[$Matches[1].Trim()] = $Matches[2].Trim()
            }
        }
        $NewLines += $Line
    }
}

# Add reliability fixes section
$NewLines += ""
$NewLines += "# =============================================================================="
$NewLines += "# Build Reliability Fixes (prevent Kotlin/AAPT2 issues)"
$NewLines += "# =============================================================================="

foreach ($Key in $RequiredProps.Keys) {
    $Value = $RequiredProps[$Key]
    
    if ($ExistingProps.ContainsKey($Key)) {
        if ($ExistingProps[$Key] -ne $Value) {
            Write-Host "  Updating $Key = $Value" -ForegroundColor Yellow
            # Replace in content
            $Content = $Content -replace "(?m)^\s*$Key\s*=.*$", "$Key=$Value"
            $Modified = $true
        }
    } else {
        Write-Host "  Adding $Key = $Value" -ForegroundColor Gray
        $NewLines += "$Key=$Value"
        $Modified = $true
    }
}

# Write back if modified
if ($Modified) {
    $FinalContent = $NewLines -join "`n"
    Set-Content -Path $GradlePropsPath -Value $FinalContent -NoNewline
    Write-Host "  gradle.properties patched successfully" -ForegroundColor Green
} else {
    Write-Host "  gradle.properties already contains all fixes" -ForegroundColor Green
}

exit 0
