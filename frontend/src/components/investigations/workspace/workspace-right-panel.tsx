import { CircleGauge, CircleHelp, Database, Filter, Goal, Layers3, LineChart, UsersRound } from "lucide-react"

import type { WorkspaceState } from "@/components/investigations/workspace/types"

type WorkspaceRightPanelProps = {
  state: WorkspaceState
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl bg-muted/30 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-medium">{value}</p>
    </div>
  )
}

export function WorkspaceRightPanel({ state }: WorkspaceRightPanelProps) {
  return (
    <aside className="sticky top-20 space-y-4">
      <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
        <h2 className="text-sm font-medium text-muted-foreground">Current Investigation Context</h2>

        <div className="mt-4 space-y-3 text-sm">
          <p><span className="font-medium">Question:</span> {state.question}</p>
          <p className="inline-flex items-center gap-2"><Goal className="size-4 text-muted-foreground" />Goal: {state.goal}</p>
          <p className="inline-flex items-center gap-2"><UsersRound className="size-4 text-muted-foreground" />Audience: {state.audience}</p>
          <p className="inline-flex items-center gap-2"><Database className="size-4 text-muted-foreground" />Uploaded Datasets: {state.datasets.length}</p>
        </div>
      </section>

      <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
        <h3 className="text-sm font-medium text-muted-foreground">Information Signals</h3>
        <div className="mt-3 grid grid-cols-2 gap-2">
          <StatCard label="Data Health Score" value={`${state.healthScore}%`} />
          <StatCard label="Question Confidence" value={`${state.questionConfidence}%`} />
        </div>

        <div className="mt-4 space-y-3 text-sm text-muted-foreground">
          <p className="inline-flex items-start gap-2"><Layers3 className="mt-0.5 size-4" />Detected Business Dimensions: {state.dimensions.join(", ")}</p>
          <p className="inline-flex items-start gap-2"><CircleGauge className="mt-0.5 size-4" />Detected Measures: {state.measures.join(", ")}</p>
          <p className="inline-flex items-start gap-2"><Filter className="mt-0.5 size-4" />Applied Filters: {state.filters.join(" • ")}</p>
          <p className="inline-flex items-start gap-2"><LineChart className="mt-0.5 size-4" />Current Visualization: {state.currentVisualization}</p>
          <p className="inline-flex items-start gap-2"><CircleHelp className="mt-0.5 size-4" />Future Support Status: {state.futureSupportStatus}</p>
        </div>
      </section>
    </aside>
  )
}
