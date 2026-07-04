import { DataTable } from '@/components/DataTable';
import { apiGet, formatMoney } from '@/lib/api';

type ExceptionRow = {
  open_amount: number;
  exception_type: string;
};

export default async function ExceptionsPage() {
  const rows = await safeGet<ExceptionRow[]>('/dashboards/invoice-exceptions', []);
  const blockedAmount = rows.reduce((sum, row) => sum + Number(row.open_amount || 0), 0);
  const noReceipt = rows.filter((row) => row.exception_type === 'NO_RECEIPT').length;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Invoice Exception Queue</h1>
          <p>Blocked invoices sorted by exposure and age.</p>
        </div>
      </header>
      <section className="grid cols-3">
        <div className="card metric">
          <span className="label">Blocked invoices</span>
          <div className="value">{rows.length}</div>
        </div>
        <div className="card metric">
          <span className="label">Blocked amount</span>
          <div className="value">{formatMoney(blockedAmount)}</div>
        </div>
        <div className="card metric">
          <span className="label">No receipt exceptions</span>
          <div className="value">{noReceipt}</div>
        </div>
      </section>
      <section style={{ marginTop: 16 }}>
        <DataTable rows={rows as unknown as Record<string, unknown>[]} />
      </section>
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
