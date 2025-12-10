#!/bin/bash
# Script untuk menjalankan Face Recognition API Server (Linux/Mac)

echo "========================================"
echo "Face Recognition Attendance System"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment tidak ditemukan"
    echo "[*] Membuat virtual environment..."
    python3 -m venv venv
    echo "[+] Virtual environment berhasil dibuat"
    echo ""
fi

# Activate virtual environment
echo "[*] Aktivasi virtual environment..."
source venv/bin/activate

# Check if dependencies installed
if ! pip show fastapi &> /dev/null; then
    echo "[!] Dependencies belum terinstall"
    echo "[*] Install dependencies..."
    pip install -r requirements.txt
    echo "[+] Dependencies berhasil diinstall"
    echo ""
else
    echo "[+] Dependencies sudah terinstall"
    echo ""
fi

# Run server
echo "[*] Starting server..."
echo "[*] API akan berjalan di: http://localhost:8001"
echo "[*] Dokumentasi: http://localhost:8001/docs"
echo "[*] Tekan CTRL+C untuk stop server"
echo ""
echo "========================================"
echo ""

python main.py
