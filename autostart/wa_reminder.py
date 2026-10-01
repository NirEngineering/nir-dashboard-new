# -*- coding: utf-8 -*-
"""
wa_reminder.py — שולח תזכורות WhatsApp אוטומטיות למסמכים שפוקעים בעוד 45-60 ימים
הצב קובץ זה בתיקיית: nir_final
הגדר משימה יומית: setup_wa_reminder.bat
"""

import requests
import json
import os
import time
from datetime import date, datetime

# ─── הגדרות ────────────────────────────────────────────────────────────────
SHEET_ID   = "1mZZq0QrQVqzNJ66ErJ-h81FSkO_5KIu3orePE5A9BqE"
API_KEY    = "AIzaSyDJy8tolZu8z-IuMFXSmRfsFFrM_rJkK8w"
SHEET_NAME = "מסמכים"

WA_INSTANCE = "7107614555"
WA_TOKEN    = "9be94b91b1264012b9b39df959537b993dcccb3065b14d40b4"
WA_CHAT_ID  = "972504325915@c.us"

DAYS_MIN = 45
DAYS_MAX = 60

# קובץ מעקב — נשמר לצד הסקריפט
SENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wa_sent.json")
DELAY_SECONDS = 120  # הפרש 2 דקות בין הודעה להודעה

# ─── טעינת היסטוריה ────────────────────────────────────────────────────────
def load_sent():
    try:
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_sent(s):
    try:
        with open(SENT_FILE, "w", encoding="utf-8") as f:
            json.dump(list(s), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"שגיאה בשמירת היסטוריה: {e}")

# ─── קריאת נתונים מגוגל שיטס ───────────────────────────────────────────────
def fetch_sheet():
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
        f"/values/{SHEET_NAME}?key={API_KEY}"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    rows = r.json().get("values", [])
    if len(rows) < 2:
        return []

    headers = rows[0]

    def col(name):
        for i, h in enumerate(headers):
            if h and name in h:
                return i
        return -1

    iA = col("לקוח")
    iB = col("מיקום")
    iC = col("סוג")
    iE = col("תוקף")
    iH = col("ארכיון")

    records = []
    for row in rows[1:]:
        def get(i):
            return row[i].strip() if 0 <= i < len(row) else ""

        archived = get(iH).lower()
        if archived in ("1", "true", "yes", "כן", "archive"):
            continue

        records.append({
            "client":   get(iA),
            "location": get(iB),
            "docType":  get(iC),
            "expiry":   get(iE),
        })
    return records

# ─── חישוב ימים ────────────────────────────────────────────────────────────
def parse_date(s):
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d", "%d/%m/%y"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except Exception:
            pass
    return None

def days_remaining(expiry_str):
    d = parse_date(expiry_str)
    if not d:
        return None
    return (d - date.today()).days

def doc_key(r):
    return f"{r['client']}||{r['docType']}||{r['expiry']}"

# ─── בניית הודעה ───────────────────────────────────────────────────────────
def build_message(r, days):
    if days <= 0:
        emoji = "🔴"
        status = f"פג לפני {-days} ימים — נדרש חידוש דחוף"
    elif days <= 60:
        emoji = "🟡"
        status = f"נותרו {days} ימים לחידוש"
    else:
        emoji = "🟢"
        status = f"בתוקף — נותרו {days} ימים"

    msg = f"{emoji} תזכורת מסמך\n\n"
    msg += f"👤 לקוח: {r['client']}\n"
    if r["location"]:
        msg += f"📍 מיקום: {r['location']}\n"
    msg += f"📋 מסמך: {r['docType']}\n"
    if r["expiry"]:
        msg += f"📅 תאריך תוקף: {r['expiry']}\n"
    msg += f"⏰ {status}"
    return msg

# ─── שליחה ─────────────────────────────────────────────────────────────────
def send_wa(msg):
    server = WA_INSTANCE[:4]
    url = (
        f"https://{server}.api.greenapi.com"
        f"/waInstance{WA_INSTANCE}/sendMessage/{WA_TOKEN}"
    )
    r = requests.post(
        url,
        json={"chatId": WA_CHAT_ID, "message": msg},
        timeout=20
    )
    data = r.json()
    if not data.get("idMessage"):
        raise Exception(str(data)[:150])

# ─── ראשי ──────────────────────────────────────────────────────────────────
def main():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now_str}] wa_reminder.py — מתחיל בדיקה (חלון: {DAYS_MIN}-{DAYS_MAX} ימים)")

    try:
        records = fetch_sheet()
    except Exception as e:
        print(f"שגיאה בקריאת גוגל שיטס: {e}")
        return

    sent = load_sent()
    to_send = []

    for r in records:
        days = days_remaining(r["expiry"])
        if days is None:
            continue
        if not (DAYS_MIN <= days <= DAYS_MAX):
            continue
        key = doc_key(r)
        if key in sent:
            continue
        to_send.append((r, days, key))

    if not to_send:
        print("אין מסמכים חדשים לשליחה")
        return

    print(f"נמצאו {len(to_send)} מסמכים לשליחה")

    for i, (r, days, key) in enumerate(to_send):
        msg = build_message(r, days)
        try:
            send_wa(msg)
            sent.add(key)
            save_sent(sent)
            print(f"✅ [{i+1}/{len(to_send)}] {r['client']} — {r['docType']} ({days} ימים)")
        except Exception as e:
            print(f"❌ שגיאה: {r['client']} — {e}")

        if i < len(to_send) - 1:
            print(f"   ממתין {DELAY_SECONDS} שניות לפני ההודעה הבאה...")
            time.sleep(DELAY_SECONDS)

    print(f"[{datetime.now().strftime('%H:%M')}] הסתיים")

if __name__ == "__main__":
    main()
