@echo off
echo Stopping existing Python processes...
taskkill /F /IM python.exe
timeout /t 2

echo Seeding Database...
python check_categories.py

echo Restarting Server...
start_server.bat
pause
