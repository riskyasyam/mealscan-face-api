@echo off
REM Script untuk menjalankan Face Recognition API Server

echo ========================================
echo Face Recognition Attendance System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [!] Virtual environment tidak ditemukan
    echo [*] Membuat virtual environment...
    python -m venv venv
    echo [+] Virtual environment berhasil dibuat
    echo.
)

REM Activate virtual environment
echo [*] Aktivasi virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies installed
echo [*] Memeriksa dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [!] Dependencies belum terinstall
    echo [*] Install dependencies...
    pip install -r requirements.txt
    echo [+] Dependencies berhasil diinstall
    echo.
) else (
    echo [+] Dependencies sudah terinstall
    echo.
)

REM Run server
echo [*] Starting server...
echo [*] API akan berjalan di: http://localhost:8000
echo [*] Dokumentasi: http://localhost:8000/docs
echo [*] Tekan CTRL+C untuk stop server
echo.
echo ========================================
echo.

python main.py

pause
