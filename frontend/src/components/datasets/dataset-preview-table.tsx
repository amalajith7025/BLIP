import type { PreviewRow } from "@/components/datasets/types"

type DatasetPreviewTableProps = {
  rows: PreviewRow[]
}

export function DatasetPreviewTable({ rows }: DatasetPreviewTableProps) {
  return (
    <section className="rounded-xl border border-border bg-card">
      <div className="border-b border-border px-5 py-4">
        <h3 className="text-base font-semibold">Dataset Preview</h3>
        <p className="mt-1 text-sm text-muted-foreground">Showing the first few rows.</p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-[760px] w-full text-sm">
          <thead className="bg-muted/50 text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Region</th>
              <th className="px-4 py-3 font-medium">Account</th>
              <th className="px-4 py-3 font-medium">Product Line</th>
              <th className="px-4 py-3 font-medium">Units</th>
              <th className="px-4 py-3 font-medium">Revenue</th>
              <th className="px-4 py-3 font-medium">Margin</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.date}-${row.account}`} className="border-t border-border">
                <td className="px-4 py-3">{row.date}</td>
                <td className="px-4 py-3">{row.region}</td>
                <td className="px-4 py-3">{row.account}</td>
                <td className="px-4 py-3">{row.productLine}</td>
                <td className="px-4 py-3">{row.units}</td>
                <td className="px-4 py-3">{row.revenue}</td>
                <td className="px-4 py-3">{row.margin}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
