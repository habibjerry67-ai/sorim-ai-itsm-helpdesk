from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Sorim.AI ITSM Helpdesk API",
    version="1.0.0",
    description="AI-powered IT service management helpdesk",
)

# Allow the React frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class IncidentRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Describe the IT issue",
    )


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Sorim.AI ITSM Helpdesk API is running"
    }


# Health check endpoint
@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "application": "Sorim.AI ITSM Helpdesk",
        "backend": "FastAPI",
    }


# Incident analysis endpoint
@app.post("/api/incidents/analyze")
def analyze_incident(request: IncidentRequest):
    description = request.description.strip()

    if not description:
        raise HTTPException(
            status_code=400,
            detail="Please describe your IT issue.",
        )

    text = description.lower()

    # Classify the incident using basic rules.
    if any(
        word in text
        for word in ["vpn", "network", "wifi", "wi-fi"]
    ):
        category = "Network / VPN"
        assignment_group = "Network Support"
        resolution = (
            "Check your internet connection, reconnect to the "
            "company VPN, and verify that your VPN credentials "
            "have not expired."
        )

    elif any(
        word in text
        for word in [
            "password",
            "login",
            "locked",
            "sign in",
            "signin",
        ]
    ):
        category = "Account / Access"
        assignment_group = "Identity Support"
        resolution = (
            "Verify your account credentials and account status. "
            "Use the approved password reset process if needed."
        )

    elif any(
        word in text
        for word in [
            "laptop",
            "keyboard",
            "monitor",
            "hardware",
        ]
    ):
        category = "Hardware"
        assignment_group = "IT Support"
        resolution = (
            "Check the device connections and restart the "
            "affected equipment if it is safe to do so."
        )

    else:
        category = "General IT"
        assignment_group = "Service Desk"
        resolution = (
            "The issue needs further investigation by the "
            "Service Desk. More information may be required."
        )

    # Initial demo priority. We will improve this with
    # impact and urgency rules in a later step.
    return {
        "ticket_type": "Incident",
        "category": category,
        "priority": "P2 - High",
        "impact": "Individual",
        "urgency": "High",
        "assignment_group": assignment_group,
        "short_description": description[:100],
        "description": description,
        "suggested_resolution": resolution,
        "status": "Analyzed - Not Yet Submitted",
        "automation_executed": False,
    }
