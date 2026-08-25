@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" goto run

echo [setup] Creating virtual environment...
py -3 -m venv .venv
if exist ".venv\Scripts\python.exe" goto deps
echo [setup] Python 3 not found. Please install Python 3 first.
pause
exit /b 1

:deps
echo [setup] Installing dependencies (first time, please wait)...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

:run
start "" ".venv\Scripts\pythonw.exe" -m pet.main
endlocal
