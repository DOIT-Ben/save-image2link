@echo off
chcp 65001 >nul
setlocal

echo ========================================
echo   Build SaveImageToLink.exe
echo ========================================
echo.

python -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed.
    echo Run: python -m pip install -r requirements-dev.txt
    exit /b 1
)

python -m PyInstaller --onefile --noconsole --icon assets\icon.ico --name SaveImageToLink save_image.py

if errorlevel 1 (
    echo.
    echo Build failed.
    exit /b 1
)

echo.
echo Built: dist\SaveImageToLink.exe
echo.
