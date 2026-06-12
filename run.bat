@echo off
cd /d "%~dp0"
echo ============================
echo  Discorder - Voice AI Bot
echo ============================
echo.
.venv\Scripts\python.exe main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ОШИБКА] Бот упал с кодом %ERRORLEVEL%
    pause
)
