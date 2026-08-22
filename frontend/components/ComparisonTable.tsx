interface ComparisonTableData {
  columns: string[];
  rows: string[][];
}

interface ComparisonTableProps {
  table: ComparisonTableData;
}

export default function ComparisonTable({
  table,
}: ComparisonTableProps) {
  if (
    !table ||
    !table.columns ||
    !table.rows ||
    table.columns.length === 0 ||
    table.rows.length === 0
  ) {
    return null;
  }

  return (
    <div className="mt-5 overflow-hidden rounded-xl border border-slate-700">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-slate-800">
              {table.columns.map((column, index) => (
                <th
                  key={index}
                  className="border-b border-slate-700 px-4 py-3 text-left font-semibold text-white"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {table.rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className="border-b border-slate-800 last:border-b-0"
              >
                {row.map((value, columnIndex) => (
                  <td
                    key={columnIndex}
                    className="px-4 py-4 align-top leading-6 text-slate-300"
                  >
                    {value}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}