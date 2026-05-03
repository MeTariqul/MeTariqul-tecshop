@echo off
setlocal enabledelayedexpansion

:: ========================================
::   TechShop Django Unified Launcher
:: ========================================

echo ========================================
echo   TechShop E-Commerce System
echo ========================================
echo.

cd /d "%~dp0"
set "PROJECT_DIR=%CD%"

:: 1. Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYVER=%%a"
echo [SUCCESS] Python !PYVER! found.
echo.

:: 2. Virtual Environment
echo [2/6] Managing Virtual Environment...
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
) else (
    echo [INFO] Virtual environment found.
)
call venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated.
echo.

:: 3. Dependencies
echo [3/6] Synchronizing dependencies...
python -m pip install --upgrade pip --quiet
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    echo [SUCCESS] Dependencies installed from requirements.txt.
) else (
    echo [WARNING] requirements.txt not found. Installing core packages...
    pip install Django Pillow django-environ django-decouple whitenoise qrcode[pil] reportlab --quiet
)
echo.

:: 4. Database Migrations
echo [4/6] Running database migrations...
cd techshop
python manage.py migrate --noinput
if errorlevel 1 (
    echo [WARNING] Migrations encountered issues. Checking project structure...
) else (
    echo [SUCCESS] Database is up to date.
)
echo.

:: 5. Administrative Setup
echo [5/6] Ensuring administrative access...
:: Build temp python script for superuser creation to avoid batch syntax issues
set "SUPERUSER_SCRIPT=%TEMP%\ts_create_admin.py"
echo from django.contrib.auth import get_user_model > "%SUPERUSER_SCRIPT%"
echo User = get_user_model() >> "%SUPERUSER_SCRIPT%"
echo if not User.objects.filter^(is_superuser=True^).exists^(^): >> "%SUPERUSER_SCRIPT%"
echo     User.objects.create_superuser^('admin', 'admin@example.com', 'admin123'^) >> "%SUPERUSER_SCRIPT%"
echo     print^('Default admin created: admin / admin123'^) >> "%SUPERUSER_SCRIPT%"
echo else: >> "%SUPERUSER_SCRIPT%"
echo     print^('Admin account already exists.'^) >> "%SUPERUSER_SCRIPT%"

python manage.py shell < "%SUPERUSER_SCRIPT%" >nul 2>&1
del "%SUPERUSER_SCRIPT%"
echo [SUCCESS] Admin check complete.
echo.

:: 6. Launch Server
echo [6/6] Launching TechShop...
echo ========================================
echo   SERVER IS STARTING
echo   URL: http://127.0.0.1:8000
echo   Admin: http://127.0.0.1:8000/admin
echo ========================================
echo.
echo Press Ctrl+C to stop the server.
echo.

:: Open browser automatically
start http://127.0.0.1:8000

python manage.py runserver 127.0.0.1:8000
