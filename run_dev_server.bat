@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   TechShop Django Dev Server Launcher
echo   (Improved for Windows compatibility)
echo ========================================
echo.

cd /d "%~dp0"

REM Get the current directory path
set "PROJECT_DIR=%CD%"

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo [ERROR] Please install Python 3.11+ from https://www.python.org/downloads/
    timeout /t 5
    exit /b 1
)
echo [SUCCESS] Python found.

REM Check Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYVER=%%a"
echo [INFO] Python version: !PYVER!

REM Check if virtual environment exists
if not exist "%PROJECT_DIR%\techshop\venv\Scripts\python.exe" (
    echo.
    echo [INFO] Virtual environment not found. Creating one...
    cd techshop
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        timeout /t 5
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
) else (
    echo [INFO] Virtual environment found.
)

REM Activate virtual environment
cd /d "%PROJECT_DIR%"
echo.
echo [INFO] Activating virtual environment...
call "techshop\venv\Scripts\activate.bat" 2>nul
if errorlevel 1 (
    echo [WARNING] Could not activate venv normally. Adjusting PATH...
    set "PATH=%PROJECT_DIR%\techshop\venv\Scripts;%PATH%"
    set "VIRTUAL_ENV=%PROJECT_DIR%\techshop\venv"
)
echo [SUCCESS] Virtual environment activated.

REM Upgrade pip
echo.
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet 2>nul

REM Install dependencies if needed
echo.
echo [INFO] Checking dependencies...
python -m pip show Django >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Django...
    pip install Django==4.2.7 --quiet
)
python -m pip show django-environ >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing django-environ...
    pip install django-environ==0.11.2 --quiet
)
python -m pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Pillow...
    pip install Pillow --quiet
)
python -m pip show reportlab >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing reportlab...
    pip install reportlab==4.1.0 --quiet
)
python -m pip show qrcode >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing qrcode...
    pip install "qrcode[pil]==8.0" --quiet
)
python -m pip show whitenoise >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing whitenoise...
    pip install whitenoise==6.6.0 --quiet
)
echo [SUCCESS] All dependencies installed.

REM Check if database exists, if not run migrations
cd /d "%PROJECT_DIR%\techshop"
if not exist "db.sqlite3" (
    echo.
    echo [INFO] Database not found. Running initial migrations...
    python manage.py migrate --noinput
    if errorlevel 1 (
        echo [WARNING] Migrations had issues, but continuing...
    ) else (
        echo [SUCCESS] Migrations complete.
    )
    
    echo.
    echo [INFO] Creating superuser (if needed)...
    echo from django.contrib.auth import get_user_model > "%TEMP%\createsuperuser.py"
    echo User = get_user_model() >> "%TEMP%\createsuperuser.py"
    echo if not User.objects.filter^(is_superuser=True^).exists^(^): >> "%TEMP%\createsuperuser.py"
    echo     User.objects.create_superuser^('admin', 'admin@example.com', 'admin123'^) >> "%TEMP%\createsuperuser.py"
    echo     print^('Superuser created: admin/admin123'^) >> "%TEMP%\createsuperuser.py"
    echo else: >> "%TEMP%\createsuperuser.py"
    echo     print^('Superuser already exists'^) >> "%TEMP%\createsuperuser.py"
    python manage.py shell ^< "%TEMP%\createsuperuser.py"
    del "%TEMP%\createsuperuser.py"
) else (
    echo [INFO] Database already exists.
)

echo.
echo ========================================
echo   Starting Django Development Server
========================================
echo [INFO] Server will be available at: http://127.0.0.1:8000
echo [INFO] Admin panel: http://127.0.0.1:8000/admin
echo [INFO] Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start server
python manage.py runserver 127.0.0.1:8000