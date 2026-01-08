import sqlite3
import os

db_path = 'instance/local.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_generated_content';")
    exists = len(cursor.fetchall()) > 0
    print(f"Table 'ai_generated_content' exists: {exists}")
    
    if not exists:
        print("Creating 'ai_generated_content' table...")
        cursor.execute('''
            CREATE TABLE ai_generated_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source_type VARCHAR(50),
                source_id INTEGER,
                content TEXT NOT NULL,
                content_type VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        print("Table created successfully.")
    conn.close()
else:
    print(f"Database {db_path} not found.")
