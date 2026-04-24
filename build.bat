@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Ensure Python is installed and available in PATH.
    exit /b 1
)

python scripts\package_release.py %*
set EXIT_CODE=%ERRORLEVEL%
if not "%EXIT_CODE%"=="0" (
    echo [ERROR] Package build failed with exit code %EXIT_CODE%.
    exit /b %EXIT_CODE%
)

echo [DONE] VocabChan package build finished.
exit /b 0
