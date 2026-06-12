@echo off
cd /d "%~dp0"
echo ============================
echo  Discorder - Voice AI Bot
echo ============================
echo.
uv run main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ОШИБКА] Бот упал с кодом %ERRORLEVEL%
    pause
)
