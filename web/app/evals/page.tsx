import { DataTable } from '@/components/DataTable';
import { apiGet } from '@/lib/api';

export default async function EvalsPage() {
  const rows = await safeGet<Record<string, unknown>[]>('/evals/results', []);
  const passed = rows.filter((row) => row.passed === true).length;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Eval Results</h1>
          <p>Local scorecard for routing, security, policy grounding, and answer checks.</p>
        </div>
        <span className="status good">{rows.length ? `${passed}/${rows.length} passed` : 'No runs yet'}</span>
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
