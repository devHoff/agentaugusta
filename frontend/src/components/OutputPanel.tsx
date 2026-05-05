'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check, ChevronDown, ChevronUp, Mail, FileText, CheckSquare, Brain, Search } from 'lucide-react';

interface OutputItem {
  type: string;
  title: string;
  content: string;
}

interface OutputPanelProps {
  output: OutputItem;
  defaultOpen?: boolean;
}

const TYPE_CONFIG: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
  email: {
    icon: <Mail size={16} />,
    color: '#60a5fa',
    bg: 'rgba(59, 130, 246, 0.1)',
  },
  proposal: {
    icon: <FileText size={16} />,
    color: '#a78bfa',
    bg: 'rgba(139, 92, 246, 0.1)',
  },
  team_plan: {
    icon: <CheckSquare size={16} />,
    color: '#34d399',
    bg: 'rgba(16, 185, 129, 0.1)',
  },
  meeting_prep: {
    icon: <Brain size={16} />,
    color: '#fbbf24',
    bg: 'rgba(245, 158, 11, 0.1)',
  },
  research_report: {
    icon: <Search size={16} />,
    color: '#f472b6',
    bg: 'rgba(236, 72, 153, 0.1)',
  },
};

export default function OutputPanel({ output, defaultOpen = true }: OutputPanelProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [copied, setCopied] = useState(false);

  const config = TYPE_CONFIG[output.type] || TYPE_CONFIG.email;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(output.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className="rounded-xl border overflow-hidden animate-fadeIn"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border)',
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer select-none"
        style={{ backgroundColor: config.bg, borderBottom: isOpen ? `1px solid var(--border)` : 'none' }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <span style={{ color: config.color }}>{config.icon}</span>
          <span className="font-semibold text-sm" style={{ color: config.color }}>
            {output.title}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isOpen && (
            <button
              onClick={(e) => { e.stopPropagation(); handleCopy(); }}
              className="flex items-center gap-1 text-xs px-2 py-1 rounded-md transition-all"
              style={{
                backgroundColor: 'rgba(255,255,255,0.08)',
                color: 'var(--text-secondary)',
              }}
              title="Copy to clipboard"
            >
              {copied ? <Check size={12} style={{ color: '#34d399' }} /> : <Copy size={12} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          )}
          <span style={{ color: 'var(--text-secondary)' }}>
            {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </span>
        </div>
      </div>

      {/* Content */}
      {isOpen && (
        <div className="p-5 overflow-x-auto" style={{ maxHeight: '600px', overflowY: 'auto' }}>
          <div className="prose-dark">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {output.content}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
