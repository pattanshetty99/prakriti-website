import sqlite3

DB_NAME = "prakriti.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        answers TEXT,
        image_path TEXT,
        prakriti TEXT,
        confidence REAL
    )
    """)
    conn.commit()
    conn.close()

def save_record(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
    INSERT INTO submissions 
    (name, age, answers, image_path, prakriti, confidence)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["age"],
        data["answers"],
        data["image_path"],
        data["prakriti"],
        data["confidence"]
    ))
    conn.commit()
    conn.close()

def get_all_records():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows
