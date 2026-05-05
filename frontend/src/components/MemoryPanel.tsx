'use client';

import React, { useState } from 'react';
import { Database, ChevronDown, ChevronUp, Clock, AlertCircle, CheckCircle, Activity } from 'lucide-react';

interface MemoryData {
  client_id: string;
  client_name: string;
  company_name: string;
  project_status: string;
  last_updated: string;
  events: { type: string; summary: string; timestamp: string }[];
  open_items: { item: string; added_at: string; resolved: boolean }[];
  decisions: string[];
  extra_context?: string;
}

interface MemoryPanelProps {
  memory: MemoryData | null;
}

const STATUS_COLORS: Record<string, string> = {
  discovery: '#60a5fa',
  proposal: '#a78bfa',
  negotiation: '#fbbf24',
  active: '#34d399',
  delivered: '#6ee7b7',
};

export default function MemoryPanel({ memory }: MemoryPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!memory) {
    return (
      <div
        className="rounded-xl border p-4 flex items-center gap-3"
        style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        <Database size={16} style={{ color: 'var(--text-secondary)' }} />
        <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          No memory yet — trigger an event to build context
        </span>
      </div>
    );
  }

  const openItems = (memory.open_items || []).filter((i) => !i.resolved);
  const status = memory.project_status || 'unknown';
  const statusColor = STATUS_COLORS[status] || '#9ca3c0';

  return (
    <div
      className="rounded-xl border overflow-hidden"
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer"
        style={{ backgroundColor: 'rgba(16,185,129,0.08)' }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <Database size={15} style={{ color: '#34d399' }} />
          <span className="font-semibold text-sm" style={{ color: '#34d399' }}>
            Project Memory
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span
            className="text-xs px-2 py-0.5 rounded-full font-medium capitalize"
            style={{
              backgroundColor: `${statusColor}20`,
              color: statusColor,
              border: `1px solid ${statusColor}40`,
            }}
          >
            {status}
          </span>
          <span style={{ color: 'var(--text-secondary)' }}>
            {isOpen ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
          </span>
        </div>
      </div>

      {/* Stats bar */}
      <div
        className="grid grid-cols-3 divide-x text-center py-2"
        style={{ borderBottom: '1px solid var(--border)', borderColor: 'var(--border)' }}
      >
        {[
          { label: 'Events', value: (memory.events || []).length, icon: <Activity size={11} /> },
          { label: 'Open Items', value: openItems.length, icon: <AlertCircle size={11} /> },
          { label: 'Decisions', value: (memory.decisions || []).length, icon: <CheckCircle size={11} /> },
        ].map((stat) => (
          <div key={stat.label} className="py-1.5" style={{ borderColor: 'var(--border)' }}>
            <div className="flex items-center justify-center gap-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
              {stat.icon}
              <span>{stat.label}</span>
            </div>
            <div className="text-base font-bold mt-0.5" style={{ color: 'var(--text-primary)' }}>
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      {/* Expandable content */}
      {isOpen && (
        <div className="p-4 space-y-4 animate-fadeIn">
          {/* Recent Events */}
          {memory.events && memory.events.length > 0 && (
            <div>
              <div className="text-xs font-semibold mb-2 uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>
                Recent Events
              </div>
              <div className="space-y-1.5">
                {[...memory.events].reverse().slice(0, 5).map((event, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <span
                      className="mt-0.5 px-1.5 py-0.5 rounded text-xs shrink-0 capitalize"
                      style={{
                        backgroundColor: 'rgba(99,102,241,0.15)',
                        color: '#818cf8',
                      }}
                    >
                      {event.type}
                    </span>
                    <span style={{ color: 'var(--text-secondary)' }} className="flex-1 leading-relaxed">
                      {event.summary}
                    </span>
                    <span className="shrink-0" style={{ color: 'rgba(156,163,192,0.5)' }}>
                      {event.timestamp?.slice(0, 10)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Open Items */}
          {openItems.length > 0 && (
            <div>
              <div className="text-xs font-semibold mb-2 uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>
                Open Items
              </div>
              <div className="space-y-1.5">
                {openItems.slice(0, 8).map((item, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <AlertCircle size={11} className="mt-0.5 shrink-0" style={{ color: '#fbbf24' }} />
                    <span style={{ color: 'var(--text-primary)' }}>{item.item}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Extra Context */}
          {memory.extra_context && (
            <div>
              <div className="text-xs font-semibold mb-2 uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>
                Latest Context
              </div>
              <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {memory.extra_context}
              </p>
            </div>
          )}

          {/* Last updated */}
          <div className="flex items-center gap-1 text-xs" style={{ color: 'rgba(156,163,192,0.5)' }}>
            <Clock size={10} />
            <span>Updated {memory.last_updated?.slice(0, 16).replace('T', ' ')} UTC</span>
          </div>
        </div>
      )}
    </div>
  );
}
