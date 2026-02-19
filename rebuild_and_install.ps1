# Rebuild APK with patched manifest and install on device
Set-Location 'D:\projects\Cursor_Restaurant_App'

# Step 1: Gradle rebuild with patched manifest
Write-Host '[Step 1] Rebuilding APK with gradle...' -ForegroundColor Yellow
$AndroidPath = 'build_src\build\flutter\android'
$SitePackages = Join-Path (Get-Location) 'build_src\build\site-packages'
$env:SERIOUS_PYTHON_SITE_PACKAGES = $SitePackages
Write-Host "  SERIOUS_PYTHON_SITE_PACKAGES=$SitePackages" -ForegroundColor Gray

Push-Location $AndroidPath
Write-Host '  Running gradlew assembleRelease...' -ForegroundColor Gray
.\gradlew.bat app:assembleRelease --no-daemon 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
$exitCode = $LASTEXITCODE
Pop-Location

Write-Host "  Gradle exit code: $exitCode" -ForegroundColor Gray

if ($exitCode -eq 0) {
    $rebuilt = 'build_src\build\flutter\build\app\outputs\flutter-apk\app-release.apk'
    $target  = 'build_src\build\apk\app-release.apk'
    if (Test-Path $rebuilt) {
        Copy-Item $rebuilt $target -Force
        Write-Host '  Patched APK copied OK' -ForegroundColor Green
    } else {
        # Search for it
        $found = Get-ChildItem 'build_src\build\flutter' -Recurse -Filter 'app-release.apk' -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            Copy-Item $found.FullName $target -Force
            Write-Host "  Found and copied from: $($found.FullName)" -ForegroundColor Green
        } else {
            Write-Host '  Could not find rebuilt APK, keeping original' -ForegroundColor Yellow
        }
    }
} else {
    Write-Host '  Gradle failed, keeping original APK' -ForegroundColor Yellow
}

# Step 2: Copy to dist/latest
Write-Host ''
Write-Host '[Step 2] Copying to dist/latest...' -ForegroundColor Yellow
$LatestDir = 'dist\apk\latest'
if (-not (Test-Path $LatestDir)) { New-Item -ItemType Directory -Force -Path $LatestDir | Out-Null }
Copy-Item 'build_src\build\apk\app-release.apk' "$LatestDir\app-release.apk" -Force
$apkSize = [math]::Round((Get-Item "$LatestDir\app-release.apk").Length / 1MB, 2)
Write-Host "  APK at: $LatestDir\app-release.apk ($apkSize MB)" -ForegroundColor Green

# Step 3: ADB install
Write-Host ''
Write-Host '[Step 3] Installing APK on device...' -ForegroundColor Yellow
$adb = 'C:\Users\Teodor\AppData\Local\Android\Sdk\platform-tools\adb.exe'
if (Test-Path $adb) {
    $result = & $adb install -r "$LatestDir\app-release.apk" 2>&1
    Write-Host "  $result"
    if ($result -match 'Success') {
        Write-Host '  Install SUCCESS' -ForegroundColor Green
    } else {
        Write-Host '  Install may have failed - check device' -ForegroundColor Yellow
    }
} else {
    Write-Host "  adb not found at: $adb" -ForegroundColor Red
}

Write-Host ''
Write-Host '============================================================' -ForegroundColor Green
Write-Host '  DONE' -ForegroundColor Green
Write-Host '============================================================' -ForegroundColor Green
