import uuid
from db import get_db_connection

def request_software(username: str, software: str):
    request_id = "REQ-" + uuid.uuid4().hex[:8].upper()
    status = "Approved - Mock Provisioning"

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS software_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                request_id VARCHAR(30) NOT NULL,
                username VARCHAR(100) NOT NULL,
                software VARCHAR(100) NOT NULL,
                status VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            INSERT INTO software_requests
                (request_id, username, software, status)
            VALUES (%s, %s, %s, %s)
        """, (request_id, username, software, status))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return {
        "request_id": request_id,
        "username": username,
        "software": software,
        "status": status,
        "message": f"{software} provisioning simulated for {username}. No software was installed."
    }
