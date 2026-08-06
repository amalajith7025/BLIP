import { Link2 } from "lucide-react"

import { cn } from "@/lib/utils"

type MappingChoice = "date" | "region" | "account" | "product" | "value" | "not-used"

type ConnectionRow = {
  id: string
  sourceField: string
  suggestedMatch: string
  confidence: number
  choice: MappingChoice
}

type ConnectionMappingTableProps = {
  rows: ConnectionRow[]
  onChoiceChange: (id: string, value: MappingChoice) => void
}

const choices: Array<{ value: MappingChoice; label: string }> = [
  { value: "date", label: "Date" },
  { value: "region", label: "Region" },
  { value: "account", label: "Account" },
  { value: "product", label: "Product" },
  { value: "value", label: "Value" },
  { value: "not-used", label: "Not Used" },
]

export function ConnectionMappingTable({ rows, onChoiceChange }: ConnectionMappingTableProps) {
  return (
    <section className="rounded-xl border border-border bg-card">
      <div className="border-b border-border px-5 py-4">
        <h3 className="text-base font-semibold">Connecting Information</h3>
        <p className="mt-1 text-sm text-muted-foreground">Confirm suggested matches or adjust them.</p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-[720px] w-full text-sm">
          <thead className="bg-muted/50 text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Source Field</th>
              <th className="px-4 py-3 font-medium">Suggested Match</th>
              <th className="px-4 py-3 font-medium">Confidence</th>
              <th className="px-4 py-3 font-medium">Override</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-t border-border align-middle">
                <td className="px-4 py-3 font-medium">{row.sourceField}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-2 rounded-md bg-muted px-2.5 py-1">
                    <Link2 className="size-3.5 text-muted-foreground" />
                    {row.suggestedMatch}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 overflow-hidden rounded-full bg-muted">
                      <div
                        className={cn(
                          "h-full rounded-full",
                          row.confidence >= 85 ? "bg-emerald-500" : "bg-amber-500"
                        )}
                        style={{ width: `${row.confidence}%` }}
                        aria-hidden="true"
                      />
                    </div>
                    <span className="text-xs text-muted-foreground">{row.confidence}%</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <select
                    value={row.choice}
                    onChange={(event) => onChoiceChange(row.id, event.target.value as MappingChoice)}
                    className="h-9 rounded-md border border-input bg-background px-2.5 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    {choices.map((choice) => (
                      <option key={choice.value} value={choice.value}>
                        {choice.label}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

export type { ConnectionRow, MappingChoice }
