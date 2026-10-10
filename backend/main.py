
import json
import httpx
from dotenv import load_dotenv
from db import get_db_connection
from rag import search_knowledge
from automation import reset_expired_password
from provisioning import request_software
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="Sorim.AI ITSM Helpdesk API",
    version="1.0.0",
    description="AI-powered IT service management helpdesk",
)

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IncidentRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=2000)


class PasswordResetRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)


class SoftwareRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    software: str = Field(..., min_length=1, max_length=100)


@app.get("/")
def home():
    return {"message": "Sorim.AI ITSM API is running"}


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "application": "Sorim.AI ITSM Helpdesk",
        "backend": "FastAPI",
        "llm": OLLAMA_MODEL,
    }


@app.get("/api/incidents")
def get_incidents():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM incidents ORDER BY id DESC")
        incidents = cursor.fetchall()
        return {"incidents": incidents}
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve incidents.",
        )
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.post("/api/incidents/analyze")
def analyze_incident(request: IncidentRequest):
    description = request.description.strip()

    if not description:
        raise HTTPException(
            status_code=400,
            detail="Please describe your IT issue.",
        )

    text = description.lower()

    if any(w in text for w in ["vpn", "network", "wifi", "wi-fi"]):
        category, group = "Network / VPN", "Network Support"
    elif any(w in text for w in [
        "password", "login", "locked", "sign in", "signin"
    ]):
        category, group = "Account / Access", "Identity Support"
    elif any(w in text for w in [
        "laptop", "keyboard", "monitor", "hardware"
    ]):
        category, group = "Hardware", "IT Support"
    else:
        category, group = "General IT", "Service Desk"

    prompt = f"""
Analyze this employee IT incident:
{description}

Return JSON with:
priority: "P1 - Critical", "P2 - High", "P3 - Medium", or "P4 - Low"
impact: "Organization", "Department", or "Individual"
urgency: "High", "Medium", or "Low"
suggested_resolution: concise steps, maximum 3
needs_escalation: true or false
escalation_reason: short reason or empty string

Never ask for passwords or MFA codes.
Never recommend disabling security controls.
Escalate suspected security incidents.
Do not claim the issue has been fixed.
If uncertain, recommend IT review.
"""

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a safe IT helpdesk assistant. "
                            "Return valid JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        ai = json.loads(response.json()["message"]["content"])

        priority = ai.get("priority", "P3 - Medium")
        if priority not in {
            "P1 - Critical", "P2 - High",
            "P3 - Medium", "P4 - Low",
        }:
            priority = "P3 - Medium"

        impact = ai.get("impact", "Individual")
        if impact not in {"Organization", "Department", "Individual"}:
            impact = "Individual"

        urgency = ai.get("urgency", "Medium")
        if urgency not in {"High", "Medium", "Low"}:
            urgency = "Medium"

        resolution = str(
            ai.get(
                "suggested_resolution",
                "Contact the IT Service Desk.",
            )
        )[:1500]

        needs_escalation = ai.get("needs_escalation", False) is True
        escalation_reason = str(ai.get("escalation_reason", ""))[:300]

    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        priority = "P3 - Medium"
        impact = "Individual"
        urgency = "Medium"
        resolution = (
            "AI analysis is unavailable. Contact the IT Service Desk."
        )
        needs_escalation = True
        escalation_reason = "AI unavailable; manual review required."

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO incidents (description, category, priority, status)
            VALUES (%s, %s, %s, %s)
            """,
            (description, category, priority, "Open"),
        )
        ticket_id = cursor.lastrowid
        conn.commit()
 
    except Exception as e:
        if conn:
            conn.rollback()
        print("INCIDENT DATABASE ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Could not save incident to database.",
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return {
        "ticket_id": ticket_id,
        "ticket_type": "Incident",
        "category": category,
        "priority": priority,
        "impact": impact,
        "urgency": urgency,
        "assignment_group": group,
        "short_description": description[:100],
        "description": description,
        "suggested_resolution": resolution,
        "needs_escalation": needs_escalation,
        "escalation_reason": escalation_reason,
        "status": "Open",
        "automation_executed": False,
        "llm_model": OLLAMA_MODEL,
    }


@app.post("/api/knowledge/ask")
def ask_knowledge(request: IncidentRequest):
    results = search_knowledge(request.description)

    if not results:
        return {
            "answer": (
                "I couldn't find relevant information in the "
                "Knowledge Base. Please contact the IT Service Desk."
            ),
            "sources": [],
            "found": False,
        }

    context = "\n\n".join(
        f"Source: {item['source']}\n{item['content']}"
        for item in results
    )

    prompt = f"""
Answer using ONLY the knowledge below.

Knowledge:
{context}

Question:
{request.description}

Do not invent information. If the knowledge is insufficient,
say so and recommend IT support.
"""

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Answer safely using only the supplied knowledge."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"temperature": 0.1},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"]
    except (httpx.HTTPError, KeyError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Knowledge assistant is temporarily unavailable.",
        )

    return {
        "answer": answer,
        "sources": list(dict.fromkeys(
            item["source"] for item in results
        )),
        "found": True,
    }


@app.post("/api/automation/password-reset")
def password_reset(request: PasswordResetRequest):
    username = request.username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required.",
        )

    try:
        return reset_expired_password(username)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Password reset simulation failed.",
        )


@app.post("/api/provisioning/request")
def provision_software(request: SoftwareRequest):
    username = request.username.strip()
    software = request.software.strip()

    if not username or not software:
        raise HTTPException(
            status_code=400,
            detail="Username and software are required.",
        )

    try:
        return request_software(username, software)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not create software request.",
        )
