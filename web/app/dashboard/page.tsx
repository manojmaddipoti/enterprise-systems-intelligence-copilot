import { Activity, AlertTriangle, BadgeDollarSign, Clock, FileWarning, ReceiptText } from 'lucide-react';
import { DataTable } from '@/components/DataTable';
import { apiGet, formatMoney } from '@/lib/api';

type WorkflowRow = {
  business_unit: string;
  period: string;
  total_pos: number;
  total_invoices: number;
  exception_rate: number;
  match_rate: number;
  avg_approval_cycle_days: number;
  blocked_invoice_amount: number;
  open_invoice_amount: number;
  workflow_health_score: number;
};

type ExceptionRow = {
  supplier_name: string;
  open_amount: number;
  exception_type: string;
};

type BottleneckRow = {
  business_unit: string;
  approver_role: string;
  approver_name: string;
  avg_cycle_time_hours: number;
  overdue_count: number;
  total_amount_pending: number;
};

export default async function DashboardPage() {
  const [rows, exceptions, bottlenecks] = await Promise.all([
    safeGet<WorkflowRow[]>('/dashboards/workflow-health', []),
    safeGet<ExceptionRow[]>('/dashboards/invoice-exceptions', []),
    safeGet<BottleneckRow[]>('/dashboards/approval-bottlenecks', []),
  ]);
  const latest = rows[0];
  const avgHealth = rows.length
    ? rows.reduce((sum, row) => sum + Number(row.workflow_health_score || 0), 0) / rows.length
    : 0;
  const totals = rows.reduce(
    (acc, row) => ({
      totalPos: acc.totalPos + Number(row.total_pos || 0),
      totalInvoices: acc.totalInvoices + Number(row.total_invoices || 0),
      blockedAmount: acc.blockedAmount + Number(row.blocked_invoice_amount || 0),
      openAmount: acc.openAmount + Number(row.open_invoice_amount || 0),
      matchRate: acc.matchRate + Number(row.match_rate || 0),
      approvalDays: acc.approvalDays + Number(row.avg_approval_cycle_days || 0),
    }),
    { totalPos: 0, totalInvoices: 0, blockedAmount: 0, openAmount: 0, matchRate: 0, approvalDays: 0 },
  );
  const avgMatchRate = rows.length ? (totals.matchRate / rows.length) * 100 : 0;
  const avgApprovalDays = rows.length ? totals.approvalDays / rows.length : 0;
  const topBlocked = [...exceptions]
    .sort((a, b) => Number(b.open_amount || 0) - Number(a.open_amount || 0))
    .slice(0, 5);

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
          <div className="value">{formatMoney(totals.blockedAmount || latest?.blocked_invoice_amount)}</div>
          <span className="status warn">
            <AlertTriangle size={14} /> open exposure
          </span>
        </div>
        <div className="card metric">
          <span className="label">Open invoice amount</span>
          <div className="value">{formatMoney(totals.openAmount || latest?.open_invoice_amount)}</div>
          <span className="status">
            <BadgeDollarSign size={14} /> governed mart
          </span>
        </div>
        <div className="card metric">
          <span className="label">Purchase orders</span>
          <div className="value">{totals.totalPos.toLocaleString()}</div>
          <span className="status">
            <ReceiptText size={14} /> workflow volume
          </span>
        </div>
        <div className="card metric">
          <span className="label">Invoices</span>
          <div className="value">{totals.totalInvoices.toLocaleString()}</div>
          <span className="status">
            <FileWarning size={14} /> exception count {exceptions.length}
          </span>
        </div>
        <div className="card metric">
          <span className="label">Match rate / approval cycle</span>
          <div className="value">{avgMatchRate.toFixed(1)}%</div>
          <span className="status">
            <Clock size={14} /> {avgApprovalDays.toFixed(1)} days avg approval
          </span>
        </div>
      </section>

      <section className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h2>Workflow Health by Business Unit</h2>
          <div className="bar-list">
            {rows.slice(0, 8).map((row) => (
              <div key={`${row.business_unit}-${row.period}`} className="bar-row">
                <span>{row.business_unit}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${Math.max(4, Number(row.workflow_health_score || 0))}%` }} />
                </div>
                <strong>{Number(row.workflow_health_score || 0).toFixed(1)}</strong>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h2>Top Blocked Suppliers</h2>
          <DataTable rows={topBlocked as unknown as Record<string, unknown>[]} />
        </div>
      </section>

      <section className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h2>Top Approval Bottlenecks</h2>
          <DataTable rows={bottlenecks as unknown as Record<string, unknown>[]} />
        </div>
        <div className="card">
          <h2>Workflow Health Detail</h2>
          <DataTable rows={rows as unknown as Record<string, unknown>[]} />
        </div>
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
