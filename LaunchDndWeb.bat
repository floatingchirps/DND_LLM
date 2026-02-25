@echo off
setlocal
cd /d "%~dp0"

echo Starting D&D Flask web app...
start "DND Flask Server" cmd /k "python flask_web.py"

echo Waiting for server to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser...
start "" "http://127.0.0.1:5000/"

echo Done. You can now use the D&D web app.
endlocal
