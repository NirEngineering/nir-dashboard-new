@echo off
chcp 65001 >nul
echo עוצר את הסורק...
taskkill /f /im pythonw.exe >nul 2>&1
echo הסורק הופסק.
pause
