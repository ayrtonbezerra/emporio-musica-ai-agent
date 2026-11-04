import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

def get_connection():
    return psycopg.connect(
        conninfo=os.getenv("DATABASE_URL"),
        row_factory=dict_row,
        connect_timeout=2
    )

if __name__ == '__main__':
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            print(cur.fetchone())