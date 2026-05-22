@echo off
chcp 65001 >nul
setlocal

set "APP_EXE=%~dp0SaveImageToLink.exe"
set "APP_PY=%~dp0save_image.py"

echo ========================================
echo   Uninstall SaveImageToLink context menu
echo ========================================
echo.

if exist "%APP_EXE%" (
    "%APP_EXE%" --uninstall-context-menu
) else (
    python "%APP_PY%" --uninstall-context-menu
)

if errorlevel 1 (
    echo.
    echo Uninstall failed.
    exit /b 1
)

echo.
echo Removed for current user.
echo.
pause

