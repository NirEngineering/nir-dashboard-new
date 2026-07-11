@echo off
chcp 65001 >nul
echo.
echo  ===================================================
echo   ניר הנדסה - הגדרת סנכרון אוטומטי
echo  ===================================================
echo.

set NIR_DIR=C:\Users\civil\OneDrive\Desktop\Nir Engineering\Nir Engineering ScanSystem\nir_engineering_system\אפליקציית דשבורד למעקב מסמכים\nir_final
set VBS_FILE=%NIR_DIR%\watcher_silent.vbs
set TASK_NAME=NIR_Engineering_Watcher

rem --- העתק את הסקריפט השקט לתיקיית הסורק ---
echo [1/3] מעתיק קובץ הפעלה...
copy /Y "%~dp0watcher_silent.vbs" "%VBS_FILE%" >nul
if errorlevel 1 (
    echo שגיאה: לא ניתן להעתיק. ודא שהתיקייה קיימת:
    echo %NIR_DIR%
    pause
    exit /b 1
)
echo        הצלחה.

rem --- מחק משימה קיימת (אם יש) ---
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

rem --- צור משימה מתוזמנת - מופעל בכניסה למחשב ---
echo [2/3] מגדיר הפעלה אוטומטית בכניסה למחשב...
schtasks /create /tn "%TASK_NAME%" /tr "wscript.exe \"%VBS_FILE%\"" /sc ONLOGON /ru "%USERNAME%" /rl HIGHEST /f >nul
if errorlevel 1 (
    echo שגיאה ביצירת משימה מתוזמנת.
    echo נסה להריץ כמנהל מערכת (Run as Administrator).
    pause
    exit /b 1
)
echo        הצלחה.

rem --- הפעל עכשיו גם בפועל ---
echo [3/3] מפעיל את הסורק עכשיו ברקע...
wscript.exe "%VBS_FILE%"
echo        הצלחה.

echo.
echo  ===================================================
echo   הסנכרון הוגדר בהצלחה!
echo.
echo   * הסורק רץ עכשיו ברקע
echo   * בכל קובץ חדש - הדשבורד יתעדכן תוך שניות
echo   * בכל כניסה למחשב - יופעל אוטומטית
echo.
echo   לבדיקת הסורק: פתח Task Manager > Details > pythonw.exe
echo  ===================================================
echo.
pause
