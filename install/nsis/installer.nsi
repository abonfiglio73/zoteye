!include "MUI2.nsh"
!include "nsDialogs.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

!searchparse /file "..\..\src\config.py" `APP_NAME = "` APP_NAME `"`
!searchparse /file "..\..\src\config.py" `APP_VERSION = "` APP_VERSION `"`
!searchparse /file "..\..\src\config.py" `AUTHOR = "` PUBLISHER `"`

!tempfile sizefolder
!system 'python "${__FILEDIR__}\..\..\src\utils\calcsize.py" > "${sizefolder}"'
!define /file ESTIMATED_SIZE_KB "${sizefolder}"
!delfile "${sizefolder}"

Name "${APP_NAME}"
OutFile "..\build\${APP_NAME}_Installer.exe"
InstallDir "$LOCALAPPDATA\Programs\${APP_NAME}"
RequestExecutionLevel user
SetCompress auto
SetCompressor lzma

!define MUI_ABORTWARNING
!define MUI_ICON "..\..\assets\icons\${APP_NAME}.ico"
!define MUI_UNICON "..\..\assets\icons\uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "..\..\assets\images\header.bmp"
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADER_TRANSPARENT_TEXT
!define MUI_WELCOMEFINISHPAGE_BITMAP "..\..\assets\images\welcome.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP_NOSTRETCH

Var INST_PYTHON
!macro FindPython VERSION

    ${If} $INST_PYTHON == ""
        ReadRegStr $INST_PYTHON HKCU \
            "SOFTWARE\Python\PythonCore\${VERSION}\InstallPath" ""
    ${EndIf}

    ${If} $INST_PYTHON == ""
        ReadRegStr $INST_PYTHON HKLM \
            "SOFTWARE\Python\PythonCore\${VERSION}\InstallPath" ""
    ${EndIf}

    ${If} $INST_PYTHON == ""
        ReadRegStr $INST_PYTHON HKLM \
            "SOFTWARE\WOW6432Node\Python\PythonCore\${VERSION}\InstallPath" ""
    ${EndIf}

!macroend

Var PYTHON_INSTALLER
Var DELETE_USER_DATA

!define MUI_WELCOMEPAGE_TITLE "$(WELCOME_TITLE)"
!define MUI_WELCOMEPAGE_TEXT "$(WELCOMEPAGE_TEXT)"
!define MUI_LICENSEPAGE_CHECKBOX
!define MUI_LICENSEPAGE_CHECKBOX_TEXT "$(LICENSEPAGE_CHECKBOX_TEXT)"
!define MUI_LICENSEPAGE_CHECKBOX_NOTCHECKED "$(LICENSEPAGE_CHECKBOX_NOTCHECKED)"
!define MUI_FINISHPAGE_TITLE "$(FINISHPAGE_TITLE)"
!define MUI_FINISHPAGE_TEXT "$(FINISHPAGE_TEXT)"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_NAME}.exe"
!define MUI_FINISHPAGE_RUN_TEXT "$(FINISHPAGE_RUN_TEXT)"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Italian"

LangString WELCOME_TITLE ${LANG_ENGLISH} "Installing ${APP_NAME}"
LangString WELCOMEPAGE_TEXT ${LANG_ENGLISH} "Welcome to the ${APP_NAME} setup wizard.$\r$\nThe application will be installed in your user area and Python 3.11-3.14 will be checked automatically."
LangString PREVIOUS_VERSION_FOUND ${LANG_ENGLISH} "A previous version of ${APP_NAME} was detected and will be removed before continuing."
LangString REMOVE_PREVIOUS ${LANG_ENGLISH} "A previous version of ${APP_NAME} was detected and will be removed before continuing."
LangString REMOVED_PREVIOUS ${LANG_ENGLISH} "Uninstallation completed."
LangString SPACE_REQUIRED ${LANG_ENGLISH} "Space required (estimated): "
LangString FINISHPAGE_TITLE ${LANG_ENGLISH} "Installation completed."
LangString FINISHPAGE_TEXT ${LANG_ENGLISH} "The installation of ${APP_NAME} has been completed successfully!"
LangString LICENSEPAGE_CHECKBOX_TEXT ${LANG_ENGLISH} "I accept the terms of the license"
LangString LICENSEPAGE_CHECKBOX_NOTCHECKED ${LANG_ENGLISH} "You must accept the license terms to proceed with the installation."
LangString FINISHPAGE_RUN_TEXT ${LANG_ENGLISH} "Run ${APP_NAME} now"
LangString BRANDING_TEXT ${LANG_ENGLISH} "Installing ${APP_NAME} v${APP_VERSION} by ${PUBLISHER}"
LangString VERIFY_PYTHON ${LANG_ENGLISH} "Checking for Python 3.11-3.14..."
LangString PYTHON_FOUND ${LANG_ENGLISH} "Python found at"
LangString PYTHON_NOT_FOUND ${LANG_ENGLISH} "Python 3.11-3.14 not found. Downloading Python 3.14.2-amd64..."
LangString DOWNLOAD_PYTHON_FAILED ${LANG_ENGLISH} "Python download failed. Please check your connection and try again."
LangString INSTALLING_PYTHON ${LANG_ENGLISH} "Installing Python 3.14.2-amd64..."
LangString INSTALL_PYTHON_FAILED ${LANG_ENGLISH} "Automatic Python installation failed. Please install it manually from https://www.python.org/downloads/"
LangString CREATE_VENV ${LANG_ENGLISH} "Creating virtual environment..."
LangString INSTALL_DEPENDENCIES ${LANG_ENGLISH} "Installing dependencies..."
LangString DELETE_USER_DATA ${LANG_ENGLISH} "Do you want to remove the folder data $LOCALAPPDATA\${APP_NAME} as well?"

LangString WELCOME_TITLE ${LANG_ITALIAN} "Installazione di ${APP_NAME}"
LangString WELCOMEPAGE_TEXT ${LANG_ITALIAN} "Benvenuto nell'installazione di ${APP_NAME}.$\r$\nL'applicazione sarà installata nella tua area utente e verrà verificata automaticamente la presenza di Python 3.11-3.14."
LangString PREVIOUS_VERSION_FOUND ${LANG_ITALIAN} "È stata rilevata una versione precedente di ${APP_NAME} che verrà rimossa prima di continuare."
LangString REMOVE_PREVIOUS ${LANG_ITALIAN} "È stata rilevata una versione precedente di ${APP_NAME} che verrà rimossa prima di continuare."
LangString REMOVED_PREVIOUS ${LANG_ITALIAN} "Disinstallazione completata."
LangString SPACE_REQUIRED ${LANG_ITALIAN} "Spazio richiesto (stimato): "
LangString FINISHPAGE_TITLE ${LANG_ITALIAN} "Installazione completata"
LangString FINISHPAGE_TEXT ${LANG_ITALIAN} "L'installazione di ${APP_NAME} è stata completata con successo!"
LangString LICENSEPAGE_CHECKBOX_TEXT ${LANG_ITALIAN} "Accetto i termini della licenza"
LangString LICENSEPAGE_CHECKBOX_NOTCHECKED ${LANG_ITALIAN} "Devi accettare i termini della licenza per continuare l'installazione."
LangString FINISHPAGE_RUN_TEXT ${LANG_ITALIAN} "Avvia ${APP_NAME} ora"
LangString BRANDING_TEXT ${LANG_ITALIAN} "Installazione di ${APP_NAME} v${APP_VERSION} di ${PUBLISHER}"
LangString VERIFY_PYTHON ${LANG_ITALIAN} "Verifica presenza di Python 3.11-3.14..."
LangString PYTHON_FOUND ${LANG_ITALIAN} "Python trovato in"
LangString PYTHON_NOT_FOUND ${LANG_ITALIAN} "Python 3.11-3.14 non trovato. Scaricamento di Python 3.14.2-amd64..."
LangString DOWNLOAD_PYTHON_FAILED ${LANG_ITALIAN} "Download di Python fallito. Controlla la connessione e riprova."
LangString INSTALLING_PYTHON ${LANG_ITALIAN} "Installazione di Python 3.14.2-amd64 in corso..."
LangString INSTALL_PYTHON_FAILED ${LANG_ITALIAN} "Installazione automatica di Python fallita. Installa manualmente da https://www.python.org/downloads/"
LangString CREATE_VENV ${LANG_ITALIAN} "Creazione ambiente virtuale..."
LangString INSTALL_DEPENDENCIES ${LANG_ITALIAN} "Installazione dipendenze..."
LangString DELETE_USER_DATA ${LANG_ITALIAN} "Vuoi rimuovere anche la cartella $LOCALAPPDATA\${APP_NAME}?"

SpaceTexts "$(SPACE_REQUIRED)" ""

Function .onInit
    StrCpy $LANGUAGE ${LANG_ENGLISH}    
    !insertmacro MUI_LANGDLL_DISPLAY
    SectionSetSize "Main installlation" "${ESTIMATED_SIZE_KB}"
FunctionEnd

BrandingText "$(BRANDING_TEXT)"

Function UninstallPreviousVersion

    Var /GLOBAL UninstallString
    ReadRegStr $UninstallString HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString"
    StrCmp $UninstallString "" UninstallDone 
    DetailPrint "$(REMOVE_PREVIOUS)"
    MessageBox MB_OK "$(PREVIOUS_VERSION_FOUND)"
    MessageBox MB_YESNO|MB_ICONQUESTION "$(DELETE_USER_DATA)" IDYES delete_data IDNO keep_data

delete_data:
    StrCpy $DELETE_USER_DATA "1"
    Goto continue

keep_data:
    StrCpy $DELETE_USER_DATA "0"

continue:
    RMDir /r "$INSTDIR"
    ${If} $DELETE_USER_DATA == "1"
         RMDir /r "$LOCALAPPDATA\${APP_NAME}"
    ${EndIf}
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKCU "Software\${APP_NAME}"

  DetailPrint "$(REMOVED_PREVIOUS)"

UninstallDone:
  
FunctionEnd

Section "Main installlation"

    Call UninstallPreviousVersion

    SetOutPath "$INSTDIR"
    File /r /x "utils" "..\..\src\*.py"
    File "..\build\${APP_NAME}.exe"
    File "..\..\requirements.txt"
    File "..\..\src\.env"
    CreateDirectory "$INSTDIR\assets"
    SetOutPath "$INSTDIR\assets"
    File /r "..\..\assets\locales"
    File /r "..\..\assets\theme"
    File /r "..\..\assets\icons"
  
    DetailPrint "$(VERIFY_PYTHON)"

    StrCpy $INST_PYTHON ""
    !insertmacro FindPython "3.14"
    !insertmacro FindPython "3.13"
    !insertmacro FindPython "3.12"
    !insertmacro FindPython "3.11"
  
    ${If} $INST_PYTHON == ""
        DetailPrint "$(PYTHON_NOT_FOUND)"
        InitPluginsDir
        StrCpy $PYTHON_INSTALLER "$PLUGINSDIR\python-installer.exe"
        
        ; Requires Inetc plug-in: https://nsis.sourceforge.io/Inetc_plug-in since NSISdl::download does not support HTTPS
        inetc::get "https://www.python.org/ftp/python/3.14.2/python-3.14.2-amd64.exe" "$PYTHON_INSTALLER" /end
      
        Pop $0
        StrCmp $0 "OK" 0 download_failed

        DetailPrint "$(INSTALLING_PYTHON)"
     
        ExecWait '"$PYTHON_INSTALLER"'

        !insertmacro FindPython "3.14"

        ${If} $INST_PYTHON == ""
            MessageBox MB_OK "$(INSTALL_PYTHON_FAILED)"
            Abort
        ${EndIf}

        Goto python_found

    download_failed:
        MessageBox MB_OK "$(DOWNLOAD_PYTHON_FAILED)"
        Abort
    ${EndIf}

    python_found:
    DetailPrint "$(PYTHON_FOUND): $INST_PYTHON"

    DetailPrint "$(CREATE_VENV)"
    nsExec::ExecToLog '"$INST_PYTHON\python.exe" -m venv "$INSTDIR\venv"'
    
    DetailPrint "$(INSTALL_DEPENDENCIES)"
    nsExec::ExecToLog '"$INSTDIR\venv\Scripts\python.exe" -m pip install --upgrade pip'
    nsExec::ExecToLog '"$INSTDIR\venv\Scripts\python.exe" -m pip install -r "$INSTDIR\requirements.txt"'

    CreateDirectory "$LOCALAPPDATA\${APP_NAME}"
    CreateDirectory "$LOCALAPPDATA\${APP_NAME}\data"
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" '"$INSTDIR\${APP_NAME}.exe"'' "" '"$INSTDIR\assets\icons\${APP_NAME}.ico"''
    CreateShortCut "$SMPROGRAMS\Uninstall.lnk" '"$INSTDIR\Uninstall.exe"'' "" '"$INSTDIR\assets\icons\uninstall.ico"''
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" '"$INSTDIR\${APP_NAME}.exe"'' "" '"$INSTDIR\assets\icons\${APP_NAME}.ico"''

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation" '"$INSTDIR"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" '"$INSTDIR\assets\icons\${APP_NAME}.ico"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "QuietUninstallString" '"$INSTDIR\uninstall.exe" /S'

    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "EstimatedSize" "$0"

    WriteRegDWORD HKCU "Software\${APP_NAME}" "InstallerLanguage" $LANGUAGE

SectionEnd

Section "Uninstall"
    
    MessageBox MB_YESNO|MB_ICONQUESTION "$(DELETE_USER_DATA)" IDYES delete_data IDNO keep_data

delete_data:
    StrCpy $DELETE_USER_DATA "1"
    Goto continue

keep_data:
    StrCpy $DELETE_USER_DATA "0"

continue:
    RMDir /r "$INSTDIR"
    ${If} $DELETE_USER_DATA == "1"
         RMDir /r "$LOCALAPPDATA\${APP_NAME}"
    ${EndIf}
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKCU "Software\${APP_NAME}"

SectionEnd

Function un.onInit
  
    ReadRegDWORD $0 HKCU "Software\${APP_NAME}" "InstallerLanguage"
    StrCmp $0 "" 0 +2
        StrCpy $0 ${LANG_ENGLISH}
    StrCpy $LANGUAGE $0

FunctionEnd