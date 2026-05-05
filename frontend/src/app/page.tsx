'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Zap, AlertCircle, X, ChevronRight, RotateCcw, Sparkles, Activity } from 'lucide-react';
import ClientSelector from '@/components/ClientSelector';
import EventButtons from '@/components/EventButtons';
import OutputPanel from '@/components/OutputPanel';
import ChatPanel from '@/components/ChatPanel';
import MemoryPanel from '@/components/MemoryPanel';
import {
  fetchClients,
  triggerTranscript,
  triggerMeeting,
  triggerEmail,
  sendChat,
  resetMemory,
  getClientMemory,
  type ClientInfo,
  type AgentResult,
} from '@/lib/api';

interface HistoryEntry {
  id: string;
  event: string;
  client: string;
  timestamp: string;
  outputCount: number;
}

export default function Home() {
  const [clients, setClients] = useState<ClientInfo[]>([]);
  const [selectedClient, setSelectedClient] = useState<ClientInfo | null>(null);
  const [selectedTranscriptId, setSelectedTranscriptId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeEvent, setActiveEvent] = useState<string | null>(null);
  const [result, setResult] = useState<AgentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [clientMemory, setClientMemory] = useState<Record<string, unknown> | null>(null);
  const [showChat, setShowChat] = useState(false);

  // Load clients
  const loadClients = useCallback(async () => {
    try {
      const data = await fetchClients();
      setClients(data);
    } catch (e) {
      console.error('Failed to load clients:', e);
    }
  }, []);

  useEffect(() => {
    loadClients();
  }, [loadClients]);

  // Refresh client memory
  const refreshMemory = useCallback(async () => {
    if (!selectedClient) return;
    try {
      const mem = await getClientMemory(selectedClient.client_id);
      setClientMemory(mem?.memory || null);
    } catch {
      setClientMemory(null);
    }
  }, [selectedClient]);

  useEffect(() => {
    refreshMemory();
  }, [refreshMemory]);

  const handleSelectClient = async (client: ClientInfo) => {
    setSelectedClient(client);
    setSelectedTranscriptId(client.transcripts[0]?.id || null);
    setResult(null);
    setError(null);
    setShowChat(false);
    // Load memory
    try {
      const mem = await getClientMemory(client.client_id);
      setClientMemory(mem?.memory || null);
    } catch {
      setClientMemory(null);
    }
  };

  const handleEvent = async (eventType: 'transcript' | 'email' | 'meeting') => {
    if (!selectedClient || loading) return;
    setLoading(true);
    setActiveEvent(eventType);
    setError(null);
    setResult(null);

    try {
      let res: AgentResult;
      if (eventType === 'transcript') {
        res = await triggerTranscript(selectedClient.client_id, selectedTranscriptId || undefined);
      } else if (eventType === 'email') {
        res = await triggerEmail(selectedClient.client_id);
      } else {
        res = await triggerMeeting(selectedClient.client_id);
      }
      setResult(res);

      // Add to history
      const entry: HistoryEntry = {
        id: Date.now().toString(),
        event: eventType,
        client: selectedClient.company_name,
        timestamp: new Date().toLocaleTimeString(),
        outputCount: Object.keys(res.outputs || {}).length,
      };
      setHistory((h) => [entry, ...h].slice(0, 10));

      // Refresh memory & clients
      await refreshMemory();
      await loadClients();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong');
    } finally {
      setLoading(false);
      setActiveEvent(null);
    }
  };

  const handleResetMemory = async (clientId?: string) => {
    await resetMemory(clientId);
    await loadClients();
    if (selectedClient) {
      await refreshMemory();
    }
    setResult(null);
  };

  const handleChat = async (messages: { role: string; content: string }[]) => {
    if (!selectedClient) throw new Error('No client selected');
    return sendChat(
      selectedClient.client_id,
      messages as { role: 'user' | 'assistant'; content: string }[]
    );
  };

  const EVENT_LABELS: Record<string, string> = {
    transcript: '📝 Transcript',
    email: '📧 Email Reply',
    meeting: '📅 Upcoming Meeting',
  };

  const outputItems = result ? Object.values(result.outputs || {}) : [];

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}
    >
      {/* Top Nav */}
      <header
        className="border-b sticky top-0 z-50"
        style={{
          backgroundColor: 'rgba(15,17,23,0.9)',
          borderColor: 'var(--border)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <div className="max-w-screen-2xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #6366f1, #818cf8)' }}
            >
              <Zap size={16} className="text-white" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight" style={{ color: '#fff' }}>
                Augusta
              </span>
              <span className="text-sm ml-2" style={{ color: 'var(--text-secondary)' }}>
                PM Agent
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Activity indicator */}
            {loading && (
              <div className="flex items-center gap-2 text-sm" style={{ color: '#818cf8' }}>
                <div className="spinner" />
                <span>Agent working...</span>
              </div>
            )}

            {/* History */}
            {history.length > 0 && (
              <div className="flex items-center gap-1.5">
                <Activity size={13} style={{ color: 'var(--text-secondary)' }} />
                <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {history.length} event{history.length !== 1 ? 's' : ''} today
                </span>
              </div>
            )}

            {selectedClient && (
              <div
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm"
                style={{
                  backgroundColor: 'rgba(99,102,241,0.12)',
                  border: '1px solid rgba(99,102,241,0.25)',
                  color: '#818cf8',
                }}
              >
                <span
                  className="w-5 h-5 rounded flex items-center justify-center text-xs font-bold"
                  style={{ backgroundColor: 'rgba(99,102,241,0.3)' }}
                >
                  {selectedClient.company_name.charAt(0)}
                </span>
                {selectedClient.company_name}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="max-w-screen-2xl mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* LEFT SIDEBAR — Client Selection + Controls */}
          <div className="col-span-3 space-y-5">
            {/* Client Selection */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ backgroundColor: '#6366f1' }}
                />
                <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-secondary)' }}>
                  Clients
                </span>
              </div>
              <ClientSelector
                clients={clients}
                selectedClient={selectedClient}
                selectedTranscriptId={selectedTranscriptId}
                onSelectClient={handleSelectClient}
                onSelectTranscript={setSelectedTranscriptId}
                onResetMemory={handleResetMemory}
                loading={loading}
              />
            </div>

            {/* Event Triggers */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ backgroundColor: '#34d399' }}
                />
                <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-secondary)' }}>
                  Trigger Event
                </span>
              </div>
              <EventButtons
                onTranscript={() => handleEvent('transcript')}
                onEmail={() => handleEvent('email')}
                onMeeting={() => handleEvent('meeting')}
                loading={loading}
                activeEvent={activeEvent}
                hasClient={!!selectedClient}
                hasTranscript={(selectedClient?.transcripts?.length ?? 0) > 0}
                hasEmail={!!selectedClient?.email}
              />
            </div>

            {/* Memory */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: '#34d399' }} />
                <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-secondary)' }}>
                  Project Memory
                </span>
              </div>
              <MemoryPanel memory={clientMemory as any} />
            </div>

            {/* Recent Activity */}
            {history.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: '#fbbf24' }} />
                  <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-secondary)' }}>
                    Recent Activity
                  </span>
                </div>
                <div
                  className="rounded-xl border overflow-hidden"
                  style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
                >
                  {history.slice(0, 5).map((entry) => (
                    <div
                      key={entry.id}
                      className="px-3 py-2.5 border-b flex items-center justify-between last:border-0"
                      style={{ borderColor: 'var(--border)' }}
                    >
                      <div>
                        <div className="text-xs font-medium" style={{ color: 'var(--text-primary)' }}>
                          {EVENT_LABELS[entry.event]} · {entry.client}
                        </div>
                        <div className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                          {entry.outputCount} output{entry.outputCount !== 1 ? 's' : ''} · {entry.timestamp}
                        </div>
                      </div>
                      <ChevronRight size={12} style={{ color: 'var(--text-secondary)' }} />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* CENTER — Outputs */}
          <div className="col-span-6 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-lg font-bold" style={{ color: '#fff' }}>
                  {result
                    ? `${EVENT_LABELS[result.event_type] || result.event_type} — ${selectedClient?.company_name}`
                    : selectedClient
                    ? `${selectedClient.company_name} Engagement`
                    : 'AI Project Management Agent'}
                </h1>
                <p className="text-sm mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                  {result
                    ? `${outputItems.length} output${outputItems.length !== 1 ? 's' : ''} generated · ${new Date(result.timestamp).toLocaleTimeString()}`
                    : selectedClient
                    ? 'Select an event to trigger the agent'
                    : 'Select a client to get started'}
                </p>
              </div>
              {result && (
                <button
                  onClick={() => setResult(null)}
                  className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg transition-all"
                  style={{
                    backgroundColor: 'rgba(255,255,255,0.06)',
                    color: 'var(--text-secondary)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <RotateCcw size={12} />
                  Clear
                </button>
              )}
            </div>

            {/* Error */}
            {error && (
              <div
                className="flex items-start gap-3 p-4 rounded-xl border animate-fadeIn"
                style={{
                  backgroundColor: 'rgba(239,68,68,0.08)',
                  borderColor: 'rgba(239,68,68,0.25)',
                }}
              >
                <AlertCircle size={16} style={{ color: '#f87171', marginTop: 1 }} />
                <div className="flex-1">
                  <div className="font-semibold text-sm" style={{ color: '#f87171' }}>
                    Agent Error
                  </div>
                  <div className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                    {error}
                  </div>
                </div>
                <button onClick={() => setError(null)}>
                  <X size={14} style={{ color: 'var(--text-secondary)' }} />
                </button>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div
                className="rounded-xl border p-8 flex flex-col items-center gap-4 animate-fadeIn"
                style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
              >
                <div
                  className="w-14 h-14 rounded-full flex items-center justify-center"
                  style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.3), rgba(129,140,248,0.2))' }}
                >
                  <Sparkles size={24} style={{ color: '#818cf8' }} className="animate-pulse-subtle" />
                </div>
                <div className="text-center">
                  <p className="font-semibold" style={{ color: '#fff' }}>
                    Agent is working...
                  </p>
                  <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                    {activeEvent === 'transcript' && 'Analyzing transcript and generating outputs'}
                    {activeEvent === 'email' && 'Reading email and crafting response'}
                    {activeEvent === 'meeting' && 'Preparing meeting briefing'}
                  </p>
                </div>
                <div className="flex gap-1.5 mt-2">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-2 h-2 rounded-full"
                      style={{
                        backgroundColor: '#6366f1',
                        animation: `pulse-subtle 1.5s ${i * 0.2}s ease-in-out infinite`,
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Incoming Email Preview */}
            {result?.incoming_email && (
              <div
                className="rounded-xl border p-4 animate-fadeIn"
                style={{
                  backgroundColor: 'rgba(139,92,246,0.08)',
                  borderColor: 'rgba(139,92,246,0.2)',
                }}
              >
                <div className="text-xs font-semibold mb-2" style={{ color: '#a78bfa' }}>
                  📬 Incoming Email
                </div>
                <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  {result.incoming_email.subject}
                </div>
                <div className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                  From: {result.incoming_email.from}
                </div>
                <div className="text-xs mt-2 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  {result.incoming_email.preview}
                </div>
              </div>
            )}

            {/* Transcript Title */}
            {result?.transcript_title && (
              <div
                className="rounded-xl border p-3 flex items-center gap-2 animate-fadeIn"
                style={{
                  backgroundColor: 'rgba(59,130,246,0.08)',
                  borderColor: 'rgba(59,130,246,0.2)',
                }}
              >
                <span style={{ color: '#60a5fa' }}>📝</span>
                <div className="text-sm">
                  <span className="font-medium" style={{ color: '#60a5fa' }}>Transcript: </span>
                  <span style={{ color: 'var(--text-primary)' }}>{result.transcript_title}</span>
                  {result.branch === 'new_client' && (
                    <span
                      className="ml-2 text-xs px-2 py-0.5 rounded-full"
                      style={{ backgroundColor: 'rgba(236,72,153,0.15)', color: '#f472b6' }}
                    >
                      New Client
                    </span>
                  )}
                  {result.branch === 'existing_client' && (
                    <span
                      className="ml-2 text-xs px-2 py-0.5 rounded-full"
                      style={{ backgroundColor: 'rgba(16,185,129,0.15)', color: '#34d399' }}
                    >
                      Existing Client
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Output Panels */}
            {outputItems.length > 0 && (
              <div className="space-y-4">
                {outputItems.map((output, i) => (
                  <OutputPanel
                    key={i}
                    output={output}
                    defaultOpen={i === 0}
                  />
                ))}
              </div>
            )}

            {/* Empty State */}
            {!loading && !result && !error && (
              <div
                className="rounded-xl border p-12 flex flex-col items-center gap-6 text-center"
                style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
              >
                <div
                  className="w-16 h-16 rounded-2xl flex items-center justify-center"
                  style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(129,140,248,0.1))' }}
                >
                  <Zap size={28} style={{ color: '#6366f1' }} />
                </div>
                <div>
                  <h2 className="text-xl font-bold" style={{ color: '#fff' }}>
                    Augusta PM Agent
                  </h2>
                  <p className="text-sm mt-2 max-w-md" style={{ color: 'var(--text-secondary)' }}>
                    Select a client on the left, then trigger an event to see the AI agent
                    in action. It will automatically generate emails, proposals, team plans,
                    and meeting briefs.
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-3 w-full max-w-md">
                  {[
                    { icon: '📝', label: 'Transcript', desc: 'Extracts insights, drafts email, creates plans' },
                    { icon: '📧', label: 'Email Reply', desc: 'Reads context, drafts a full response' },
                    { icon: '📅', label: 'Meeting Prep', desc: 'Briefing doc or research report' },
                  ].map((item) => (
                    <div
                      key={item.label}
                      className="rounded-xl border p-3 text-center"
                      style={{
                        backgroundColor: 'rgba(255,255,255,0.03)',
                        borderColor: 'var(--border)',
                      }}
                    >
                      <div className="text-2xl mb-2">{item.icon}</div>
                      <div className="text-xs font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                        {item.label}
                      </div>
                      <div className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                        {item.desc}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* RIGHT SIDEBAR — Chat + Insights */}
          <div className="col-span-3 space-y-5">
            {/* Chat Toggle */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: '#818cf8' }} />
                  <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-secondary)' }}>
                    Ask the Agent
                  </span>
                </div>
                {selectedClient && (
                  <button
                    onClick={() => setShowChat(!showChat)}
                    className="text-xs px-2.5 py-1 rounded-lg transition-all"
                    style={{
                      backgroundColor: showChat ? 'rgba(99,102,241,0.25)' : 'rgba(99,102,241,0.1)',
                      color: '#818cf8',
                      border: '1px solid rgba(99,102,241,0.3)',
                    }}
                  >
                    {showChat ? 'Hide' : 'Open'}
                  </button>
                )}
              </div>

              {showChat && selectedClient ? (
                <ChatPanel
                  clientId={selectedClient.client_id}
                  companyName={selectedClient.company_name}
                  onSend={handleChat}
                />
              ) : (
                <div
                  className="rounded-xl border p-5 flex flex-col items-center gap-3 text-center cursor-pointer transition-all"
                  style={{
                    backgroundColor: 'var(--bg-card)',
                    borderColor: 'var(--border)',
                  }}
                  onClick={() => selectedClient && setShowChat(true)}
                >
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(99,102,241,0.15)' }}
                  >
                    <span className="text-xl">💬</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                      Chat Interface
                    </p>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                      {selectedClient
                        ? 'Ask questions, refine outputs, explore the engagement'
                        : 'Select a client to chat about their engagement'}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Agent Insights (when result available) */}
            {result?.insights && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: '#f472b6' }} />
                  <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-secondary)' }}>
                    Agent Insights
                  </span>
                </div>
                <div
                  className="rounded-xl border overflow-hidden animate-fadeIn"
                  style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
                >
                  {/* Sentiment */}
                  {(result.insights as any).client_sentiment && (
                    <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
                      <div className="text-xs font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>
                        Client Sentiment
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm">
                          {(result.insights as any).client_sentiment === 'positive' && '😊'}
                          {(result.insights as any).client_sentiment === 'neutral' && '😐'}
                          {(result.insights as any).client_sentiment === 'concerned' && '😟'}
                          {(result.insights as any).client_sentiment === 'negative' && '😠'}
                        </span>
                        <span
                          className="text-xs px-2 py-0.5 rounded-full capitalize font-medium"
                          style={{
                            backgroundColor:
                              (result.insights as any).client_sentiment === 'positive'
                                ? 'rgba(16,185,129,0.15)'
                                : (result.insights as any).client_sentiment === 'concerned'
                                ? 'rgba(245,158,11,0.15)'
                                : 'rgba(99,102,241,0.15)',
                            color:
                              (result.insights as any).client_sentiment === 'positive'
                                ? '#34d399'
                                : (result.insights as any).client_sentiment === 'concerned'
                                ? '#fbbf24'
                                : '#818cf8',
                          }}
                        >
                          {(result.insights as any).client_sentiment}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Key Decisions */}
                  {((result.insights as any).decisions?.length ?? 0) > 0 && (
                    <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--border)' }}>
                      <div className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
                        Decisions Made
                      </div>
                      <ul className="space-y-1">
                        {((result.insights as any).decisions as string[]).slice(0, 4).map((d, i) => (
                          <li key={i} className="text-xs flex items-start gap-1.5">
                            <span style={{ color: '#34d399' }}>✓</span>
                            <span style={{ color: 'var(--text-primary)' }}>{d}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Key Risks */}
                  {((result.insights as any).key_risks?.length ?? 0) > 0 && (
                    <div className="px-4 py-3">
                      <div className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
                        Risks Identified
                      </div>
                      <ul className="space-y-1">
                        {((result.insights as any).key_risks as string[]).slice(0, 4).map((r, i) => (
                          <li key={i} className="text-xs flex items-start gap-1.5">
                            <span style={{ color: '#fbbf24' }}>⚠</span>
                            <span style={{ color: 'var(--text-secondary)' }}>{r}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* How to use guide */}
            {!result && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: '#fbbf24' }} />
                  <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-secondary)' }}>
                    How It Works
                  </span>
                </div>
                <div
                  className="rounded-xl border p-4 space-y-3"
                  style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
                >
                  {[
                    {
                      step: '1',
                      title: 'Select a Client',
                      desc: 'Choose FinoVa or MedBridge with their transcripts',
                    },
                    {
                      step: '2',
                      title: 'Trigger an Event',
                      desc: 'Simulate transcript, email, or upcoming meeting',
                    },
                    {
                      step: '3',
                      title: 'Review Outputs',
                      desc: 'Agent generates emails, proposals, plans & briefs',
                    },
                    {
                      step: '4',
                      title: 'Memory Builds',
                      desc: 'Context persists — run events in sequence to see it evolve',
                    },
                  ].map((item) => (
                    <div key={item.step} className="flex gap-3">
                      <div
                        className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
                        style={{ backgroundColor: 'rgba(99,102,241,0.2)', color: '#818cf8' }}
                      >
                        {item.step}
                      </div>
                      <div>
                        <div className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>
                          {item.title}
                        </div>
                        <div className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                          {item.desc}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
