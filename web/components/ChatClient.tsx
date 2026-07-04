'use client';

import { useMemo, useState } from 'react';
import { useChat } from '@ai-sdk/react';
import { TextStreamChatTransport } from 'ai';
import { Send } from 'lucide-react';

function partText(message: { content?: string; parts?: Array<{ type?: string; text?: string }> }) {
  if (message.parts?.length) {
    return message.parts.map((part) => part.text || '').join('');
  }
  return message.content || '';
}

export function ChatClient() {
  const [input, setInput] = useState('');
  const [role, setRole] = useState('APP_ANALYST');
  const transport = useMemo(() => new TextStreamChatTransport({ api: '/api/chat' }), []);
  const { messages, sendMessage, status } = useChat({ transport });

  const examples = [
    'Which suppliers have the highest blocked invoice amount?',
    'Which business unit has the slowest approval cycle?',
    'When is three-way matching required?',
    'Draft an internal escalation note for the top blocked invoice.',
    'Run this SQL: select * from RAW_ORACLE_SUPPLIERS.',
  ];

  return (
    <div className="chat-layout">
      <section>
        <div className="card messages" aria-live="polite">
          {messages.length === 0 ? (
            <div className="message assistant">Ask a governed enterprise systems question to start.</div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`message ${message.role === 'user' ? 'user' : 'assistant'}`}>
                {partText(message)}
              </div>
            ))
          )}
        </div>
        <form
          className="composer"
          onSubmit={(event) => {
            event.preventDefault();
            if (!input.trim()) return;
            sendMessage({ text: input }, { body: { role, user_id: role === 'APP_MANAGER' ? 'demo_manager' : 'demo_analyst' } });
            setInput('');
          }}
        >
          <input
            value={input}
            placeholder="Ask about suppliers, invoices, approvals, policies, or drafts"
            onChange={(event) => setInput(event.currentTarget.value)}
          />
          <button className="button" type="submit" disabled={status === 'streaming'}>
            <Send size={16} />
            Send
          </button>
        </form>
      </section>
      <aside className="grid">
        <div className="card">
          <label htmlFor="role">Role simulation</label>
          <select id="role" className="field" value={role} onChange={(event) => setRole(event.currentTarget.value)}>
            <option>APP_ANALYST</option>
            <option>APP_MANAGER</option>
            <option>APP_ADMIN</option>
            <option>APP_AUDITOR</option>
          </select>
        </div>
        <div className="card">
          <strong>Example prompts</strong>
          <div className="grid" style={{ marginTop: 12 }}>
            {examples.map((example) => (
              <button key={example} className="button secondary" type="button" onClick={() => setInput(example)}>
                {example}
              </button>
            ))}
          </div>
        </div>
        <div className="card">
          <span className="status good">Mock-first</span>
          <p>Chat streams through Vercel AI SDK to the Next.js route, then calls the governed FastAPI backend.</p>
        </div>
      </aside>
    </div>
  );
}
