!searchparse /file "..\..\src\config.py" `APP_NAME = "` APP_NAME `"`
!define PYTHON_PATH "venv\\Scripts\\pythonw.exe"
!define SCRIPT_PATH "main.py"
!define ICON_PATH "..\..\assets\icons\${APP_NAME}.ico"

OutFile "..\build\${APP_NAME}.exe"
Icon "${ICON_PATH}"
SilentInstall silent
AutoCloseWindow true
RequestExecutionLevel user

Section
    Exec '"$EXEDIR\\${PYTHON_PATH}" "$EXEDIR\\${SCRIPT_PATH}"'
SectionEnd

