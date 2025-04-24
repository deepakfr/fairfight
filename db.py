import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def save_verdict(theme, user1_name, user2_name, user1_input, user2_input, verdict,
                 user1_email=None, user2_email=None, user1_phone=None, user2_phone=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS verdicts (
            id SERIAL PRIMARY KEY,
            theme TEXT,
            user1_name TEXT,
            user2_name TEXT,
            user1_input TEXT,
            user2_input TEXT,
            verdict TEXT,
            user1_email TEXT,
            user2_email TEXT,
            user1_phone TEXT,
            user2_phone TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    ''')

    cur.execute('''
        INSERT INTO verdicts (
            theme, user1_name, user2_name, user1_input, user2_input, verdict,
            user1_email, user2_email, user1_phone, user2_phone
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (theme, user1_name, user2_name, user1_input, user2_input, verdict,
          user1_email, user2_email, user1_phone, user2_phone))

    conn.commit()
    cur.close()
    conn.close()

def get_recent_verdicts(limit=10):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM verdicts ORDER BY created_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
