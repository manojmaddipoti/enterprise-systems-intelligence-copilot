export function DataTable({ rows }: { rows: Record<string, unknown>[] }) {
  if (!rows.length) {
    return <div className="card">No records found.</div>;
  }

  const columns = Object.keys(rows[0]).slice(0, 10);

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td key={column}>{String(row[column] ?? '')}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
