from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.get("/")
def read_root():
    return {"status": "API running"}

@app.post("/enrich")
def enrich(ticket_id: str, message: str):

    classification = "Device Offline"
    confidence = 0.85
    priority = "Medium"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO decision_events
        (ticket_id, classification, classification_confidence, priority)
        VALUES (%s,%s,%s,%s)
        """,
        (ticket_id, classification, confidence, priority)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "classification": classification,
        "confidence": confidence,
        "priority": priority
    }
