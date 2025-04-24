import psycopg2
import streamlit as st

# 🔐 Load DB config from Streamlit secrets
DB_CONFIG = {
    "host": st.secrets.get("DB_HOST", "localhost"),
    "port": st.secrets.get("DB_PORT", "5432"),
    "dbname": st.secrets.get("DB_NAME", "postgres"),
    "user": st.secrets.get("DB_USER", "postgres"),
    "password": st.secrets.get("DB_PASSWORD", "1234"),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def save_verdict(theme, user1_name, user2_name, user1_input, user2_input, verdict,
                 user1_email=None, user2_email=None, user1_phone=None, user2_phone=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        INSERT INTO verdicts (
            theme, user1_name, user2_name, user1_input, user2_input, verdict,
            user1_email, user2_email, user1_phone, user2_phone
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (theme, user1_name, user2_name, user1_input, user2_input, verdict,
          user1_email, user2_email, user1_phone, user2_phone))
    conn.commit()
    cur.close()
    conn.close()
