
import json
import uuid
from datetime import datetime, timezone

from db import get_db_connection
from rag import search_knowledge
from servicenow_client import create_servicenow_incident


def identify_issue(description):
    """Identify an issue using explicit, conservative rules."""
    text = description.lower()

    if any(word in text for word in (
        "security breach", "hacked", "malware",
        "data breach", "suspicious login"
    )):
        return {
            "issue_type": "security",
            "confidence": 0.95,
            "summary": "Potential security incident requiring human review."
        }

    if any(word in text for word in (
        "password expired", "expired password",
        "password has expired", "cannot log in because of password"
    )):
        return {
            "issue_type": "expired_password",
            "confidence": 0.90,
            "summary": "Employee reports a possible expired-password issue."
        }

    if any(word in text for word in (
        "vpn", "virtual private network"
    )):
        return {
            "issue_type": "vpn",
            "confidence": 0.95,
            "summary": "Employee reports a VPN connectivity or access issue."
        }

    return {
        "issue_type": "unknown",
        "confidence": 0.40,
        "summary": "Issue not recognized by safe automation rules."
    }


def diagnose_issue(issue_type, identity_verified=False):
    """Provide a conservative diagnosis without claiming an unverified fix."""
    if issue_type == "expired_password":
        return {
            "diagnosis": "A password-expiration issue is possible; verify the account and identity.",
            "requires_identity_verification": True,
            "identity_verified": bool(identity_verified)
        }

    if issue_type == "vpn":
        return {
            "diagnosis": "VPN connectivity problem reported; the actual cause has not yet been verified.",
            "requires_identity_verification": False,
            "identity_verified": bool(identity_verified)
        }

    if issue_type == "security":
        return {
            "diagnosis": "Potential security incident. Human security-team investigation is required.",
            "requires_identity_verification": False,
            "identity_verified": bool(identity_verified)
        }

    return {
        "diagnosis": "Insufficient evidence for safe diagnosis.",
        "requires_identity_verification": False,
        "identity_verified": bool(identity_verified)
    }


def get_knowledge(issue_type, description):
    """Retrieve approved knowledge using the existing RAG component."""
    try:
        results = search_knowledge(description) or []
    except Exception as exc:
        return {
            "article_id": None,
            "title": "Knowledge search unavailable",
            "instructions": [
                "Knowledge retrieval failed. Escalate to IT support."
            ],
            "source": None,
            "error": str(exc)[:300]
        }

    if not results:
        return {
            "article_id": None,
            "title": "No matching approved article",
            "instructions": ["Escalate to IT support."],
            "source": None
        }

    sources = []
    instructions = []

    for item in results:
        if not isinstance(item, dict):
            continue

        source = item.get("source") or item.get("article_id")
        content = item.get("content") or item.get("text")

        if source and source not in sources:
            sources.append(source)

        if content:
            instructions.append(str(content))

    return {
        "article_id": sources[0] if sources else None,
        "title": f"Knowledge retrieved for {issue_type}",
        "instructions": instructions or [
            "Relevant results were found, but no readable instructions were returned."
        ],
        "source": sources or None
    }


def determine_automation(issue_type, identity_verified, knowledge):
    """Choose only actions permitted by the demo's safety rules."""
    has_knowledge = bool(knowledge.get("source"))

    if issue_type == "expired_password":
        if not identity_verified:
            return {
                "decision": "needs_verification",
                "safe_to_automate": False,
                "reason": "Identity verification is required before password-reset automation."
            }

        return {
            "decision": "mock_execute",
            "safe_to_automate": True,
            "reason": "Identity verification was asserted for this demo; only a simulated reset is permitted."
        }

    if issue_type == "vpn":
        return {
            "decision": "guided_troubleshooting",
            "safe_to_automate": False,
            "reason": "Provide approved troubleshooting guidance; escalate if unresolved."
        }

    if issue_type == "security":
        return {
            "decision": "escalate",
            "safe_to_automate": False,
            "reason": "Potential security incidents require human investigation."
        }

    return {
        "decision": "escalate",
        "safe_to_automate": False,
        "reason": (
            "No relevant knowledge was found."
            if not has_knowledge
            else "The issue is not covered by an approved safe-automation rule."
        )
    }


def execute_mock_action(issue_type, identity_verified):
    """Simulate an action. This function never changes a real account."""
    if issue_type == "expired_password" and identity_verified:
        return {
            "executed": True,
            "mode": "mock",
            "action": "password_reset_simulation",
            "message": "Simulated password-reset action completed. No real password was changed."
        }

    return {
        "executed": False,
        "mode": "mock",
        "message": "No action executed."
    }


def validate_result(execution):
    """Validate only the simulated action result."""
    successful = (
        execution.get("executed") is True
        and execution.get("mode") == "mock"
    )

    return {
        "validated": successful,
        "validation_type": "mock_result_check",
        "note": (
            "Simulated action result passed validation; no real account was changed."
            if successful
            else "No successful mock action to validate."
        )
    }


def write_audit(case_id, ticket_id, issue_type, decision, outcome, payload):
    """Write an audit entry when the audit table is available."""
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Discover the actual schema rather than assuming column names.
        cursor.execute("SHOW COLUMNS FROM self_heal_audit")
        columns = {row[0] for row in cursor.fetchall()}

        candidates = {
            "case_id": case_id,
            "ticket_id": ticket_id,
            "issue_type": issue_type,
            "decision": decision,
            "outcome": outcome,
            "details": json.dumps(payload, default=str),
            "payload": json.dumps(payload, default=str),
            "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
        }

        values = {
            name: value
            for name, value in candidates.items()
            if name in columns
        }

        if values:
            names = ", ".join(f"`{name}`" for name in values)
            placeholders = ", ".join(["%s"] * len(values))
            cursor.execute(
                f"INSERT INTO self_heal_audit ({names}) VALUES ({placeholders})",
                tuple(values.values())
            )
            conn.commit()

    except Exception as exc:
        # Do not hide the workflow result if auditing itself fails.
        print("SELF-HEAL AUDIT ERROR:", repr(exc))
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def run_self_heal(description, ticket_id=None, identity_verified=False):
    """Run identify → diagnose → knowledge → decision → execute → validate → update."""

    description = (description or "").strip()
    if not description:
        raise ValueError("Please provide an issue description.")

    case_id = f"SH-{uuid.uuid4().hex[:8].upper()}"

    identified = identify_issue(description)
    issue_type = identified["issue_type"]

    diagnosis = diagnose_issue(issue_type, identity_verified)
    knowledge = get_knowledge(issue_type, description)

    decision = determine_automation(
        issue_type,
        bool(identity_verified),
        knowledge
    )

    execution = {"executed": False, "mode": "mock", "message": "No action executed."}
    validation = {
        "validated": False,
        "validation_type": "mock_result_check",
        "note": "No successful mock action to validate."
    }

    if decision["decision"] == "mock_execute":
        execution = execute_mock_action(issue_type, bool(identity_verified))
        validation = validate_result(execution)

    if decision["decision"] == "escalate":
        outcome = "escalated_to_human"
    elif decision["decision"] == "needs_verification":
        outcome = "needs_identity_verification"
    elif decision["decision"] == "guided_troubleshooting":
        outcome = "guidance_provided"
    elif validation["validated"]:
        outcome = "mock_action_validated"
    else:
        outcome = "mock_action_not_validated"

    # Attempt to create a ServiceNow incident for this self-heal case.
    service_now = {
        "connected": False,
        "status": "not_connected",
        "message": "ServiceNow incident has not been created."
    }

    try:
        snow_incident = create_servicenow_incident(
            short_description=f"Sorim.AI self-heal: {identified['summary']}"[:160],
            description=(
                f"Self-heal case: {case_id}\n"
                f"Local ticket ID: {ticket_id}\n"
                f"Issue: {description}\n"
                f"Diagnosis: {diagnosis['diagnosis']}\n"
                f"Decision: {decision['decision']}\n"
                f"Outcome: {outcome}\n"
                "Note: Any password-reset action in this demo is simulated."
            ),
            urgency="2" if issue_type in ("vpn", "security") else "3",
            impact="2" if issue_type == "security" else "3",
            category="network" if issue_type == "vpn" else "software"
        )

        service_now = {
            "connected": True,
            "status": "created",
            "incident_number": snow_incident.get("number"),
            "sys_id": snow_incident.get("sys_id"),
            "message": "ServiceNow incident created successfully."
        }

    except Exception as exc:
        print("SELF-HEAL SERVICENOW ERROR:", repr(exc))
        service_now = {
            "connected": False,
            "status": "failed",
            "message": "Could not create the ServiceNow incident.",
            "error": str(exc)[:500]
        }

    result = {
        "case_id": case_id,
        "ticket_id": ticket_id,
        "identified": identified,
        "diagnosis": diagnosis,
        "knowledge": knowledge,
        "decision": decision,
        "execution": execution,
        "validation": validation,
        "ticket_outcome": outcome,
        "service_now": service_now
    }

    write_audit(
        case_id=case_id,
        ticket_id=ticket_id,
        issue_type=issue_type,
        decision=decision["decision"],
        outcome=outcome,
        payload=result
    )

    return result
