@echo off
rem Start the node editor with the Python in the "venv" folder.
rem Make the venv first. See "Quick start" in README.md.
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    echo The venv folder was not found. See "Quick start" in README.md.
    pause
    exit /b 1
)

venv\Scripts\python.exe main.py
