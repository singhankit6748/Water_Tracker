import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'water_tracker.db'

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='water_intake'")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute("PRAGMA table_info(water_intake)")
        columns = [col[1] for col in cursor.fetchall()]
        if "intake_ml" not in columns:
            cursor.execute("ALTER TABLE water_intake RENAME TO water_intake_old")
            cursor.execute('''
                CREATE TABLE water_intake (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    intake_ml REAL NOT NULL
                )
            ''')
            if "amount" in columns:
                cursor.execute('''
                    INSERT INTO water_intake (user_id, date, intake_ml)
                    SELECT user_id, date, amount FROM water_intake_old
                ''')
            cursor.execute("DROP TABLE water_intake_old")
    else:
        cursor.execute('''
            CREATE TABLE water_intake (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                intake_ml REAL NOT NULL
            )
        ''')

    conn.commit()
    conn.close()

def log_intake(user_id, intake_ml, timestamp=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    date_str = (timestamp or datetime.now()).strftime('%Y-%m-%d')
    cursor.execute('''
        INSERT INTO water_intake (user_id, date, intake_ml) VALUES (?, ?, ?)
    ''', (user_id, date_str, intake_ml))
    conn.commit()
    conn.close()

def get_intake_history(user_id, date_filter="All time"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = "SELECT date, intake_ml FROM water_intake WHERE user_id = ?"
    params = [user_id]
    
    today = datetime.now().date()
    if date_filter == "Today":
        query += " AND date = ?"
        params.append(today.strftime('%Y-%m-%d'))
    elif date_filter == "Last 7 days":
        params.append((today - timedelta(days=7)).strftime('%Y-%m-%d'))
        query += " AND date >= ?"
    elif date_filter == "Last 30 days":
        params.append((today - timedelta(days=30)).strftime('%Y-%m-%d'))
        query += " AND date >= ?"
    
    cursor.execute(query, tuple(params))
    records = cursor.fetchall()
    conn.close()
    
    formatted_records = []
    for date_str, intake_ml in records:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            formatted_records.append({
                "Date": date_obj.strftime('%Y-%m-%d'),
                "Day": date_obj.strftime('%A'),
                "Amount (ml)": intake_ml
            })
        except:
            formatted_records.append({
                "Date": date_str,
                "Day": "Unknown",
                "Amount (ml)": intake_ml
            })
    
    return formatted_records

def get_today_intake(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        "SELECT SUM(intake_ml) FROM water_intake WHERE user_id = ? AND date = ?", 
        (user_id, today)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0

# Ensure tables are created on import
create_tables()
