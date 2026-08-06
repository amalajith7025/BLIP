"use client"

import { FormEvent, useState } from "react"
import { BookmarkPlus, ChartNoAxesColumn, Lightbulb, Send, Sparkles, TableProperties } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { WorkspaceState } from "@/components/investigations/workspace/types"

type WorkspaceCenterPanelProps = {
  state: WorkspaceState
  onSubmitPrompt: (prompt: string) => void
  onAddBookmark: (value: string) => void
}

const promptExamples = [
  "Why did revenue decrease?",
  "Compare Europe with APAC.",
  "What caused the increase in customer complaints?",
  "Show trends over the last six months.",
]

export function WorkspaceCenterPanel({ state, onSubmitPrompt, onAddBookmark }: WorkspaceCenterPanelProps) {
  const [prompt, setPrompt] = useState("")

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const clean = prompt.trim()
    if (!clean) return
    onSubmitPrompt(clean)
    setPrompt("")
  }

  return (
    <section className="space-y-4">
      <header className="rounded-2xl bg-card/90 p-5 shadow-sm ring-1 ring-white/5">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">Investigation Workspace</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight">{state.title}</h1>
        <p className="mt-2 text-sm text-muted-foreground">Original Business Question: {state.question}</p>
        <div className="mt-4 flex flex-wrap gap-2 text-xs text-muted-foreground">
          <span className="rounded-full bg-muted px-2.5 py-1">Current Dataset: {state.datasets[0]}</span>
          <span className="rounded-full bg-muted px-2.5 py-1">Current Filters: {state.filters.join(" • ")}</span>
        </div>
      </header>

      <div className="grid gap-4 xl:grid-cols-2">
        <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">Investigation Conversation</h2>
          <div className="space-y-3">
            {state.messages.slice(-6).map((message) => (
              <article key={message.id} className="rounded-lg bg-muted/30 p-3">
                <div className="mb-1 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{message.author}</span>
                  <span>{message.createdAt}</span>
                </div>
                <p className="text-sm">{message.content}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">Findings and Recommendations</h2>
          <div className="space-y-3">
            {state.artifacts
              .filter((item) => item.type === "insight" || item.type === "recommendation")
              .slice(0, 4)
              .map((item) => (
                <article key={item.id} className="rounded-lg bg-muted/30 p-3">
                  <p className="inline-flex items-center gap-2 text-xs font-medium text-muted-foreground">
                    {item.type === "insight" ? <Lightbulb className="size-3.5" /> : <Sparkles className="size-3.5" />}
                    {item.type === "insight" ? "Finding" : "Recommendation"}
                  </p>
                  <p className="mt-1 text-sm font-medium">{item.title}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{item.summary}</p>
                  <Button className="mt-3" size="sm" variant="outline" onClick={() => onAddBookmark(item.title)}>
                    <BookmarkPlus className="size-3.5" />
                    Save Bookmark
                  </Button>
                </article>
              ))}
          </div>
        </section>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
          <h2 className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <ChartNoAxesColumn className="size-4" />
            Charts
          </h2>
          <div className="space-y-3">
            {state.generatedCharts.slice(0, 3).map((chart) => (
              <article key={chart} className="rounded-lg bg-muted/30 p-3">
                <p className="text-sm font-medium">{chart}</p>
                <div className="mt-2 h-20 rounded-md bg-gradient-to-br from-primary/20 via-primary/5 to-transparent p-2">
                  <div className="flex h-full items-end gap-1">
                    <div className="w-1/6 rounded bg-primary/40" style={{ height: "45%" }} />
                    <div className="w-1/6 rounded bg-primary/55" style={{ height: "65%" }} />
                    <div className="w-1/6 rounded bg-primary/45" style={{ height: "40%" }} />
                    <div className="w-1/6 rounded bg-primary/60" style={{ height: "75%" }} />
                    <div className="w-1/6 rounded bg-primary/50" style={{ height: "58%" }} />
                    <div className="w-1/6 rounded bg-primary/70" style={{ height: "82%" }} />
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="rounded-2xl bg-card/90 p-4 shadow-sm ring-1 ring-white/5">
          <h2 className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <TableProperties className="size-4" />
            Tables
          </h2>
          <div className="space-y-3">
            {state.generatedTables.slice(0, 1).map((table) => (
              <article key={table} className="rounded-lg bg-muted/30 p-3">
                <p className="mb-2 text-sm font-medium">{table}</p>
                <div className="overflow-x-auto">
                  <table className="min-w-[320px] w-full text-xs">
                    <thead className="text-left text-muted-foreground">
                      <tr>
                        <th className="pb-1">Region</th>
                        <th className="pb-1">Revenue</th>
                        <th className="pb-1">Movement</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td className="py-1">Europe</td><td>$1.2M</td><td>-9%</td></tr>
                      <tr><td className="py-1">APAC</td><td>$980K</td><td>-7%</td></tr>
                      <tr><td className="py-1">North America</td><td>$1.9M</td><td>-2%</td></tr>
                    </tbody>
                  </table>
                </div>
              </article>
            ))}

            <article className="rounded-lg bg-muted/30 p-3">
              <p className="mb-2 text-sm font-medium">KPIs</p>
              <div className="grid grid-cols-3 gap-2 text-xs">
                {state.kpis.map((kpi) => (
                  <div key={kpi.id} className="rounded-md bg-background px-2 py-2">
                    <p className="text-muted-foreground">{kpi.label}</p>
                    <p className="mt-1 font-medium">{kpi.value}</p>
                    <p className="text-muted-foreground">{kpi.change}</p>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </section>
      </div>

      <form onSubmit={submit} className="sticky bottom-3 rounded-2xl bg-card/95 p-4 shadow-sm ring-1 ring-white/5 backdrop-blur">
        <label htmlFor="investigation-input" className="mb-2 block text-sm font-medium text-muted-foreground">
          Continue the investigation
        </label>
        <div className="flex gap-2">
          <Input
            id="investigation-input"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            className="h-12"
            placeholder="Why did revenue decrease?"
          />
          <Button className="h-12 px-4" type="submit">
            <Send className="size-4" />
            Explore
          </Button>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {promptExamples.map((example) => (
            <Button key={example} type="button" size="sm" variant="outline" onClick={() => setPrompt(example)}>
              {example}
            </Button>
          ))}
        </div>
      </form>
    </section>
  )
}
