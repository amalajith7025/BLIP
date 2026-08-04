import { Pin } from "lucide-react"

import type { PinnedItem } from "@/components/home/home-data"

type PinnedItemsSectionProps = {
  items: PinnedItem[]
}

export function PinnedItemsSection({ items }: PinnedItemsSectionProps) {
  return (
    <section className="rounded-xl border border-border bg-card p-4">
      <h3 className="text-sm font-semibold tracking-wide text-muted-foreground">Pinned</h3>
      <div className="mt-3 grid gap-3 sm:grid-cols-3">
        {items.map((item) => (
          <article key={item.id} className="rounded-lg border border-border bg-background p-3">
            <div className="mb-2 inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-1 text-xs text-primary">
              <Pin className="size-3" />
              Pinned
            </div>
            <h4 className="text-sm font-medium">{item.title}</h4>
            <p className="mt-1 text-xs text-muted-foreground">{item.subtitle}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
