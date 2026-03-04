@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

if not exist logs mkdir logs
set logFile=logs\job.log

echo ==============================>>"%logFile%"
echo %date% %time% Starting job>>"%logFile%"

if exist .env (
  for /f "usebackq delims=" %%x in (".env") do set "%%x"
)

set apiUrl=http://127.0.0.1:8000

for /f %%s in ('curl -s -o nul -w "%%{http_code}" "%apiUrl%/health"') do set "status=%%s"

if not "!status!"=="200" (
  echo API not running, starting...>>"%logFile%"
  start "" /b cmd /c "py -3.14 app.py"

  set tries=0

:waitLoop
  timeout /t 1 >nul
  set /a tries=!tries!+1

  for /f %%s in ('curl -s -o nul -w "%%{http_code}" "%apiUrl%/health"') do set "status=%%s"

  if "!status!"=="200" (
    echo API started successfully>>"%logFile%"
    goto sendMail
  )

  if !tries! GEQ 10 (
    echo API failed to start>>"%logFile%"
    goto end
  )

  goto waitLoop
)

:sendMail
echo Sending notifications>>"%logFile%"
curl -s -X POST "%apiUrl%/notifications/send" >>"%logFile%"
echo.>>"%logFile%"
echo Job finished>>"%logFile%"

:end
endlocal