
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH, override=True)


def create_servicenow_incident(
    short_description,
    description,
    priority="3",
    urgency="2",
    impact="2",
    category="inquiry",
):
    instance = os.getenv("SERVICENOW_INSTANCE_URL", "").rstrip("/")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")

    if not instance or not username or not password:
        raise RuntimeError(
            "ServiceNow configuration is missing. "
            "Check SERVICENOW_INSTANCE_URL, "
            "SERVICENOW_USERNAME and SERVICENOW_PASSWORD in .env."
        )

    payload = {
        "short_description": short_description[:160],
        "description": description,
        "urgency": str(urgency),
        "impact": str(impact),
        "category": category,
    }

    # ServiceNow usually derives priority from impact and urgency.
    # Send priority only if you explicitly need to override that behavior.
    if priority is not None:
        payload["priority"] = str(priority)

    try:
        response = httpx.post(
            f"{instance}/api/now/table/incident",
            auth=(username, password),
            json=payload,
            headers={"Accept": "application/json"},
            timeout=30.0,
        )
        response.raise_for_status()

        data = response.json()
        incident = data.get("result")

        if not isinstance(incident, dict) or not incident.get("number"):
            raise RuntimeError(
                "ServiceNow responded, but no incident number was returned."
            )

        return incident

    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code

        if status == 401:
            raise RuntimeError(
                "ServiceNow authentication failed (401). "
                "Verify the instance username and password."
            ) from exc

        if status == 403:
            raise RuntimeError(
                "ServiceNow rejected the request (403). "
                "Check the account's permissions to create incidents."
            ) from exc

        raise RuntimeError(
            f"ServiceNow returned HTTP {status}: "
            f"{exc.response.text[:500]}"
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            f"Could not reach ServiceNow: {exc}"
        ) from exc
