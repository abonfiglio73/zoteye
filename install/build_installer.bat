@echo off
chcp 65001 >nul

rem === Configuration ===
set NSIS_PATH=C:\Program Files (x86)\NSIS\makensis.exe
set PROJECT_DIR=%~dp0
set BUILD_DIR=%PROJECT_DIR%build
set LOG_FILE=%BUILD_DIR%\build.log

rem === Initialize log ===
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
echo =============================================== > "%LOG_FILE%"
echo Build executed on %date% at %time% >> "%LOG_FILE%"
echo =============================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

rem === NSIS Compilation: launcher.nsi ===
echo ===============================
echo NSIS Compilation: launcher.nsi
echo ===============================
echo [1/2] NSIS Compilation: launcher.nsi >> "%LOG_FILE%"
"%NSIS_PATH%" "%PROJECT_DIR%\nsis\launcher.nsi" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo ❌ Error during compilation of launcher.nsi
    echo [ERROR] launcher.nsi >> "%LOG_FILE%"
    exit /b 1
)

rem === NSIS Compilation: installer.nsi ===
echo.
echo ===============================
echo NSIS Compilation: installer.nsi
echo ===============================
echo [2/2] NSIS Compilation: installer.nsi >> "%LOG_FILE%"
"%NSIS_PATH%" /INPUTCHARSET UTF8 "%PROJECT_DIR%\nsis\installer.nsi" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo ❌ Error during compilation of installer.nsi
    echo [ERROR] installer.nsi >> "%LOG_FILE%"
    exit /b 1
)

echo.
echo ===============================
echo ✅ All compilations completed with success!
echo ===============================
echo [OK] Build completed with success >> "%LOG_FILE%"

endlocal
