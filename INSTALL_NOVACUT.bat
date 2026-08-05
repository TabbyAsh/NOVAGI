@echo off
setlocal
cd /d "%~dp0"
title NovaCut Installer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALL_NOVACUT.ps1"
if errorlevel 1 (
  echo.
  echo NovaCut installation failed. The error is shown above.
  pause
  exit /b 1
)
exit /b 0
