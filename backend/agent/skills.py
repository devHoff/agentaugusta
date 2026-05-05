"""
Agent skills — modular prompt-based tools the agent can invoke.
Each skill takes context and returns a structured output.
"""
from .llm import chat
from ..memory import store


# ─────────────────────────────────────────────
# SKILL 1: Extract structured info from transcript
# ─────────────────────────────────────────────
def extract_transcript_insights(transcript: str, client_name: str, company: str) -> dict:
    system = """You are an expert project manager at Augusta, a consulting firm.
Analyze meeting transcripts and extract structured information.
Return your response as valid JSON only, no markdown code blocks."""

    user = f"""Analyze this meeting transcript for {client_name} at {company}.

Extract and return JSON with these exact fields:
{{
  "summary": "2-3 sentence summary of the meeting",
  "decisions": ["list of decisions made"],
  "commitments": ["list of commitments made by either party"],
  "action_items": [
    {{"owner": "person name", "task": "what they need to do", "due": "when"}}
  ],
  "open_items": ["unresolved questions or blockers"],
  "project_status": "one of: discovery / proposal / negotiation / active / delivered",
  "has_proposal_needed": true or false,
  "has_task_assignments": true or false,
  "key_risks": ["list of risks mentioned"],
  "client_sentiment": "positive / neutral / concerned / negative",
  "context_update": "brief paragraph to store as updated project context"
}}

TRANSCRIPT:
{transcript}"""

    raw = chat(system, user, model="gpt-5-mini", max_tokens=3000)
    import json, re
    # Strip markdown code blocks if present
    clean = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
    try:
        return json.loads(clean)
    except Exception:
        return {
            "summary": raw[:300],
            "decisions": [],
            "commitments": [],
            "action_items": [],
            "open_items": [],
            "project_status": "active",
            "has_proposal_needed": False,
            "has_task_assignments": True,
            "key_risks": [],
            "client_sentiment": "neutral",
            "context_update": raw[:500],
        }


# ─────────────────────────────────────────────
# SKILL 2: Draft next-steps email to client
# ─────────────────────────────────────────────
def draft_followup_email(
    client_name: str,
    company: str,
    transcript: str,
    insights: dict,
    memory_context: str,
) -> str:
    system = """You are Marcus Reid, an Engagement Lead at Augusta, a premium consulting firm.
Write professional, warm, and clear client emails. Be specific — reference actual items from the meeting.
Use proper email formatting with Subject line, greeting, body, and sign-off."""

    action_items_text = "\n".join(
        f"- {a['owner']}: {a['task']} (by {a.get('due', 'TBD')})"
        for a in insights.get("action_items", [])
    )

    user = f"""Draft a follow-up email to {client_name} at {company} after a meeting.

CLIENT HISTORY:
{memory_context}

MEETING SUMMARY:
{insights.get('summary', '')}

ACTION ITEMS AGREED:
{action_items_text or 'See email body'}

KEY DECISIONS:
{chr(10).join('- ' + d for d in insights.get('decisions', []))}

COMMITMENTS MADE:
{chr(10).join('- ' + c for c in insights.get('commitments', []))}

Write a professional follow-up email that:
1. Thanks them for the meeting
2. Summarizes key decisions (be specific)
3. Lists next steps with clear owners and dates
4. Sets the tone for the next interaction
5. Ends with a forward-looking statement

Email format:
Subject: [subject line]

[email body]"""

    return chat(system, user, model="gpt-5-mini", max_tokens=2000)


# ─────────────────────────────────────────────
# SKILL 3: Generate proposal document
# ─────────────────────────────────────────────
def generate_proposal(
    client_name: str,
    company: str,
    transcript: str,
    insights: dict,
    memory_context: str,
) -> str:
    system = """You are a senior consultant at Augusta. 
Write clear, compelling proposals in Markdown format.
Be specific, professional, and structured. Reference actual details from the engagement."""

    user = f"""Generate a project proposal for {company} based on recent discussions.

CLIENT CONTEXT:
{memory_context}

MEETING INSIGHTS:
Summary: {insights.get('summary', '')}
Commitments: {', '.join(insights.get('commitments', []))}
Key Risks: {', '.join(insights.get('key_risks', []))}

Create a professional proposal in Markdown with these sections:
# Proposal: [Project Title] for {company}

## Executive Summary
(2-3 paragraphs on what Augusta will deliver and why it matters)

## Scope of Work
(Detailed breakdown of deliverables by phase)

## Timeline & Milestones
(Table or list of key milestones with dates)

## Investment
(Pricing, payment terms, what's included)

## Team
(Augusta team members and their roles)

## Success Criteria
(Measurable outcomes)

## Next Steps
(What needs to happen to proceed)

Make it specific to {company}'s situation based on the transcript content."""

    return chat(system, user, model="gpt-5-mini", max_tokens=3000)


# ─────────────────────────────────────────────
# SKILL 4: Generate internal team plan
# ─────────────────────────────────────────────
def generate_team_plan(
    client_name: str,
    company: str,
    insights: dict,
    memory_context: str,
    augusta_team: list,
) -> str:
    system = """You are an Engagement Lead at Augusta creating an internal team plan.
Be direct, specific, and actionable. This is for internal use only — be frank about risks."""

    team_str = ", ".join(augusta_team) if augusta_team else "Augusta team"
    action_items = insights.get("action_items", [])
    action_text = "\n".join(
        f"- {a['owner']}: {a['task']} (by {a.get('due', 'TBD')})"
        for a in action_items
    )

    user = f"""Create an internal team action plan for the {company} engagement.

CURRENT PROJECT STATE:
{memory_context}

MEETING INSIGHTS:
{insights.get('summary', '')}

AGREED ACTION ITEMS:
{action_text or 'Extract from meeting context'}

OPEN ITEMS / BLOCKERS:
{chr(10).join('- ' + i for i in insights.get('open_items', []))}

KEY RISKS:
{chr(10).join('- ' + r for r in insights.get('key_risks', []))}

AUGUSTA TEAM: {team_str}

Generate an internal team plan in Markdown with:

# Internal Team Plan — {company}
## Post-Meeting Action Items
(Table: Owner | Task | Due Date | Priority)

## This Week's Focus
(Top 3 priorities for the team)

## Risks & Watch Items
(What to monitor, who owns mitigation)

## Client Sentiment & Relationship Notes
(Internal notes on client mood, key personalities, dynamics)

## Blockers Needing Escalation
(Anything that needs leadership attention)"""

    return chat(system, user, model="gpt-5-mini", max_tokens=2500)


# ─────────────────────────────────────────────
# SKILL 5: Research report (no prior client memory)
# ─────────────────────────────────────────────
def generate_research_report(
    company: str,
    attendees: list,
    industry: str,
) -> str:
    system = """You are a research analyst at Augusta preparing pre-meeting briefs.
Create concise, insightful research reports that help consultants walk into meetings prepared."""

    attendees_str = ", ".join(attendees) if attendees else "Unknown attendees"

    user = f"""Generate a pre-meeting research report for a first meeting with {company}.

Industry: {industry}
Known Attendees: {attendees_str}

Create a research report in Markdown with:

# Pre-Meeting Research Report: {company}

## Company Overview
(What does this company do? Size, market position, key products/services)

## Business Model
(How do they make money? Key revenue drivers)

## Industry Context
(Market trends, competitive landscape, key challenges in {industry})

## Known Attendees
(For each attendee: likely role, focus areas, what they probably care about)

## Strategic Priorities
(What are companies like {company} typically focused on right now?)

## Potential Pain Points
(Common challenges in {industry} that Augusta might help solve)

## Suggested Opening Questions
(5 good discovery questions to ask in the meeting)

## Augusta Angle
(How Augusta's capabilities likely align with their needs)

Note: This is based on general industry knowledge since we have no prior history with this client."""

    return chat(system, user, model="gpt-5-mini", max_tokens=2800)


# ─────────────────────────────────────────────
# SKILL 6: Meeting prep document (existing client)
# ─────────────────────────────────────────────
def generate_meeting_prep(
    client_name: str,
    company: str,
    memory_context: str,
    attendees: list,
    augusta_team: list,
) -> str:
    system = """You are an Engagement Lead at Augusta preparing your team for an upcoming client meeting.
Create actionable, specific meeting prep documents. Reference actual project details."""

    attendees_str = ", ".join(attendees) if attendees else "TBD"
    team_str = ", ".join(augusta_team) if augusta_team else "Augusta team"

    user = f"""Create a meeting prep document for the upcoming meeting with {company}.

FULL PROJECT CONTEXT:
{memory_context}

MEETING DETAILS:
Client Attendees: {attendees_str}
Augusta Team: {team_str}
Meeting is in 3 hours.

Generate a meeting prep document in Markdown:

# Meeting Prep: {company} — [Today's Date]

## Project Status Snapshot
(Current state in 3-4 bullet points)

## Since Last Meeting
(Key developments, completed items, new information)

## Open Items to Address
(List with owner and status for each open item)

## Agenda Suggestions
(Recommended agenda items with time allocations)

## Suggested Questions
(5-7 specific questions to ask based on current project state)

## Watch Out For
(Potential friction points, sensitivities, things to be careful about)

## Risks & Blockers
(Current risks with status)

## Talking Points
(Key messages Augusta wants to land in this meeting)

## What Success Looks Like
(What should we walk away with from this meeting?)"""

    return chat(system, user, model="gpt-5-mini", max_tokens=2800)


# ─────────────────────────────────────────────
# SKILL 7: Email reply
# ─────────────────────────────────────────────
def draft_email_reply(
    sender_name: str,
    sender_email: str,
    subject: str,
    email_body: str,
    client_name: str,
    company: str,
    memory_context: str,
) -> str:
    system = """You are an Engagement Lead at Augusta responding to client emails.
Be professional, thorough, and warm. Address every point raised in the email specifically.
Use proper email formatting."""

    user = f"""Draft a reply to this email from {sender_name} at {company}.

PROJECT CONTEXT:
{memory_context}

INCOMING EMAIL:
From: {sender_name} <{sender_email}>
Subject: {subject}

{email_body}

Write a complete, professional reply that:
1. Acknowledges their message warmly
2. Addresses EVERY point they raised (go through each numbered item or concern)
3. Provides clear answers or next steps for each item
4. Flags any issues that need team discussion
5. Ends positively with clear next steps

Email format:
Subject: Re: {subject}

[email body with proper greeting and sign-off as Marcus Reid / Diana Park, Engagement Lead at Augusta]"""

    return chat(system, user, model="gpt-5-mini", max_tokens=2500)
