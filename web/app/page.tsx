import { ChatClient } from '@/components/ChatClient';

export default function Page() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1>Governed Chat</h1>
          <p>Ask cross-system questions with controlled tools, citations, approvals, and audit traces.</p>
        </div>
      </header>
      <ChatClient />
    </>
  );
}
