import json
import sqlite3
from pathlib import Path
from datetime import datetime

from agent_framework import Skill

enquiry_skill = Skill(
    name="enquiry-skill",
    description="Submit and store enquiry form data. Required inputs: name, email, message.",
    content="""
Steps to submit enquiry form:
1. Collect user details (name, email, message, optional phone).
2. Validate required fields are not empty.
3. Call submit_enquiry script.
4. The script will store the data in SQLite DB.
5. Return confirmation with saved record details.
"""
)


DB_PATH = Path("data/enquiries.db")


def init_db():
    """Create DB and table if not exists"""
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@enquiry_skill.script(
    name="submit_enquiry",
    description="Save enquiry form data into SQLite database"
)
def submit_enquiry(name: str, email: str, message: str, phone: str = "") -> str:
    """Save enquiry data into SQLite DB"""

    # Basic validation
    if not name or not email or not message:
        return json.dumps({
            "saved": False,
            "error": "name, email and message are required fields"
        })

    # Initialize DB
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO enquiries (name, email, phone, message, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, phone, message, created_at))

    enquiry_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return json.dumps({
        "saved": True,
        "enquiry_id": enquiry_id,
        "data": {
            "name": name,
            "email": email,
            "phone": phone,
            "message": message,
            "created_at": created_at
        }
    })