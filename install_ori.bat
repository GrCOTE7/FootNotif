@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"
set "rootDir=%cd%"

if not exist "%rootDir%\.env" (
    echo Warning: %rootDir%\.env not found
)

if exist "%rootDir%\football-admin" (
    if not exist "%rootDir%\football-admin\.env" (
        echo Warning: %rootDir%\football-admin\.env not found
    )
)

where winget >nul 2>&1
if errorlevel 1 (
    echo winget not found. Install Node and Python manually.
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo Node not found, installing with winget...
    winget install -e --id OpenJS.NodeJS.LTS
)

where npm >nul 2>&1
if errorlevel 1 (
    echo npm still not found. Restart terminal or install Node manually.
    exit /b 1
)

where py >nul 2>&1
if errorlevel 1 (
    echo Python not found, installing with winget...
    winget install -e --id Python.Python.3.12
)

where py >nul 2>&1
if errorlevel 1 (
    echo py still not found. Restart terminal or install Python manually.
    exit /b 1
)

if not exist logs mkdir logs

if not exist ".venv" (
    py -3 -m venv .venv
)

set "venvPython=%rootDir%\.venv\Scripts\python.exe"

if not exist "%venvPython%" (
    echo Virtual environment Python not found
    exit /b 1
)

"%venvPython%" -m pip install --upgrade pip

if exist requirements.txt (
    "%venvPython%" -m pip install -r requirements.txt
)

if exist football-admin\package.json (
    cd football-admin
    npm install
    cd /d "%rootDir%"
) else (
    if exist package.json (
        npm install
    )
)

if exist "%rootDir%\installTask.bat" (
    call "%rootDir%\installTask.bat"
) else (
    echo installTask.bat not found
    exit /b 1
)

echo Installation complete
exit /b 0