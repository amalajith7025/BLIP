import { Clock3 } from "lucide-react"

import type { RecentInvestigation } from "@/components/home/home-data"

type RecentInvestigationsSectionProps = {
  items: RecentInvestigation[]
}

export function RecentInvestigationsSection({ items }: RecentInvestigationsSectionProps) {
  return (
    <section className="rounded-xl border border-border bg-card p-4">
      <h3 className="text-sm font-semibold tracking-wide text-muted-foreground">Recent Investigations</h3>
      <div className="mt-2 divide-y divide-border">
        {items.map((item) => (
          <article key={item.id} className="flex items-center justify-between gap-3 py-3">
            <div>
              <h4 className="text-sm font-medium">{item.title}</h4>
              <p className="mt-0.5 text-xs text-muted-foreground">{item.status}</p>
            </div>
            <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
              <Clock3 className="size-3.5" />
              {item.updatedAt}
            </span>
          </article>
        ))}
      </div>
    </section>
  )
}
