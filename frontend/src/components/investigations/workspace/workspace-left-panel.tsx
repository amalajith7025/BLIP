import { Bookmark, BookOpenText, ChartSpline, Clock3, Lightbulb, ListChecks, NotebookPen, Table2 } from "lucide-react"

import type { WorkspaceState } from "@/components/investigations/workspace/types"

type WorkspaceLeftPanelProps = {
  state: WorkspaceState
  summaryCounts: {
    conversation: number
    insights: number
    charts: number
    tables: number
    notes: number
    bookmarks: number
  }
}

export function WorkspaceLeftPanel({ state, summaryCounts }: WorkspaceLeftPanelProps) {
  return (
    <aside className="space-y-4">
      <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
        <h2 className="text-sm font-medium text-muted-foreground">Investigation</h2>
        <p className="mt-1 text-base font-semibold">{state.title}</p>
        <p className="mt-2 inline-flex rounded-full bg-emerald-500/15 px-2.5 py-1 text-xs font-medium text-emerald-300">
          {state.status}
        </p>
      </section>

      <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
        <h3 className="mb-3 text-sm font-medium text-muted-foreground">Investigation Timeline</h3>
        <ul className="space-y-2 text-sm">
          {state.timeline.slice(-4).map((entry) => (
            <li key={entry} className="inline-flex items-start gap-2 text-muted-foreground">
              <Clock3 className="mt-0.5 size-3.5 shrink-0" />
              {entry}
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
        <h3 className="mb-3 text-sm font-medium text-muted-foreground">Investigation Memory</h3>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li className="flex items-center justify-between"><span className="inline-flex items-center gap-2"><BookOpenText className="size-4" />Conversation History</span><span>{summaryCounts.conversation}</span></li>
          <li className="flex items-center justify-between"><span className="inline-flex items-center gap-2"><Lightbulb className="size-4" />Saved Insights</span><span>{summaryCounts.insights}</span></li>
          <li className="flex items-center justify-between"><span className="inline-flex items-center gap-2"><ChartSpline className="size-4" />Generated Charts</span><span>{summaryCounts.charts}</span></li>
          <li className="flex items-center justify-between"><span className="inline-flex items-center gap-2"><Table2 className="size-4" />Generated Tables</span><span>{summaryCounts.tables}</span></li>
          <li className="flex items-center justify-between"><span className="inline-flex items-center gap-2"><NotebookPen className="size-4" />Notes</span><span>{summaryCounts.notes}</span></li>
          <li className="flex items-center justify-between"><span className="inline-flex items-center gap-2"><Bookmark className="size-4" />Bookmarks</span><span>{summaryCounts.bookmarks}</span></li>
        </ul>
      </section>

      <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
        <h3 className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <ListChecks className="size-4" />
          Recent Bookmarks
        </h3>
        <ul className="space-y-2 text-sm text-muted-foreground">
          {state.bookmarks.slice(0, 4).map((bookmark) => (
            <li key={bookmark} className="truncate rounded-md bg-muted/30 px-2 py-1">{bookmark}</li>
          ))}
        </ul>
      </section>
    </aside>
  )
}
