@echo off

REM Function to check the success of each step
:check_success
if %errorlevel% neq 0 (
    echo An error occurred during the last step. Exiting.
    exit /b 1
)
goto :eof

REM Step 1: Install JupyterLab
conda install -c conda-forge jupyterlab --upgrade
call :check_success

REM Step 2: Install JupyterLab Language Server Protocol (LSP) and Python LSP Server
conda install -c conda-forge jupyterlab-lsp -y
call :check_success

conda install -c conda-forge python-lsp-server -y
call :check_success

conda install -c conda-forge jupyter-ai -y
call :check_success

REM Function to get JupyterLab user settings directory
:get_jupyter_settings_dir
for /f "tokens=*" %%i in ('jupyter --paths ^| findstr /r /c:"^ *C:"') do set "jupyter_paths=%%i"
set "settings_dir=%jupyter_paths%\lab\user-settings\@jupyterlab\notebook-extension"
goto :eof

REM Define the settings directory
call :get_jupyter_settings_dir

REM Define the settings file path
set "settings_file=%settings_dir%\tracker.jupyterlab-settings"

REM Create the settings directory if it doesn't exist
if not exist "%settings_dir%" (
    mkdir "%settings_dir%"
)

REM Define the JSON content
set "json_content={
    \"codeCellConfig\": {
        \"lineNumbers\": true,
        \"lineWrap\": true,
        \"autoClosingBrackets\": true
    },
    \"markdownCellConfig\": {
        \"lineNumbers\": true,
        \"matchBrackets\": true,
        \"autoClosingBrackets\": true
    },
    \"rawCellConfig\": {
        \"lineNumbers\": true,
        \"matchBrackets\": true,
        \"autoClosingBrackets\": true
    }
}"

REM Write the JSON content to the settings file
echo %json_content% > "%settings_file%"
call :check_success

echo JupyterLab configuration updated successfully!

