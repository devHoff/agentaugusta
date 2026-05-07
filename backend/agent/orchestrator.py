"""
Main agent orchestrator — routes events to the right skills,
updates memory, and returns structured outputs.
"""
from datetime import datetime
from ..memory import store
from ..data.test_data import TEST_CLIENTS, TRANSCRIPTS, EMAIL_REPLIES
from . import skills


def _get_client_meta(client_id: str) -> dict:
    return TEST_CLIENTS.get(client_id, {
        "client_id": client_id,
        "client_name": "Client",
        "company_name": client_id,
        "industry": "Unknown",
        "attendees": [],
        "augusta_team": [],
    })


# ─────────────────────────────────────────────
# EVENT 1: Meeting transcript came in
# ─────────────────────────────────────────────
def handle_transcript(client_id: str, transcript_id: str = None, custom_transcript: str = None) -> dict:
    """Process a meeting transcript and generate appropriate outputs."""
    meta = _get_client_meta(client_id)
    company = meta["company_name"]
    client_name = meta["client_name"]
    augusta_team = meta.get("augusta_team", [])

    # Get transcript content
    if custom_transcript:
        transcript_text = custom_transcript
        transcript_title = "Custom Transcript"
    else:
        client_transcripts = TRANSCRIPTS.get(client_id, [])
        if not client_transcripts:
            return {"error": f"No transcripts found for client '{client_id}'"}

        if transcript_id:
            transcript_obj = next((t for t in client_transcripts if t["id"] == transcript_id), None)
        else:
            # Auto-pick next unprocessed transcript
            existing_events = (store.get_client(client_id) or {}).get("events", [])
            processed_ids = {e.get("transcript_id") for e in existing_events if e.get("type") == "transcript"}
            transcript_obj = next((t for t in client_transcripts if t["id"] not in processed_ids), None)
            if not transcript_obj:
                transcript_obj = client_transcripts[-1]  # fallback to last

        if not transcript_obj:
            return {"error": f"Transcript '{transcript_id}' not found"}

        transcript_text = transcript_obj["content"]
        transcript_title = transcript_obj.get("title", "Meeting")

    # Initialize client in memory if first time
    existing = store.get_client(client_id)
    if not existing:
        store.upsert_client(client_id, {
            "client_name": client_name,
            "company_name": company,
            "industry": meta.get("industry", ""),
        })

    # Get current memory context
    memory_context = store.get_client_summary(client_id)

    # STEP 1: Extract insights from transcript
    insights = skills.extract_transcript_insights(transcript_text, client_name, company)

    # STEP 2: Always generate follow-up email
    email_draft = skills.draft_followup_email(
        client_name, company, transcript_text, insights, memory_context
    )

    outputs = {
        "event_type": "transcript",
        "client_id": client_id,
        "transcript_title": transcript_title,
        "timestamp": datetime.utcnow().isoformat(),
        "insights": insights,
        "outputs": {
            "email_draft": {
                "type": "email",
                "title": "📧 Follow-up Email to Client",
                "content": email_draft,
            }
        },
    }

    # STEP 3: Optionally generate proposal
    if insights.get("has_proposal_needed"):
        proposal = skills.generate_proposal(
            client_name, company, transcript_text, insights, memory_context
        )
        outputs["outputs"]["proposal"] = {
            "type": "proposal",
            "title": "📄 Proposal Document",
            "content": proposal,
        }

    # STEP 4: Optionally generate team plan
    if insights.get("has_task_assignments"):
        team_plan = skills.generate_team_plan(
            client_name, company, insights, memory_context, augusta_team
        )
        outputs["outputs"]["team_plan"] = {
            "type": "team_plan",
            "title": "✅ Internal Team Plan",
            "content": team_plan,
        }

    # STEP 5: Update memory
    store.upsert_client(client_id, {
        "project_status": insights.get("project_status", "active"),
        "extra_context": insights.get("context_update", ""),
    })
    store.append_event(client_id, {
        "type": "transcript",
        "transcript_id": transcript_obj["id"] if not custom_transcript else "custom",
        "summary": insights.get("summary", "Meeting processed"),
        "title": transcript_title,
    })
    for item in insights.get("open_items", []):
        store.append_open_item(client_id, item)

    # STEP 6: Persist generated outputs to history
    for key, item in outputs["outputs"].items():
        persisted = store.append_output(client_id, {
            "type": item["type"],
            "title": item["title"],
            "content": item["content"],
            "event_type": outputs["event_type"],
            "transcript_id": transcript_obj["id"] if not custom_transcript else "custom",
            "transcript_title": transcript_title,
        })
        outputs["outputs"][key].update({
            "id": persisted["id"],
            "created_at": persisted["created_at"],
            "event_type": persisted["event_type"],
            "transcript_id": persisted.get("transcript_id"),
            "transcript_title": persisted.get("transcript_title"),
            "versions": persisted.get("versions", []),
        })

    return outputs


# ─────────────────────────────────────────────
# EVENT 2: Meeting in 3 hours
# ─────────────────────────────────────────────
def handle_upcoming_meeting(client_id: str) -> dict:
    """Generate prep materials for an upcoming meeting."""
    meta = _get_client_meta(client_id)
    company = meta["company_name"]
    client_name = meta["client_name"]
    attendees = meta.get("attendees", [])
    augusta_team = meta.get("augusta_team", [])
    industry = meta.get("industry", "")

    existing = store.get_client(client_id)

    outputs = {
        "event_type": "upcoming_meeting",
        "client_id": client_id,
        "timestamp": datetime.utcnow().isoformat(),
        "outputs": {},
    }

    if not existing:
        # No prior memory — generate research report
        research = skills.generate_research_report(company, attendees, industry)
        outputs["branch"] = "new_client"
        outputs["outputs"]["research_report"] = {
            "type": "research_report",
            "title": "🔍 Company Research Report",
            "content": research,
        }
        # Initialize client in memory
        store.upsert_client(client_id, {
            "client_name": client_name,
            "company_name": company,
            "industry": industry,
        })
        store.append_event(client_id, {
            "type": "research",
            "summary": f"Research report generated before first meeting with {company}",
        })
    else:
        # Existing client — generate meeting prep
        memory_context = store.get_client_summary(client_id)
        prep = skills.generate_meeting_prep(
            client_name, company, memory_context, attendees, augusta_team
        )
        outputs["branch"] = "existing_client"
        outputs["outputs"]["meeting_prep"] = {
            "type": "meeting_prep",
            "title": "🧠 Pre-Meeting Briefing",
            "content": prep,
        }
        store.append_event(client_id, {
            "type": "meeting_prep",
            "summary": f"Pre-meeting briefing generated for {company}",
        })

    # Persist generated outputs to history
    for key, item in outputs["outputs"].items():
        persisted = store.append_output(client_id, {
            "type": item["type"],
            "title": item["title"],
            "content": item["content"],
            "event_type": outputs["event_type"],
        })
        outputs["outputs"][key].update({
            "id": persisted["id"],
            "created_at": persisted["created_at"],
            "event_type": persisted["event_type"],
            "versions": persisted.get("versions", []),
        })

    return outputs


# ─────────────────────────────────────────────
# EVENT 3: Email reply came in
# ─────────────────────────────────────────────
def handle_email_reply(client_id: str, custom_email: dict = None) -> dict:
    """Generate a contextual response to an incoming client email."""
    meta = _get_client_meta(client_id)
    company = meta["company_name"]
    client_name = meta["client_name"]

    # Get email content
    if custom_email:
        email_data = custom_email
    else:
        email_data = EMAIL_REPLIES.get(client_id)
        if not email_data:
            return {"error": f"No email reply found for client '{client_id}'"}

    # Ensure client exists in memory
    existing = store.get_client(client_id)
    if not existing:
        store.upsert_client(client_id, {
            "client_name": client_name,
            "company_name": company,
        })

    memory_context = store.get_client_summary(client_id)

    # Generate reply
    reply = skills.draft_email_reply(
        sender_name=email_data.get("from_name", client_name),
        sender_email=email_data.get("from", ""),
        subject=email_data.get("subject", ""),
        email_body=email_data.get("content", ""),
        client_name=client_name,
        company=company,
        memory_context=memory_context,
    )

    # Update memory
    store.append_event(client_id, {
        "type": "email_received",
        "summary": f"Email received from {email_data.get('from_name', client_name)}: {email_data.get('subject', '')}",
    })

    result = {
        "event_type": "email_reply",
        "client_id": client_id,
        "timestamp": datetime.utcnow().isoformat(),
        "incoming_email": {
            "from": email_data.get("from_name", ""),
            "subject": email_data.get("subject", ""),
            "preview": email_data.get("content", "")[:200] + "...",
        },
        "outputs": {
            "email_reply": {
                "type": "email",
                "title": "📧 Email Response Draft",
                "content": reply,
            }
        },
    }

    # Persist generated outputs to history
    for key, item in result["outputs"].items():
        persisted = store.append_output(client_id, {
            "type": item["type"],
            "title": item["title"],
            "content": item["content"],
            "event_type": result["event_type"],
            "subject": email_data.get("subject", ""),
        })
        result["outputs"][key].update({
            "id": persisted["id"],
            "created_at": persisted["created_at"],
            "event_type": persisted["event_type"],
            "subject": persisted.get("subject"),
            "versions": persisted.get("versions", []),
        })

    return result


# ─────────────────────────────────────────────
# Chat / refine interface
# ─────────────────────────────────────────────
def handle_chat(client_id: str, messages: list, system_context: str = "") -> str:
    """Chat with the agent about a specific client/project."""
    from .llm import chat_with_history

    meta = _get_client_meta(client_id)
    company = meta["company_name"]
    memory_context = store.get_client_summary(client_id)

    system = f"""You are an AI project management assistant at Augusta, a consulting firm.
You are helping manage the {company} client engagement.

CURRENT PROJECT STATE:
{memory_context}

{system_context}

Help the user with questions, refinements, or analysis about this engagement.
Be specific, use details from the project context. Keep responses concise but complete."""

    return chat_with_history(
        system,
        messages,
        model="gpt-4o-mini",
        max_completion_tokens=1000,
        trace_name="client-chat-response",
        metadata={"feature": "chat", "company": company, "client_id": client_id},
    )
