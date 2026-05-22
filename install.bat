@echo off
chcp 65001 >nul
setlocal

set "APP_EXE=%~dp0SaveImageToLink.exe"
set "APP_PY=%~dp0save_image.py"

echo ========================================
echo   Install SaveImageToLink context menu
echo ========================================
echo.

if exist "%APP_EXE%" (
    "%APP_EXE%" --install-context-menu
) else (
    python "%APP_PY%" --install-context-menu
)

if errorlevel 1 (
    echo.
    echo Install failed.
    exit /b 1
)

echo.
echo Installed for current user.
echo You can now right-click an Explorer folder background.
echo.
pause

