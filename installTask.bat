@echo off
setlocal

set taskName=FootballNotifier
set jobPath=%~dp0runJob.bat

schtasks /query /tn "%taskName%" >nul 2>&1

if %errorlevel%==0 (
    echo Task already exists
) else (
    echo Creating task...
    schtasks /create /sc daily /st 00:00 /tn "%taskName%" /tr "\"%jobPath%\"" /f
)

pause
endlocal