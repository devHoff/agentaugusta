'use client';

import React from 'react';
import { FileText, Mail, Clock, Loader2 } from 'lucide-react';

interface EventButtonsProps {
  onTranscript: () => void;
  onEmail: () => void;
  onMeeting: () => void;
  loading: boolean;
  activeEvent: string | null;
  hasClient: boolean;
  hasTranscript: boolean;
  hasEmail: boolean;
}

export default function EventButtons({
  onTranscript,
  onEmail,
  onMeeting,
  loading,
  activeEvent,
  hasClient,
  hasTranscript,
  hasEmail,
}: EventButtonsProps) {
  const buttons = [
    {
      id: 'transcript',
      label: 'Meeting Transcript',
      sublabel: 'came in',
      icon: <FileText size={22} />,
      onClick: onTranscript,
      disabled: !hasClient || !hasTranscript,
      color: '#60a5fa',
      bg: 'rgba(59,130,246,0.12)',
      border: 'rgba(59,130,246,0.3)',
      activeBg: 'rgba(59,130,246,0.25)',
      disabledReason: !hasClient ? 'Select a client first' : !hasTranscript ? 'No transcripts available' : '',
    },
    {
      id: 'email',
      label: 'Email Reply',
      sublabel: 'came in',
      icon: <Mail size={22} />,
      onClick: onEmail,
      disabled: !hasClient || !hasEmail,
      color: '#a78bfa',
      bg: 'rgba(139,92,246,0.12)',
      border: 'rgba(139,92,246,0.3)',
      activeBg: 'rgba(139,92,246,0.25)',
      disabledReason: !hasClient ? 'Select a client first' : !hasEmail ? 'No email available' : '',
    },
    {
      id: 'meeting',
      label: 'Meeting',
      sublabel: 'in 3 hours',
      icon: <Clock size={22} />,
      onClick: onMeeting,
      disabled: !hasClient,
      color: '#fbbf24',
      bg: 'rgba(245,158,11,0.12)',
      border: 'rgba(245,158,11,0.3)',
      activeBg: 'rgba(245,158,11,0.25)',
      disabledReason: !hasClient ? 'Select a client first' : '',
    },
  ];

  return (
    <div className="grid grid-cols-3 gap-3">
      {buttons.map((btn) => {
        const isActive = activeEvent === btn.id;
        const isLoading = loading && isActive;

        return (
          <button
            key={btn.id}
            onClick={btn.onClick}
            disabled={btn.disabled || loading}
            title={btn.disabledReason}
            className="relative flex flex-col items-center justify-center gap-2 py-5 px-3 rounded-xl border transition-all font-medium"
            style={{
              backgroundColor: isActive ? btn.activeBg : btn.disabled ? 'rgba(255,255,255,0.03)' : btn.bg,
              borderColor: isActive ? btn.border : btn.disabled ? 'rgba(255,255,255,0.08)' : btn.border,
              color: btn.disabled ? 'rgba(156,163,192,0.4)' : btn.color,
              cursor: btn.disabled || loading ? 'not-allowed' : 'pointer',
              opacity: btn.disabled ? 0.5 : 1,
              boxShadow: isActive ? `0 0 20px ${btn.border}` : 'none',
              transform: isActive ? 'scale(1.02)' : 'scale(1)',
            }}
          >
            {isLoading ? (
              <Loader2 size={22} className="animate-spin" style={{ color: btn.color }} />
            ) : (
              <span style={{ color: btn.disabled ? 'rgba(156,163,192,0.3)' : btn.color }}>
                {btn.icon}
              </span>
            )}
            <div className="text-center">
              <div className="text-xs font-semibold leading-tight">{btn.label}</div>
              <div className="text-xs opacity-70 leading-tight">{btn.sublabel}</div>
            </div>
          </button>
        );
      })}
    </div>
  );
}
