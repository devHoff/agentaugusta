'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, MessageSquare } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatPanelProps {
  clientId: string;
  companyName: string;
  onSend: (messages: Message[]) => Promise<string>;
}

export default function ChatPanel({ clientId, companyName, onSend }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await onSend(newMessages);
      setMessages([...newMessages, { role: 'assistant', content: response }]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { role: 'assistant', content: `❌ Error: ${err instanceof Error ? err.message : 'Failed to get response'}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedQuestions = [
    'What are the open action items?',
    'What risks should I be aware of?',
    'Summarize the project status',
    'What should we prepare for the next meeting?',
  ];

  return (
    <div
      className="flex flex-col rounded-xl border overflow-hidden"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border)',
        height: '500px',
      }}
    >
      {/* Header */}
      <div
        className="flex items-center gap-2 px-4 py-3 border-b"
        style={{ borderColor: 'var(--border)', backgroundColor: 'rgba(99,102,241,0.08)' }}
      >
        <MessageSquare size={16} style={{ color: '#818cf8' }} />
        <span className="font-semibold text-sm" style={{ color: '#818cf8' }}>
          Chat about {companyName}
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center gap-4">
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ backgroundColor: 'rgba(99,102,241,0.15)' }}
            >
              <Bot size={24} style={{ color: '#818cf8' }} />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                Ask me anything about {companyName}
              </p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                I have full context of this engagement
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 w-full max-w-sm">
              {suggestedQuestions.map((q) => (
                <button
                  key={q}
                  onClick={() => setInput(q)}
                  className="text-left text-xs p-2.5 rounded-lg border transition-all"
                  style={{
                    backgroundColor: 'rgba(99,102,241,0.08)',
                    borderColor: 'rgba(99,102,241,0.2)',
                    color: 'var(--text-secondary)',
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5"
                style={{
                  backgroundColor:
                    msg.role === 'user' ? 'rgba(99,102,241,0.3)' : 'rgba(16,185,129,0.2)',
                }}
              >
                {msg.role === 'user' ? (
                  <User size={13} style={{ color: '#818cf8' }} />
                ) : (
                  <Bot size={13} style={{ color: '#34d399' }} />
                )}
              </div>
              <div
                className="max-w-[80%] rounded-xl px-3.5 py-2.5 text-sm"
                style={{
                  backgroundColor:
                    msg.role === 'user'
                      ? 'rgba(99,102,241,0.18)'
                      : 'rgba(255,255,255,0.05)',
                  borderRadius: msg.role === 'user' ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
                }}
              >
                {msg.role === 'assistant' ? (
                  <div className="prose-dark text-sm">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  <span style={{ color: 'var(--text-primary)' }}>{msg.content}</span>
                )}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex gap-2.5">
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center"
              style={{ backgroundColor: 'rgba(16,185,129,0.2)' }}
            >
              <Bot size={13} style={{ color: '#34d399' }} />
            </div>
            <div
              className="rounded-xl px-3.5 py-3"
              style={{ backgroundColor: 'rgba(255,255,255,0.05)' }}
            >
              <Loader2 size={16} className="animate-spin" style={{ color: '#34d399' }} />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div
        className="p-3 border-t flex gap-2 items-end"
        style={{ borderColor: 'var(--border)' }}
      >
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about this engagement... (Enter to send)"
          rows={1}
          className="flex-1 resize-none rounded-lg px-3 py-2.5 text-sm outline-none transition-all"
          style={{
            backgroundColor: 'rgba(255,255,255,0.06)',
            border: '1px solid var(--border)',
            color: 'var(--text-primary)',
            maxHeight: '100px',
          }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = 'auto';
            target.style.height = `${Math.min(target.scrollHeight, 100)}px`;
          }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="p-2.5 rounded-lg transition-all"
          style={{
            backgroundColor:
              !input.trim() || loading ? 'rgba(99,102,241,0.2)' : 'rgba(99,102,241,0.8)',
            color: !input.trim() || loading ? 'rgba(129,140,248,0.5)' : '#fff',
            cursor: !input.trim() || loading ? 'not-allowed' : 'pointer',
          }}
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
