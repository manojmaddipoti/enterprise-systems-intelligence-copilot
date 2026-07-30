import { DraftActionsTable } from '@/components/DraftActionsTable';
import { apiGet } from '@/lib/api';

export default async function DraftsPage() {
  const rows = await safeGet<Record<string, unknown>[]>('/drafts', []);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Draft Actions</h1>
          <p>Internal draft actions stay pending until approved by manager or admin roles.</p>
        </div>
      </header>
      <DraftActionsTable rows={rows} />
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
