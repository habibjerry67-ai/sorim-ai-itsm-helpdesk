
from datetime import datetime, timezone
from db import get_db_connection


def reset_expired_password(username: str):
    # Mock action only: no real password is changed.
    action = "mock_password_reset"
    status = "simulated"
    message = (
        f"Mock password reset completed for {username}. "
        "No real account was modified."
    )

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS automation_audit (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            action VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        INSERT INTO automation_audit
            (username, action, status, details)
        VALUES (%s, %s, %s, %s)
    """, (username, action, status, message))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "username": username,
        "action": action,
        "status": status,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
