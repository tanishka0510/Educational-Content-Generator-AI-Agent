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
    <div className="mt-5 overflow-hidden rounded-xl border border-[#C59B27]/25 bg-[#0B1220]">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-white/10 bg-[#0E1A30]">
              {table.columns.map((column, index) => (
                <th
                  key={index}
                  className="px-4 py-3 text-left font-serif font-semibold text-[#E5C365] tracking-wide"
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
                className="border-b border-white/5 last:border-b-0 hover:bg-white/[0.02] transition"
              >
                {row.map((value, columnIndex) => (
                  <td
                    key={columnIndex}
                    className="px-4 py-3 align-top leading-6 text-slate-300"
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