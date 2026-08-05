@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NovaCut Local AI Editor

set "PYTHON_CMD="
where py >nul 2>nul && py -3.11 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.11"
if not defined PYTHON_CMD where py >nul 2>nul && py -3.12 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.12"
if not defined PYTHON_CMD where py >nul 2>nul && py -3 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD where python >nul 2>nul && python -c "import sys" >nul 2>nul && set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
  echo.
  echo NovaCut needs Python 3.10 or newer.
  echo Opening the official Python download page...
  start "" "https://www.python.org/downloads/windows/"
  echo.
  echo Install Python with "Add Python to PATH" enabled, then double-click this file again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating NovaCut's private local environment...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto :failed
)

set "PY=.venv\Scripts\python.exe"
set "PIP=.venv\Scripts\python.exe -m pip"

if not exist ".venv\.novacut_ready" (
  echo Installing NovaCut's local components. This happens once...
  %PIP% install --disable-pip-version-check --upgrade pip
  if errorlevel 1 goto :failed
  %PIP% install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto :failed
  echo ready> ".venv\.novacut_ready"
)

if not "%~1"=="" (
  echo Processing dragged-in video: %~nx1
  %PY% -m novacut "%~1" --profile gaming --clips 12
  if errorlevel 1 goto :failed
  echo.
  echo Finished. Results are beside the original video.
  pause
  exit /b 0
)

%PY% -m novacut.app
if errorlevel 1 goto :failed
exit /b 0

:failed
echo.
echo NovaCut could not finish setup or launch.
echo Copy the error above if troubleshooting is needed.
pause
exit /b 1
