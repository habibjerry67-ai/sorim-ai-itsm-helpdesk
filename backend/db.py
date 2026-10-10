
import os
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH, override=True)

def get_db_connection():
    password = os.getenv("DB_PASSWORD")

    if not password:
        raise RuntimeError(
            f"DB_PASSWORD is missing. Check {ENV_PATH}"
        )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=password,
        database=os.getenv("DB_NAME", "sorim_itsm"),
    )
