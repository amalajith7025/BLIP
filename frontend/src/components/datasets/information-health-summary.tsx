import { AlertCircle, CircleCheckBig } from "lucide-react"

type HealthIssue = {
  id: string
  label: string
  detail: string
  whyItMatters: string
  severity: "low" | "medium"
}

type InformationHealthSummaryProps = {
  issues: HealthIssue[]
}

export function InformationHealthSummary({ issues }: InformationHealthSummaryProps) {
  if (issues.length === 0) {
    return (
      <section className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
        <p className="inline-flex items-center gap-2 text-sm font-medium text-emerald-700 dark:text-emerald-400">
          <CircleCheckBig className="size-4" />
          Everything looks ready.
        </p>
      </section>
    )
  }

  return (
    <section className="rounded-xl border border-border bg-card">
      <div className="border-b border-border px-5 py-4">
        <h3 className="text-base font-semibold">Understanding Your Information</h3>
        <p className="mt-1 text-sm text-muted-foreground">We checked your information and highlighted what to review.</p>
      </div>

      <div className="space-y-3 p-4">
        {issues.map((issue) => (
          <article key={issue.id} className="rounded-lg border border-border bg-muted/20 p-4">
            <p className="inline-flex items-center gap-2 text-sm font-medium">
              <AlertCircle className="size-4 text-amber-500" />
              {issue.label}
            </p>
            <p className="mt-2 text-sm text-muted-foreground">{issue.detail}</p>
            <p className="mt-2 text-sm text-foreground">
              <span className="font-medium">Why this matters:</span> {issue.whyItMatters}
            </p>
          </article>
        ))}
      </div>
    </section>
  )
}

export type { HealthIssue }
