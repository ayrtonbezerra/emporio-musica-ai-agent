import os
from pathlib import Path

from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DATABASE_URL = os.environ["DATABASE_URL"]

with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
    checkpointer.setup()

print("ok")