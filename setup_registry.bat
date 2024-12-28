@echo off
REM Get the directory of the batch file
SET "SCRIPT_DIR=%~dp0"

REM Define paths
SET "SCRIPT_PATH=%SCRIPT_DIR%cut_video.pyw"
SET "ICON_PATH=%SCRIPT_DIR%cut_video_icon.ico"

REM Detect the full path of pythonw.exe
FOR /F "delims=" %%I IN ('where pythonw.exe') DO SET "PYTHON_PATH=%%I"

REM If pythonw.exe is not found, show an error and exit
IF NOT DEFINED PYTHON_PATH (
    echo pythonw.exe not found in PATH. Ensure Python is installed and added to PATH.
    pause
    exit /b
)

for %%X in (mp4 avi) do (
    reg add "HKCR\SystemFileAssociations\.%%X\shell\Cut Video" /ve /d "Cut Video" /f
    reg add "HKCR\SystemFileAssociations\.%%X\shell\Cut Video\command" /ve /t REG_EXPAND_SZ /d "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" \"%%V\"" /f
)

echo Registry entries have been added successfully.
pause
