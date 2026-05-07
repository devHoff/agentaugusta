"""
Simple JSON-based memory store for persisting client/project state.
"""
import json
import os
from datetime import datetime
from typing import Any, Optional

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")


def _load() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def _save(data: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_client(client_id: str) -> Optional[dict]:
    data = _load()
    return data.get(client_id)


def get_all_clients() -> dict:
    return _load()


def upsert_client(client_id: str, updates: dict):
    data = _load()
    if client_id not in data:
        data[client_id] = {
            "client_id": client_id,
            "created_at": datetime.utcnow().isoformat(),
            "events": [],
            "open_items": [],
            "decisions": [],
            "generated_outputs": [],
            "project_status": "discovery",
            "last_updated": datetime.utcnow().isoformat(),
        }
    # Ensure generated_outputs exists on old records
    data[client_id].setdefault("generated_outputs", [])
    data[client_id].update(updates)
    data[client_id]["last_updated"] = datetime.utcnow().isoformat()
    _save(data)


def append_event(client_id: str, event: dict):
    data = _load()
    if client_id not in data:
        upsert_client(client_id, {})
        data = _load()
    event["timestamp"] = datetime.utcnow().isoformat()
    data[client_id].setdefault("events", []).append(event)
    data[client_id]["last_updated"] = datetime.utcnow().isoformat()
    _save(data)


def append_open_item(client_id: str, item: str):
    data = _load()
    if client_id not in data:
        upsert_client(client_id, {})
        data = _load()
    data[client_id].setdefault("open_items", []).append({
        "item": item,
        "added_at": datetime.utcnow().isoformat(),
        "resolved": False,
    })
    data[client_id]["last_updated"] = datetime.utcnow().isoformat()
    _save(data)


def resolve_open_item(client_id: str, item_index: int):
    data = _load()
    if client_id in data and "open_items" in data[client_id]:
        items = data[client_id]["open_items"]
        if 0 <= item_index < len(items):
            items[item_index]["resolved"] = True
    data[client_id]["last_updated"] = datetime.utcnow().isoformat()
    _save(data)


def get_client_summary(client_id: str) -> str:
    """Return a text summary of client state for use in prompts."""
    client = get_client(client_id)
    if not client:
        return "No prior information about this client."

    events = client.get("events", [])
    open_items = [i for i in client.get("open_items", []) if not i.get("resolved")]
    decisions = client.get("decisions", [])

    lines = [
        f"Client: {client.get('client_name', client_id)}",
        f"Company: {client.get('company_name', 'Unknown')}",
        f"Project Status: {client.get('project_status', 'Unknown')}",
        f"Last Updated: {client.get('last_updated', 'Unknown')}",
        "",
        f"Total Events Logged: {len(events)}",
    ]

    if events:
        lines.append("Recent Events:")
        for e in events[-5:]:
            lines.append(f"  - [{e.get('type', 'event')}] {e.get('summary', '')} ({e.get('timestamp', '')[:10]})")

    if open_items:
        lines.append(f"\nOpen Items ({len(open_items)}):")
        for item in open_items[-10:]:
            lines.append(f"  • {item['item']}")

    if decisions:
        lines.append(f"\nKey Decisions:")
        for d in decisions[-5:]:
            lines.append(f"  • {d}")

    extra = client.get("extra_context", "")
    if extra:
        lines.append(f"\nAdditional Context:\n{extra}")

    return "\n".join(lines)


def append_output(client_id: str, output: dict):
    """Persist a generated output item for a client."""
    import uuid
    data = _load()
    if client_id not in data:
        upsert_client(client_id, {})
        data = _load()
    data[client_id].setdefault("generated_outputs", [])
    output["id"] = str(uuid.uuid4())
    output["created_at"] = datetime.utcnow().isoformat()
    output.setdefault("versions", [])
    data[client_id]["generated_outputs"].append(output)
    data[client_id]["last_updated"] = datetime.utcnow().isoformat()
    _save(data)
    return output


def append_output_version(client_id: str, output_id: str, version: dict) -> Optional[dict]:
    """Append a refined version to an existing generated output."""
    import uuid
    data = _load()
    client = data.get(client_id)
    if not client:
        return None

    for output in client.get("generated_outputs", []):
        if output.get("id") == output_id:
            output.setdefault("versions", [])
            version["id"] = str(uuid.uuid4())
            version["created_at"] = datetime.utcnow().isoformat()
            version["version_number"] = len(output["versions"]) + 2
            output["versions"].append(version)
            client["last_updated"] = datetime.utcnow().isoformat()
            _save(data)
            return version

    return None


def get_outputs(client_id: str) -> list:
    """Return all generated outputs for a client, newest first."""
    data = _load()
    client = data.get(client_id, {})
    outputs = client.get("generated_outputs", [])
    return list(reversed(outputs))


def delete_client(client_id: str):
    data = _load()
    data.pop(client_id, None)
    _save(data)


def reset_all():
    _save({})
