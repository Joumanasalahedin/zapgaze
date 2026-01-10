@echo off
REM Build script for ZapGaze Agent standalone executable (Windows)

echo ==========================================
echo Building ZapGaze Agent Standalone
echo ==========================================
echo.

REM Check if PyInstaller is installed
where pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller is not installed.
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements_local.txt

REM Build the executable
echo.
echo Building executable...
cd /d %~dp0\..
pyinstaller agent\build_standalone.spec --clean

REM Check if build was successful
if exist "dist\ZapGazeAgent.exe" (
    echo.
    echo ==========================================
    echo Build successful!
    echo ==========================================
    echo.
    echo Executable location: dist\ZapGazeAgent.exe
    echo.
    echo To test:
    echo   dist\ZapGazeAgent.exe
    echo.
) else (
    echo.
    echo Build failed. Check the output above for errors.
    exit /b 1
)

