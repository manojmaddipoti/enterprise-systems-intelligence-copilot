import { Activity, AlertTriangle, BadgeDollarSign } from 'lucide-react';
import { DataTable } from '@/components/DataTable';
import { apiGet, formatMoney } from '@/lib/api';

type WorkflowRow = {
  business_unit: string;
  period: string;
  total_pos: number;
  total_invoices: number;
  exception_rate: number;
  match_rate: number;
  blocked_invoice_amount: number;
  open_invoice_amount: number;
  workflow_health_score: number;
};

export default async function DashboardPage() {
  const rows = await safeGet<WorkflowRow[]>('/dashboards/workflow-health', []);
  const latest = rows[0];
  const avgHealth = rows.length
    ? rows.reduce((sum, row) => sum + Number(row.workflow_health_score || 0), 0) / rows.length
    : 0;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Workflow Health</h1>
          <p>Business-unit level procurement, invoice, and approval health.</p>
        </div>
      </header>
      <section className="grid cols-3">
        <div className="card metric">
          <span className="label">Average workflow health</span>
          <div className="value">{avgHealth.toFixed(1)}</div>
          <span className="status good">
            <Activity size={14} /> score
          </span>
        </div>
        <div className="card metric">
          <span className="label">Blocked invoice amount</span>
          <div className="value">{formatMoney(latest?.blocked_invoice_amount)}</div>
          <span className="status warn">
            <AlertTriangle size={14} /> current period
          </span>
        </div>
        <div className="card metric">
          <span className="label">Open invoice amount</span>
          <div className="value">{formatMoney(latest?.open_invoice_amount)}</div>
          <span className="status">
            <BadgeDollarSign size={14} /> governed mart
          </span>
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
