@echo off
setlocal

set PYTHONROOT=C:\Python34\
set /p PYTHONROOT="Enter Python installation path [default: %PYTHONROOT%]: "
:: Strip trailing backslash.
set PYTHONROOT=%PYTHONROOT:~0,-1%

set PATH=%PYTHONROOT%;%PYTHONROOT%\Scripts;%PATH%

echo Testing Python environment, ...
echo|set /p="- Python version: "
python --version
echo|set /p="- pip version: "
pip --version
echo|set /p="- Current directory: "
echo %CD%
echo.

echo Create virtual env VENV under %CD% ...
python -m venv --clear VENV
call VENV\Scripts\activate.bat
pip install -r requirements.txt
:: pip install bottle jinja2
echo.

echo List installed packages ...
pip freeze
deactivate
endlocal

PAUSE
