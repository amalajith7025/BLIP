import { CalendarDays, Columns3, Rows3, Table2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import type { DatasetRecord } from "@/components/datasets/types"

type DatasetCardProps = {
  dataset: DatasetRecord
  onPreview: () => void
}

export function DatasetCard({ dataset, onPreview }: DatasetCardProps) {
  return (
    <article className="rounded-xl border border-border bg-card p-5 shadow-xs">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">{dataset.name}</h2>
          <p className="mt-1 inline-flex items-center rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-400">
            Status: {dataset.status}
          </p>
        </div>
        <Button variant="outline" onClick={onPreview}>
          Preview
        </Button>
      </div>

      <dl className="mt-5 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg bg-muted/40 p-3">
          <dt className="flex items-center gap-2 text-muted-foreground">
            <Rows3 className="size-4" />
            Rows
          </dt>
          <dd className="mt-1 font-medium">{dataset.rows.toLocaleString()}</dd>
        </div>
        <div className="rounded-lg bg-muted/40 p-3">
          <dt className="flex items-center gap-2 text-muted-foreground">
            <Columns3 className="size-4" />
            Columns
          </dt>
          <dd className="mt-1 font-medium">{dataset.columns}</dd>
        </div>
        <div className="rounded-lg bg-muted/40 p-3">
          <dt className="flex items-center gap-2 text-muted-foreground">
            <CalendarDays className="size-4" />
            Upload Date
          </dt>
          <dd className="mt-1 font-medium">{dataset.uploadDate}</dd>
        </div>
        <div className="rounded-lg bg-muted/40 p-3">
          <dt className="flex items-center gap-2 text-muted-foreground">
            <Table2 className="size-4" />
            Dataset Name
          </dt>
          <dd className="mt-1 truncate font-medium" title={dataset.name}>
            {dataset.name}
          </dd>
        </div>
      </dl>
    </article>
  )
}
