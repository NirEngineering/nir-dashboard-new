# -*- coding: utf-8 -*-
"""
audit_scan.py — בודק אילו קבצי Word בתיקיית הלקוחות חסרים מגוגל שיטס
הרץ ידנית כאשר רוצים לוודא שהסריקה מלאה.
"""

import os
import requests
import json

SHEET_ID   = "1mZZq0QrQVqzNJ66ErJ-h81FSkO_5KIu3orePE5A9BqE"
API_KEY    = "AIzaSyDJy8tolZu8z-IuMFXSmRfsFFrM_rJkK8w"
SHEET_NAME = "מסמכים"

CLIENTS_FOLDER = r"C:\Users\civil\OneDrive\Desktop\לקוחות"

WORD_EXTENSIONS = {".docx", ".doc"}

def fetch_sheet_filenames():
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
        f"/values/{SHEET_NAME}?key={API_KEY}"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    rows = r.json().get("values", [])
    if len(rows) < 2:
        return set()

    headers = rows[0]
    iG = next((i for i, h in enumerate(headers) if h and "קובץ" in h), -1)
    iA = next((i for i, h in enumerate(headers) if h and "לקוח" in h), -1)

    names = set()
    for row in rows[1:]:
        fn = row[iG].strip() if 0 <= iG < len(row) else ""
        if fn:
            names.add(fn.lower())
    return names

def scan_local_files(folder):
    found = []
    for root, dirs, files in os.walk(folder):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in WORD_EXTENSIONS:
                full = os.path.join(root, fn)
                found.append((fn, full))
    return found

def main():
    print("=" * 60)
    print("  בדיקת שלמות סריקה — ניר הנדסה")
    print("=" * 60)
    print()

    if not os.path.isdir(CLIENTS_FOLDER):
        print(f"שגיאה: התיקייה לא נמצאה:\n  {CLIENTS_FOLDER}")
        print("ודא שהמחשב מחובר ל-OneDrive ושהתיקייה קיימת.")
        input("\nלחץ Enter לסגירה...")
        return

    print(f"סורק תיקייה: {CLIENTS_FOLDER}")
    local_files = scan_local_files(CLIENTS_FOLDER)
    print(f"נמצאו {len(local_files)} קבצי Word מקומית")
    print()

    print("קורא נתונים מגוגל שיטס...")
    try:
        sheet_names = fetch_sheet_filenames()
    except Exception as e:
        print(f"שגיאה: {e}")
        input("\nלחץ Enter לסגירה...")
        return
    print(f"נמצאו {len(sheet_names)} קבצים בגוגל שיטס")
    print()

    missing = [(fn, path) for fn, path in local_files if fn.lower() not in sheet_names]

    if not missing:
        print("✅ כל הקבצים המקומיים נמצאים בגוגל שיטס — הסריקה מלאה!")
    else:
        print(f"⚠️  נמצאו {len(missing)} קבצים שחסרים מגוגל שיטס:\n")
        for fn, path in missing:
            rel = os.path.relpath(path, CLIENTS_FOLDER)
            print(f"  • {rel}")

        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "missing_files.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"קבצים חסרים מגוגל שיטס — {len(missing)} קבצים\n")
            f.write("=" * 60 + "\n")
            for fn, path in missing:
                f.write(f"{path}\n")
        print(f"\nדוח מלא נשמר: {report_path}")

    print()
    input("לחץ Enter לסגירה...")

if __name__ == "__main__":
    main()
