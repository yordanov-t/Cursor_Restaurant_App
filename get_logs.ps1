$adb = 'C:\Users\Teodor\AppData\Local\Android\Sdk\platform-tools\adb.exe'
$pkg = 'com.flet.hushove_restaurant_app'

Write-Host 'Clearing logcat...'
& $adb logcat -c
Start-Sleep -Seconds 1

Write-Host 'Force stopping app...'
& $adb shell am force-stop $pkg
Start-Sleep -Seconds 2

Write-Host 'Launching app...'
& $adb shell am start -n "$pkg/.MainActivity"
Write-Host 'Waiting 25 seconds...'
Start-Sleep -Seconds 25

Write-Host ''
Write-Host '=== Python logs ==='
& $adb logcat -d -s "py_bootstrap:*" "py_flet_app:*" 2>&1

Write-Host ''
Write-Host '=== Flutter/crash logs ==='
& $adb logcat -d -s "flutter:*" "AndroidRuntime:*" "System.err:*" 2>&1 | Select-Object -Last 30
