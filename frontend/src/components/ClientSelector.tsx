'use client';

import React from 'react';
import { Building2, User, Tag, RefreshCw, Trash2 } from 'lucide-react';

interface ClientInfo {
  client_id: string;
  client_name: string;
  company_name: string;
  industry: string;
  transcripts: { id: string; title: string; date: string }[];
  email: { subject: string; from_name: string } | null;
  memory: Record<string, unknown> | null;
}

interface ClientSelectorProps {
  clients: ClientInfo[];
  selectedClient: ClientInfo | null;
  selectedTranscriptId: string | null;
  onSelectClient: (client: ClientInfo) => void;
  onSelectTranscript: (id: string) => void;
  onResetMemory: (clientId?: string) => void;
  loading: boolean;
}

export default function ClientSelector({
  clients,
  selectedClient,
  selectedTranscriptId,
  onSelectClient,
  onSelectTranscript,
  onResetMemory,
  loading,
}: ClientSelectorProps) {
  return (
    <div className="space-y-4">
      {/* Client Cards */}
      <div className="grid grid-cols-1 gap-3">
        {clients.map((client) => {
          const isSelected = selectedClient?.client_id === client.client_id;
          const hasMemory = !!client.memory;

          return (
            <div
              key={client.client_id}
              className="rounded-xl border cursor-pointer transition-all"
              style={{
                backgroundColor: isSelected ? 'rgba(99,102,241,0.12)' : 'var(--bg-card)',
                borderColor: isSelected ? 'rgba(99,102,241,0.5)' : 'var(--border)',
                boxShadow: isSelected ? '0 0 0 1px rgba(99,102,241,0.3)' : 'none',
              }}
              onClick={() => !loading && onSelectClient(client)}
            >
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm"
                      style={{
                        backgroundColor: isSelected
                          ? 'rgba(99,102,241,0.3)'
                          : 'rgba(255,255,255,0.07)',
                        color: isSelected ? '#818cf8' : 'var(--text-secondary)',
                      }}
                    >
                      {client.company_name.charAt(0)}
                    </div>
                    <div>
                      <div className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                        {client.company_name}
                      </div>
                      <div className="text-xs flex items-center gap-1 mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                        <User size={10} />
                        {client.client_name}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {hasMemory && (
                      <span
                        className="text-xs px-2 py-0.5 rounded-full"
                        style={{
                          backgroundColor: 'rgba(16,185,129,0.15)',
                          color: '#34d399',
                          border: '1px solid rgba(16,185,129,0.3)',
                        }}
                      >
                        Memory
                      </span>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onResetMemory(client.client_id);
                      }}
                      className="p-1.5 rounded-md opacity-50 hover:opacity-100 transition-opacity"
                      style={{ backgroundColor: 'rgba(239,68,68,0.1)', color: '#f87171' }}
                      title="Clear client memory"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-1 mt-2">
                  <Tag size={10} style={{ color: 'var(--text-secondary)' }} />
                  <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                    {client.industry}
                  </span>
                </div>
              </div>

              {/* Transcripts List (shown when selected) */}
              {isSelected && client.transcripts.length > 0 && (
                <div
                  className="border-t px-4 py-3"
                  style={{ borderColor: 'var(--border)' }}
                >
                  <div className="text-xs font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
                    Select Transcript
                  </div>
                  <div className="space-y-1.5">
                    {client.transcripts.map((t) => {
                      const isSel = selectedTranscriptId === t.id;
                      return (
                        <div
                          key={t.id}
                          className="flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all text-xs"
                          style={{
                            backgroundColor: isSel
                              ? 'rgba(99,102,241,0.2)'
                              : 'rgba(255,255,255,0.04)',
                            borderLeft: isSel ? '2px solid #6366f1' : '2px solid transparent',
                            color: isSel ? '#818cf8' : 'var(--text-secondary)',
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectTranscript(t.id);
                          }}
                        >
                          <span className="truncate">{t.title}</span>
                          <span className="ml-2 shrink-0" style={{ color: 'rgba(156,163,192,0.5)' }}>
                            {t.date}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Reset All */}
      <button
        onClick={() => onResetMemory()}
        className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-xs transition-all"
        style={{
          backgroundColor: 'rgba(239,68,68,0.07)',
          color: '#f87171',
          border: '1px solid rgba(239,68,68,0.2)',
        }}
      >
        <RefreshCw size={12} />
        Reset All Memory
      </button>
    </div>
  );
}
