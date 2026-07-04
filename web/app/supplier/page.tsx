import { DataTable } from '@/components/DataTable';
import { apiGet, formatMoney } from '@/lib/api';

type Supplier = Record<string, unknown>;

export default async function SupplierPage() {
  const supplier = await safeGet<Supplier>('/dashboards/supplier-360/ENT-SUP-0001', {});

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Supplier 360</h1>
          <p>Cross-system supplier spend, invoice exposure, exceptions, and risk score.</p>
        </div>
      </header>
      <section className="grid cols-3">
        <div className="card metric">
          <span className="label">Supplier</span>
          <div className="value" style={{ fontSize: 20 }}>
            {String(supplier.supplier_name || 'ENT-SUP-0001')}
          </div>
        </div>
        <div className="card metric">
          <span className="label">Open invoice amount</span>
          <div className="value">{formatMoney(supplier.open_invoice_amount)}</div>
        </div>
        <div className="card metric">
          <span className="label">Risk score</span>
          <div className="value">{String(supplier.risk_score ?? '0')}</div>
        </div>
      </section>
      <section style={{ marginTop: 16 }}>
        <DataTable rows={[supplier]} />
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
