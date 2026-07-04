import { DataTable } from '@/components/DataTable';
import { apiGet } from '@/lib/api';

export default async function AuditPage() {
  const rows = await safeGet<Record<string, unknown>[]>('/audit/events?role=APP_ADMIN', []);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Audit Log</h1>
          <p>Traceable record of chat turns, tool calls, denials, drafts, and eval activity.</p>
        </div>
      </header>
      <DataTable rows={rows} />
    </>
  );
}

async function safeGet<T>(path: string, fallback: T): Promise<T> {
  try {
    return await apiGet<T>(path);
  } catch {
    return fallback;
  }
}
