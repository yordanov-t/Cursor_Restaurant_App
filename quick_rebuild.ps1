# Quick rebuild - prepare staging, build APK, clear data, install
Set-Location 'D:\projects\Cursor_Restaurant_App'
$adb = 'C:\Users\Teodor\AppData\Local\Android\Sdk\platform-tools\adb.exe'
$pkg = 'com.flet.hushove_restaurant_app'

# Step 1: Prepare staging
Write-Host '[1/5] Preparing staging...' -ForegroundColor Yellow
python prepare_build.py
if ($LASTEXITCODE -ne 0) { Write-Host 'prepare_build.py FAILED' -ForegroundColor Red; exit 1 }
Write-Host '  OK' -ForegroundColor Green

# Step 2: Flet build (output redirected to avoid encoding crash)
Write-Host '[2/5] Building APK...' -ForegroundColor Yellow
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$proc = Start-Process -FilePath 'flet' `
    -ArgumentList 'build apk --module-name main --project hushove-restaurant-app --product "Hushove Restaurant App" --android-adaptive-icon-background "#10B981" --no-rich-output build_src' `
    -WorkingDirectory 'D:\projects\Cursor_Restaurant_App' `
    -Wait -PassThru -NoNewWindow `
    -RedirectStandardOutput 'build_output.txt' `
    -RedirectStandardError 'build_error.txt'
Write-Host "  flet build exit: $($proc.ExitCode)"
Get-Content 'build_output.txt' | Select-String 'OK|FAIL|Error|built' | Select-Object -Last 5

# Step 3: Patch manifest
Write-Host '[3/5] Patching manifest...' -ForegroundColor Yellow
$mp = 'build_src\build\flutter\android\app\src\main\AndroidManifest.xml'
if (Test-Path $mp) {
    $c = Get-Content $mp -Raw
    $changed = $false
    if ($c -notmatch 'extractNativeLibs') {
        $c = $c -replace '(<application\b[^>]*)(>)', '$1 android:extractNativeLibs="true"$2'
        $changed = $true
    }
    if ($c -notmatch 'usesCleartextTraffic') {
        $c = $c -replace '(<application\b[^>]*)(>)', '$1 android:usesCleartextTraffic="true"$2'
        $changed = $true
    }
    if ($changed) { Set-Content $mp $c -NoNewline; Write-Host '  Manifest patched' -ForegroundColor Green }
    else { Write-Host '  Manifest already patched' -ForegroundColor Gray }
}

# Step 4: Gradle rebuild
Write-Host '[4/5] Gradle rebuild...' -ForegroundColor Yellow
$sp = Join-Path (Get-Location) 'build_src\build\site-packages'
$env:SERIOUS_PYTHON_SITE_PACKAGES = $sp
Push-Location 'build_src\build\flutter\android'
.\gradlew.bat app:assembleRelease --no-daemon 2>&1 | Select-Object -Last 5
$ge = $LASTEXITCODE
Pop-Location
Write-Host "  Gradle exit: $ge"

if ($ge -eq 0) {
    $src = Get-ChildItem 'build_src\build\flutter' -Recurse -Filter 'app-release.apk' | Select-Object -First 1
    if ($src) { Copy-Item $src.FullName 'build_src\build\apk\app-release.apk' -Force; Write-Host '  APK updated' -ForegroundColor Green }
}

# Step 5: Clear data + install
Write-Host '[5/5] Clear data + install...' -ForegroundColor Yellow
& $adb shell am force-stop $pkg
& $adb shell pm clear $pkg
& $adb install -r 'build_src\build\apk\app-release.apk' 2>&1
Write-Host ''
Write-Host 'Done! Launching app in 2s...' -ForegroundColor Green
Start-Sleep -Seconds 2
& $adb logcat -c
& $adb shell am start -n "$pkg/.MainActivity"
Start-Sleep -Seconds 25
Write-Host '=== Python logs ==='
& $adb logcat -d -s "py_bootstrap:*" "py_flet_app:*" 2>&1
