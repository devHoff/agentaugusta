"""
FastAPI backend for Augusta Project Management Agent.
"""
import os
import sys

# Add the parent directory to path so `backend` package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import traceback

from backend.agent.orchestrator import (
    handle_transcript,
    handle_upcoming_meeting,
    handle_email_reply,
    handle_chat,
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


class ResetRequest(BaseModel):
    client_id: Optional[str] = None


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "Augusta PM Agent"}


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


# ─────────────────────────────────────────────
# Agent Events
# ─────────────────────────────────────────────

@app.post("/api/events/transcript")
def event_transcript(req: TranscriptEvent):
    """Handle: Meeting transcript came in."""
    try:
        result = handle_transcript(
            client_id=req.client_id,
            transcript_id=req.transcript_id,
            custom_transcript=req.custom_transcript,
        )
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
        result = handle_upcoming_meeting(client_id=req.client_id)
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
        result = handle_email_reply(
            client_id=req.client_id,
            custom_email=req.custom_email,
        )
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
        response = handle_chat(
            client_id=req.client_id,
            messages=req.messages,
            system_context=req.system_context or "",
        )
        return {"response": response}
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
