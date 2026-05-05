const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface OutputItem {
  type: 'email' | 'proposal' | 'team_plan' | 'meeting_prep' | 'research_report';
  title: string;
  content: string;
}

export interface AgentResult {
  event_type: string;
  client_id: string;
  timestamp: string;
  insights?: Record<string, unknown>;
  outputs: Record<string, OutputItem>;
  branch?: string;
  incoming_email?: { from: string; subject: string; preview: string };
  transcript_title?: string;
  error?: string;
}

export interface ClientInfo {
  client_id: string;
  client_name: string;
  company_name: string;
  industry: string;
  transcripts: { id: string; title: string; date: string }[];
  email: { subject: string; from_name: string } | null;
  memory: Record<string, unknown> | null;
}

export async function fetchClients(): Promise<ClientInfo[]> {
  const res = await fetch(`${BASE_URL}/api/clients`);
  if (!res.ok) throw new Error('Failed to fetch clients');
  return res.json();
}

export async function triggerTranscript(
  clientId: string,
  transcriptId?: string
): Promise<AgentResult> {
  const res = await fetch(`${BASE_URL}/api/events/transcript`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId, transcript_id: transcriptId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Transcript processing failed');
  }
  return res.json();
}

export async function triggerMeeting(clientId: string): Promise<AgentResult> {
  const res = await fetch(`${BASE_URL}/api/events/meeting`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Meeting prep failed');
  }
  return res.json();
}

export async function triggerEmail(clientId: string): Promise<AgentResult> {
  const res = await fetch(`${BASE_URL}/api/events/email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Email processing failed');
  }
  return res.json();
}

export async function sendChat(
  clientId: string,
  messages: { role: string; content: string }[],
  systemContext?: string
): Promise<string> {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId, messages, system_context: systemContext }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Chat failed');
  }
  const data = await res.json();
  return data.response;
}

export async function resetMemory(clientId?: string): Promise<void> {
  await fetch(`${BASE_URL}/api/memory/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId || null }),
  });
}

export async function getClientMemory(clientId: string) {
  const res = await fetch(`${BASE_URL}/api/clients/${clientId}/memory`);
  if (!res.ok) return null;
  return res.json();
}
