import { ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import type { ContinueInvestigation } from "@/components/home/home-data"

type ContinueInvestigationCardProps = {
  item: ContinueInvestigation
}

export function ContinueInvestigationCard({ item }: ContinueInvestigationCardProps) {
  return (
    <section className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-muted-foreground">Continue Investigation</p>
          <h2 className="mt-2 text-lg font-semibold">{item.title}</h2>
          <p className="mt-1 text-sm text-muted-foreground">{item.context}</p>
          <p className="mt-3 text-xs text-muted-foreground">{item.updatedAt}</p>
        </div>
        <Button className="shrink-0" variant="outline">
          Continue
          <ArrowRight className="size-4" />
        </Button>
      </div>
      <p className="mt-4 text-sm text-muted-foreground">Continue where you left off. We&apos;ve kept everything ready.</p>
    </section>
  )
}
