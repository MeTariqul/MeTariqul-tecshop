@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   TechShop Django Server Launcher
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
    echo [ERROR] Please install Python from https://www.python.org/downloads/
    timeout /t 5
    exit /b 1
)
echo [SUCCESS] Python found.

REM Check Python version
python --version

REM Check if virtual environment exists and has activate file
if not exist "%PROJECT_DIR%\venv\Scripts\activate" (
    echo.
    echo [INFO] Virtual environment not found or incomplete. Creating one...
    if exist "%PROJECT_DIR%\venv" (
        echo [INFO] Removing incomplete venv...
        rmdir /s /q "%PROJECT_DIR%\venv"
    )
    python -m venv "%PROJECT_DIR%\venv"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        timeout /t 5
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
) else (
    echo.
    echo [INFO] Virtual environment found.
)

REM Activate virtual environment
echo.
echo [INFO] Activating virtual environment...
call "%PROJECT_DIR%\venv\Scripts\activate.bat" 2>nul
if errorlevel 1 (
    call "%PROJECT_DIR%\venv\Scripts\activate" 2>nul
    if errorlevel 1 (
        set "PATH=%PROJECT_DIR%\venv\Scripts;%PATH%"
        set "VIRTUAL_ENV=%PROJECT_DIR%\venv"
    )
)
echo [SUCCESS] Virtual environment activated.

REM Upgrade pip and setuptools
echo.
echo [INFO] Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel --quiet

REM Install dependencies
echo.
echo [INFO] Installing dependencies...

REM Install Django
echo [INFO] Installing Django...
pip install Django==4.2.7 --quiet

REM Install pymysql as MySQLdb replacement (works without MySQL dev tools)
echo [INFO] Installing pymysql...
pip install pymysql --quiet

REM Install Pillow
echo [INFO] Installing Pillow...
pip install Pillow==10.1.0 --quiet 2>nul
if errorlevel 1 (
    echo [WARNING] Pillow 10.1.0 failed. Trying newer version...
    pip install Pillow --quiet
)

REM Install other dependencies
echo [INFO] Installing django-environ...
pip install django-environ==0.11.2 --quiet

echo [INFO] Installing python-decouple...
pip install python-decouple==3.8 --quiet

echo [INFO] Installing whitenoise...
pip install whitenoise==6.6.0 --quiet

echo [INFO] Installing gunicorn...
pip install gunicorn==21.2.0 --quiet

echo [INFO] Installing qrcode and reportlab...
pip install "qrcode[pil]==8.0" --quiet
pip install reportlab==4.1.0 --quiet

echo [SUCCESS] Core dependencies installed.

REM Try to install common additional dependencies
echo.
echo [INFO] Installing additional common dependencies...
pip install django-cors-headers --quiet
pip install django-debug-toolbar --quiet
pip install crispy-bootstrap4 --quiet
pip install crispy-bootstrap5 --quiet
pip install channels --quiet
pip install daphne --quiet
echo [SUCCESS] Additional dependencies installed.

REM Add pymysql to settings.py if not already present
echo.
echo [INFO] Configuring pymysql in settings.py...
set "SETTINGS_FILE=%PROJECT_DIR%\techshop\techshop_proj\settings.py"
findstr /C:"pymysql.install_as_MySQLdb" "%SETTINGS_FILE%" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Adding pymysql configuration to settings.py...
    
    REM Create a temporary file with the new content
    echo from pathlib import Path > "%TEMP%\settings_new.py"
    echo import pymysql >> "%TEMP%\settings_new.py"
    echo pymysql.version_info = ^(2, 2, 1, 'final', 0^) >> "%TEMP%\settings_new.py"
    echo pymysql.install_as_MySQLdb^(^) >> "%TEMP%\settings_new.py"
    echo. >> "%TEMP%\settings_new.py"
    
    REM Find the line number where we should insert (after the docstring)
    for /f "tokens=1" %%a in ('findstr /n "from decouple import" "%SETTINGS_FILE%"') do set "DECOUPLE_LINE=%%a"
    
    REM Read lines before decouple import and append the rest
    if defined DECOUPLE_LINE (
        set /a DECOUPLE_LINE-=1
        more +%DECOUPLE_LINE% "%SETTINGS_FILE%" > "%TEMP%\settings_rest.py"
        copy "%TEMP%\settings_new.py" + "%TEMP%\settings_rest.py" "%SETTINGS_FILE%" >nul
        del "%TEMP%\settings_new.py" "%TEMP%\settings_rest.py"
    )
    echo [SUCCESS] pymysql configured.
) else (
    echo [INFO] pymysql already configured.
)

REM Check for .env file and create from example if missing
echo.
echo [INFO] Checking for environment configuration...
if not exist "%PROJECT_DIR%\.env" (
    if exist "%PROJECT_DIR%\.env.example" (
        echo [INFO] Creating .env from .env.example...
        copy "%PROJECT_DIR%\.env.example" "%PROJECT_DIR%\.env"
        echo [SUCCESS] .env file created. Please edit it with your settings.
    ) else (
        echo [WARNING] .env.example not found.
    )
)

REM Check if MySQL server is running
echo.
echo [INFO] Checking MySQL server...
net start | findstr /i "mysql" >nul
if errorlevel 1 (
    echo [WARNING] MySQL server may not be running.
    echo [INFO] Please ensure MySQL is running before starting Django.
)

REM Change to techshop directory
cd /d "%PROJECT_DIR%\techshop"

REM Check if migrations are needed
echo.
echo [INFO] Checking database migrations...
python manage.py makemigrations --noinput 2>nul
if errorlevel 1 (
    echo [WARNING] Some migrations may have issues.
)

echo [INFO] Running database migrations...
python manage.py migrate --noinput 2>nul
if errorlevel 1 (
    echo [WARNING] Migration failed. Check database configuration.
    echo [INFO] Make sure MySQL server is running and .env is configured.
    echo [INFO] The server will still try to start...
)

REM Go back to project root
cd /d "%PROJECT_DIR%"

REM Run the Django development server in background
echo.
echo ========================================
echo   Starting Django Server
echo ========================================
echo [INFO] Server will be available at: http://127.0.0.1:8000
echo [INFO] Admin panel at: http://127.0.0.1:8000/admin
echo.

REM Open browser in new tab
start http://127.0.0.1:8000

REM Start server in background and exit
cd techshop
start "TechShop Server" /b python manage.py runserver 127.0.0.1:8000

echo [SUCCESS] Server started in background!
echo [INFO] Closing window...
timeout /t 3 /nobreak >nul
exit
