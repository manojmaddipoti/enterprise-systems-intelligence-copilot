'use client';

import { useMemo, useState } from 'react';
import { Check, X } from 'lucide-react';

type DraftRow = Record<string, unknown> & {
  draft_id?: string;
  status?: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export function DraftActionsTable({ rows }: { rows: DraftRow[] }) {
  const [drafts, setDrafts] = useState(rows);
  const [busyId, setBusyId] = useState<string | null>(null);
  const columns = useMemo(() => Object.keys(drafts[0] || {}).slice(0, 8), [drafts]);

  async function decide(draftId: string, action: 'approve' | 'reject') {
    setBusyId(draftId);
    try {
      const response = await fetch(
        `${apiBaseUrl}/drafts/${draftId}/${action}?role=APP_MANAGER&user_id=demo_manager`,
        { method: 'POST' },
      );
      if (!response.ok) {
        throw new Error(`Draft ${action} failed`);
      }
      const updated = (await response.json()) as DraftRow;
      setDrafts((current) => current.map((draft) => (draft.draft_id === draftId ? updated : draft)));
    } finally {
      setBusyId(null);
    }
  }

  if (!drafts.length) {
    return <div className="card">No records found.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
            <th>actions</th>
          </tr>
        </thead>
        <tbody>
          {drafts.map((draft) => {
            const draftId = String(draft.draft_id || '');
            const isPending = draft.status === 'PENDING_APPROVAL';
            return (
              <tr key={draftId}>
                {columns.map((column) => (
                  <td key={column}>{String(draft[column] ?? '')}</td>
                ))}
                <td>
                  <div className="row-actions">
                    <button
                      className="icon-button"
                      type="button"
                      title="Approve draft"
                      disabled={!isPending || busyId === draftId}
                      onClick={() => decide(draftId, 'approve')}
                    >
                      <Check size={16} />
                    </button>
                    <button
                      className="icon-button danger"
                      type="button"
                      title="Reject draft"
                      disabled={!isPending || busyId === draftId}
                      onClick={() => decide(draftId, 'reject')}
                    >
                      <X size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
