import { DatabaseZap } from "lucide-react"

import { Button } from "@/components/ui/button"

type DataEmptyStateProps = {
  onAddData: () => void
}

export function DataEmptyState({ onAddData }: DataEmptyStateProps) {
  return (
    <section className="rounded-2xl border border-dashed border-border bg-card p-10 text-center sm:p-14">
      <div className="mx-auto mb-5 flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        <DatabaseZap className="size-5" />
      </div>
      <h2 className="text-xl font-semibold tracking-tight">No data has been added yet.</h2>
      <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
        Add your first dataset to begin your investigation.
      </p>
      <div className="mt-6">
        <Button onClick={onAddData}>Add Data</Button>
      </div>
    </section>
  )
}
