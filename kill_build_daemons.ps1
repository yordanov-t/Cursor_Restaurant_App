# ==============================================================================
# Kill Build Daemons Script
# ==============================================================================
# Kills all Gradle daemons and AAPT2 processes that can cause build failures
# ==============================================================================

Write-Host "[CLEANUP] Killing build daemon processes..." -ForegroundColor Cyan

# Stop Gradle daemon via wrapper if it exists
$GradlewPath = "build_src\build\flutter\android\gradlew.bat"
if (Test-Path $GradlewPath) {
    Write-Host "  Running gradlew --stop..." -ForegroundColor Gray
    try {
        Push-Location (Split-Path $GradlewPath -Parent)
        & ".\gradlew.bat" --stop 2>&1 | Out-Null
        Pop-Location
        Write-Host "  Gradle daemon stopped via wrapper" -ForegroundColor Green
    } catch {
        Pop-Location
        Write-Host "  Could not stop via wrapper (may not be running)" -ForegroundColor Gray
    }
}

# Kill Gradle daemon processes
$GradleProcesses = Get-Process -ErrorAction SilentlyContinue | Where-Object { 
    $_.ProcessName -like "*java*" -and 
    $_.CommandLine -like "*GradleDaemon*"
}

if ($GradleProcesses) {
    Write-Host "  Killing $($GradleProcesses.Count) Gradle daemon process(es)..." -ForegroundColor Gray
    $GradleProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    Write-Host "  Gradle daemons killed" -ForegroundColor Green
} else {
    Write-Host "  No Gradle daemons running" -ForegroundColor Gray
}

# Kill AAPT2 processes
$Aapt2Processes = Get-Process -ErrorAction SilentlyContinue | Where-Object { 
    $_.ProcessName -like "*java*" -and 
    $_.CommandLine -like "*aapt2*"
}

if ($Aapt2Processes) {
    Write-Host "  Killing $($Aapt2Processes.Count) AAPT2 process(es)..." -ForegroundColor Gray
    $Aapt2Processes | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    Write-Host "  AAPT2 processes killed" -ForegroundColor Green
} else {
    Write-Host "  No AAPT2 processes running" -ForegroundColor Gray
}

# Kill any gradle-related Java processes as fallback
$JavaGradleProcesses = Get-Process -Name "java" -ErrorAction SilentlyContinue | Where-Object {
    $cmd = $_.CommandLine
    $cmd -like "*gradle*" -or $cmd -like "*kotlin*" -or $cmd -like "*android*build*"
}

if ($JavaGradleProcesses) {
    Write-Host "  Killing $($JavaGradleProcesses.Count) gradle-related Java process(es)..." -ForegroundColor Gray
    $JavaGradleProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  Java build processes killed" -ForegroundColor Green
}

Write-Host "[CLEANUP] Daemon cleanup complete" -ForegroundColor Green
Write-Host ""
