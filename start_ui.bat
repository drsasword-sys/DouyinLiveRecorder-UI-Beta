@echo off
cd /d "%~dp0"
start "DouyinLiveRecorder UI" /min ".venv\Scripts\python.exe" ui.py
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8765
