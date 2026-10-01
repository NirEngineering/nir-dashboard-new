@echo off
chcp 65001 >nul
echo.
echo  ===================================================
echo   ניר הנדסה - הגדרת תזכורות WhatsApp אוטומטיות
echo  ===================================================
echo.

set NIR_DIR=C:\Users\civil\OneDrive\Desktop\Nir Engineering\Nir Engineering ScanSystem\nir_engineering_system\אפליקציית דשבורד למעקב מסמכים\nir_final
set PY_FILE=%NIR_DIR%\wa_reminder.py
set TASK_NAME=NIR_WA_Reminder
set PYTHON=C:\Users\civil\AppData\Local\Python\bin\python.exe

rem --- העתק את הסקריפט לתיקיית הסורק ---
echo [1/2] מעתיק wa_reminder.py לתיקיית הסורק...
copy /Y "%~dp0wa_reminder.py" "%PY_FILE%" >nul
if errorlevel 1 (
    echo.
    echo שגיאה: לא ניתן להעתיק את הקובץ.
    echo ודא שהתיקייה קיימת: %NIR_DIR%
    pause
    exit /b 1
)
echo        הצלחה.

rem --- מחק משימה קיימת אם יש ---
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

rem --- צור משימה יומית בשעה 09:00 ---
echo [2/2] מגדיר הפעלה יומית בשעה 09:00...
schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON%\" \"%PY_FILE%\"" /sc DAILY /st 09:00 /ru "%USERNAME%" /rl HIGHEST /f >nul
if errorlevel 1 (
    echo.
    echo שגיאה ביצירת משימה מתוזמנת.
    echo נסה להריץ כמנהל מערכת (Run as Administrator).
    pause
    exit /b 1
)
echo        הצלחה.

echo.
echo  ===================================================
echo   תזכורות WhatsApp הוגדרו בהצלחה!
echo.
echo   * כל יום בשעה 09:00 — בדיקה אוטומטית
echo   * מסמכים שפוקעים בעוד 45-60 ימים — ישלחו לווצאפ
echo   * הפרש של 2 דקות בין הודעה להודעה
echo   * כל מסמך נשלח פעם אחת בלבד
echo   * עובד גם אם הדשבורד סגור!
echo  ===================================================
echo.
pause
