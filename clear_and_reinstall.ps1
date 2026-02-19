# Clear app data and reinstall to force fresh extraction of app.zip
$adb = 'C:\Users\Teodor\AppData\Local\Android\Sdk\platform-tools\adb.exe'
$pkg = 'com.flet.hushove_restaurant_app'
$apk = 'D:\projects\Cursor_Restaurant_App\dist\apk\latest\app-release.apk'

Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '  Clear App Data + Reinstall' -ForegroundColor Cyan
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host ''

# Step 1: Force stop
Write-Host '[1] Force stopping app...' -ForegroundColor Yellow
& $adb shell am force-stop $pkg
Start-Sleep -Seconds 1
Write-Host '  Done' -ForegroundColor Green

# Step 2: Clear ALL app data (forces fresh extraction of app.zip on next launch)
Write-Host '[2] Clearing app data (forces fresh app.zip extraction)...' -ForegroundColor Yellow
$result = & $adb shell pm clear $pkg 2>&1
Write-Host "  Result: $result" -ForegroundColor Gray
if ($result -match 'Success') {
    Write-Host '  App data cleared OK' -ForegroundColor Green
} else {
    Write-Host '  WARNING: Clear may have failed' -ForegroundColor Yellow
}
Start-Sleep -Seconds 1

# Step 3: Reinstall APK
Write-Host ''
Write-Host '[3] Installing APK...' -ForegroundColor Yellow
$install = & $adb install -r $apk 2>&1
Write-Host "  $install"
if ($install -match 'Success') {
    Write-Host '  Install SUCCESS' -ForegroundColor Green
} else {
    Write-Host '  Install may have failed' -ForegroundColor Yellow
}
Start-Sleep -Seconds 1

# Step 4: Clear logcat
Write-Host ''
Write-Host '[4] Clearing logcat...' -ForegroundColor Yellow
& $adb logcat -c
Write-Host '  Done' -ForegroundColor Green

# Step 5: Launch app
Write-Host ''
Write-Host '[5] Launching app...' -ForegroundColor Yellow
& $adb shell am start -n "$pkg/.MainActivity" 2>&1
Write-Host '  App launched' -ForegroundColor Green
Write-Host ''
Write-Host 'Waiting 20 seconds for app to initialize...' -ForegroundColor Gray
Start-Sleep -Seconds 20

# Step 6: Show key Python log lines
Write-Host ''
Write-Host '[6] Python initialization log:' -ForegroundColor Yellow
& $adb logcat -d -s "py_bootstrap:*" "py_flet_app:*" 2>&1 | Select-Object -Last 30

Write-Host ''
Write-Host '============================================================' -ForegroundColor Green
Write-Host '  Done - check your tablet!' -ForegroundColor Green
Write-Host '============================================================' -ForegroundColor Green
