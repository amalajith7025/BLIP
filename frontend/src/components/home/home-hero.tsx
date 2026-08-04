import { Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function HomeHero() {
  return (
    <section className="rounded-2xl border border-border bg-card p-5 lg:p-6">
      <p className="text-sm font-medium text-muted-foreground">Good morning, Jordan</p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight text-foreground lg:text-4xl">
        What would you like to investigate today?
      </h1>

      <div className="mt-5 flex flex-col gap-3 lg:flex-row lg:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input className="h-11 pl-9" placeholder="Search investigations, reports, data..." />
        </div>
        <Button className="h-11 px-5">Start New Investigation</Button>
      </div>
    </section>
  )
}
