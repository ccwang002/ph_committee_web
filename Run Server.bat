@echo off

setlocal
call VENV\Scripts\activate.bat
python -m bottle -b localhost:8080 server:app
endlocal

PAUSE
