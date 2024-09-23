@echo off

:: Activate the virtual environment
call venv\Scripts\activate

:: Start the three Python programs in separate command windows
start cmd /k python .\main.py
