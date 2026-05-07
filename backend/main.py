"""
FastAPI backend for Augusta Project Management Agent.
"""
import os
import sys

# Add the parent directory to path so `backend` package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import traceback

load_dotenv()

from backend.agent.orchestrator import (
    handle_transcript,
    handle_upcoming_meeting,
    handle_email_reply,
    handle_chat,
)
from backend.agent.tracing import (
    flush_traces,
    get_tracing_status,
    trace_agent_event,
    update_trace_output,
)
from backend.memory import store
from backend.data.test_data import TEST_CLIENTS, TRANSCRIPTS, EMAIL_REPLIES

app = FastAPI(title="Augusta PM Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
def shutdown_event():
    flush_traces()


@app.on_event("startup")
def startup_event():
    status = get_tracing_status()
    if status["enabled"] and status["sdk_installed"] and status["has_public_key"] and status["has_secret_key"]:
        print(f"Langfuse tracing enabled ({status['base_url'] or 'default host'})")
    else:
        print(f"Langfuse tracing not active: {status}")


# ─────────────────────────────────────────────
# Request Models
# ─────────────────────────────────────────────

class TranscriptEvent(BaseModel):
    client_id: str
    transcript_id: Optional[str] = None
    custom_transcript: Optional[str] = None


class MeetingEvent(BaseModel):
    client_id: str


class EmailEvent(BaseModel):
    client_id: str
    custom_email: Optional[dict] = None


class ChatRequest(BaseModel):
    client_id: str
    messages: List[dict]
    system_context: Optional[str] = ""


class RefineRequest(BaseModel):
    client_id: str
    output_id: str
    output_type: str
    output_title: str
    current_content: str
    instruction: str
    messages: List[dict]


class ResetRequest(BaseModel):
    client_id: Optional[str] = None


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "Augusta PM Agent"}


@app.get("/api/tracing/status")
def tracing_status():
    return get_tracing_status()


# ─────────────────────────────────────────────
# Meta: Clients & Test Data
# ─────────────────────────────────────────────

@app.get("/api/clients")
def get_clients():
    """Return all available test clients with their transcripts and emails."""
    result = []
    for client_id, meta in TEST_CLIENTS.items():
        transcripts = [
            {"id": t["id"], "title": t["title"], "date": t["date"]}
            for t in TRANSCRIPTS.get(client_id, [])
        ]
        email = EMAIL_REPLIES.get(client_id, {})
        memory = store.get_client(client_id)
        result.append({
            "client_id": client_id,
            "client_name": meta["client_name"],
            "company_name": meta["company_name"],
            "industry": meta["industry"],
            "transcripts": transcripts,
            "email": {
                "subject": email.get("subject", ""),
                "from_name": email.get("from_name", ""),
            } if email else None,
            "memory": memory,
        })
    return result


@app.get("/api/clients/{client_id}/memory")
def get_client_memory(client_id: str):
    """Get client memory state."""
    memory = store.get_client(client_id)
    if not memory:
        return {"client_id": client_id, "exists": False}
    return {"client_id": client_id, "exists": True, "memory": memory}


@app.get("/api/clients/{client_id}/summary")
def get_client_summary(client_id: str):
    """Get a text summary of the client state."""
    summary = store.get_client_summary(client_id)
    return {"client_id": client_id, "summary": summary}


@app.get("/api/clients/{client_id}/outputs")
def get_client_outputs(client_id: str):
    """Get all persisted generated outputs for a client, newest first."""
    outputs = store.get_outputs(client_id)
    return {"client_id": client_id, "outputs": outputs}


# ─────────────────────────────────────────────
# Agent Events
# ─────────────────────────────────────────────

@app.post("/api/events/transcript")
def event_transcript(req: TranscriptEvent):
    """Handle: Meeting transcript came in."""
    try:
        with trace_agent_event(
            name="process-transcript",
            client_id=req.client_id,
            event_type="transcript",
            input_data={
                "transcript_id": req.transcript_id,
                "has_custom_transcript": bool(req.custom_transcript),
            },
        ) as span:
            result = handle_transcript(
                client_id=req.client_id,
                transcript_id=req.transcript_id,
                custom_transcript=req.custom_transcript,
            )
            update_trace_output(span, {
                "output_types": list((result.get("outputs") or {}).keys()),
                "has_insights": bool(result.get("insights")),
            })
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/events/meeting")
def event_meeting(req: MeetingEvent):
    """Handle: Meeting in 3 hours."""
    try:
        with trace_agent_event(
            name="prepare-meeting",
            client_id=req.client_id,
            event_type="meeting",
            input_data={"client_id": req.client_id},
        ) as span:
            result = handle_upcoming_meeting(client_id=req.client_id)
            update_trace_output(span, {
                "branch": result.get("branch"),
                "output_types": list((result.get("outputs") or {}).keys()),
            })
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/events/email")
def event_email(req: EmailEvent):
    """Handle: Email reply came in."""
    try:
        with trace_agent_event(
            name="draft-email-reply",
            client_id=req.client_id,
            event_type="email",
            input_data={"has_custom_email": bool(req.custom_email)},
        ) as span:
            result = handle_email_reply(
                client_id=req.client_id,
                custom_email=req.custom_email,
            )
            update_trace_output(span, {
                "output_types": list((result.get("outputs") or {}).keys()),
                "incoming_subject": (result.get("incoming_email") or {}).get("subject"),
            })
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    """Chat with the agent about a client engagement."""
    try:
        with trace_agent_event(
            name="chat-response",
            client_id=req.client_id,
            event_type="chat",
            input_data={
                "message_count": len(req.messages),
                "has_system_context": bool(req.system_context),
            },
        ) as span:
            response = handle_chat(
                client_id=req.client_id,
                messages=req.messages,
                system_context=req.system_context or "",
            )
            update_trace_output(span, {"response_length": len(response)})
        return {"response": response}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/refine")
def refine_output_endpoint(req: RefineRequest):
    """Refine/tweak an existing generated output based on a user instruction."""
    try:
        from backend.agent.llm import chat_with_history
        meta_map = {c: d for c, d in store.get_all_clients().items()} if hasattr(store.get_all_clients(), 'items') else {}
        memory_context = store.get_client_summary(req.client_id)

        system = f"""You are an AI project management assistant at Augusta, a consulting firm.
You are refining a previously generated {req.output_type} document for a client engagement.

CURRENT PROJECT STATE:
{memory_context}

Your task: Apply the user's requested changes to the document below and return ONLY the revised document text — no explanations, no preamble, no "Here is the revised version:" prefix. Just the updated document content, ready to display as-is.

CURRENT DOCUMENT TITLE: {req.output_title}
CURRENT DOCUMENT CONTENT:
{req.current_content}"""

        messages = req.messages + [{"role": "user", "content": req.instruction}]
        refined = chat_with_history(
            system,
            messages,
            model="gpt-4o-mini",
            max_completion_tokens=1500,
            trace_name="output-refine",
            metadata={"feature": "refine", "output_type": req.output_type, "client_id": req.client_id},
        )
        return {
            "refined": True,
            "output_id": req.output_id,
            "output_type": req.output_type,
            "title": req.output_title,
            "content": refined,
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# Memory Management
# ─────────────────────────────────────────────

@app.post("/api/memory/reset")
def reset_memory(req: ResetRequest):
    """Reset memory for a client or all clients."""
    if req.client_id:
        store.delete_client(req.client_id)
        return {"message": f"Memory cleared for {req.client_id}"}
    else:
        store.reset_all()
        return {"message": "All memory cleared"}


@app.get("/api/memory/all")
def get_all_memory():
    """Get all client memory (for debugging)."""
    return store.get_all_clients()


# ─────────────────────────────────────────────
# Serve static UI
# ─────────────────────────────────────────────

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

@app.get("/")
def serve_ui():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/favicon.ico")
def favicon():
    # Return a minimal 1x1 transparent ICO (avoids 404 noise in browser)
    from fastapi.responses import Response
    import base64
    ico = base64.b64decode(
        "AAABAAEAAQEAAAEAGAAoAAAAFgAAACgAAAABAAAAAgAAAAEAGAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        "AAAAAAAAAAAAAAAAAAAA"
    )
    return Response(content=ico, media_type="image/x-icon")

# Mount static assets (must be last)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
