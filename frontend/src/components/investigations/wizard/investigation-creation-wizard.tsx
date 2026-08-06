"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { ArrowLeft, ArrowRight, CheckCircle2 } from "lucide-react"
import { useRouter } from "next/navigation"

import { ConnectionMappingTable, type ConnectionRow, type MappingChoice } from "@/components/datasets/connection-mapping-table"
import { FileUploadZone } from "@/components/datasets/file-upload-zone"
import { InformationHealthSummary, type HealthIssue } from "@/components/datasets/information-health-summary"
import { DatasetPreviewTable } from "@/components/datasets/dataset-preview-table"
import { mockPreviewRows } from "@/components/datasets/mock-preview"
import type { DatasetRecord } from "@/components/datasets/types"
import { UploadProgress } from "@/components/datasets/upload-progress"
import { PageContainer } from "@/components/common/page-container"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type Audience = "me" | "team" | "leadership" | "client"
type Goal = "understand" | "explain" | "predict" | "improve"
type InformationSource = "csv" | "excel" | "database" | "nothing"
type UploadPhase = "select" | "uploading" | "success"

const chapters = [
  "Question",
  "Context",
  "Information",
  "Upload",
  "Understanding",
  "Connecting",
  "Ready",
]

const questionExamples = [
  "What is driving lower renewal rates in enterprise accounts this quarter?",
  "Where are we seeing delays in our service delivery process?",
  "Which customer groups respond best to our latest pricing updates?",
]

const audienceOptions: Array<{ value: Audience; label: string }> = [
  { value: "me", label: "Me" },
  { value: "team", label: "My Team" },
  { value: "leadership", label: "Leadership" },
  { value: "client", label: "Client" },
]

const goalOptions: Array<{ value: Goal; label: string }> = [
  { value: "understand", label: "Understand" },
  { value: "explain", label: "Explain" },
  { value: "predict", label: "Predict" },
  { value: "improve", label: "Improve" },
]

const infoOptions: Array<{ value: InformationSource; label: string; description: string }> = [
  { value: "csv", label: "CSV", description: "A comma-separated file." },
  { value: "excel", label: "Excel", description: "An .xlsx or .xls workbook." },
  { value: "database", label: "Database", description: "A connected table or export." },
  { value: "nothing", label: "Nothing yet", description: "We can still continue." },
]

const defaultMappings: ConnectionRow[] = [
  { id: "m1", sourceField: "Order Date", suggestedMatch: "Date", confidence: 97, choice: "date" },
  { id: "m2", sourceField: "Region", suggestedMatch: "Region", confidence: 94, choice: "region" },
  { id: "m3", sourceField: "Customer", suggestedMatch: "Account", confidence: 88, choice: "account" },
  { id: "m4", sourceField: "Product Family", suggestedMatch: "Product", confidence: 84, choice: "product" },
  { id: "m5", sourceField: "Revenue", suggestedMatch: "Value", confidence: 98, choice: "value" },
]

function formatUploadDate() {
  return new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

function informationIssues(hasDataset: boolean): HealthIssue[] {
  if (!hasDataset) {
    return [
      {
        id: "h1",
        label: "No information added yet",
        detail: "You can continue now and add information later when it is available.",
        whyItMatters: "Having information in place helps us prepare clearer findings sooner.",
        severity: "low",
      },
    ]
  }

  return [
    {
      id: "h2",
      label: "A few dates use mixed formats",
      detail: "Most rows use YYYY-MM-DD, while a small group uses MM/DD/YYYY.",
      whyItMatters: "Consistent dates help ensure timelines and comparisons remain accurate.",
      severity: "medium",
    },
    {
      id: "h3",
      label: "Some records are missing region",
      detail: "38 rows do not include a region value.",
      whyItMatters: "Region gaps can hide patterns when comparing performance across locations.",
      severity: "medium",
    },
  ]
}

export function InvestigationCreationWizard() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [question, setQuestion] = useState("")
  const [audience, setAudience] = useState<Audience | null>(null)
  const [goal, setGoal] = useState<Goal | null>(null)
  const [informationSource, setInformationSource] = useState<InformationSource | null>(null)
  const [uploadPhase, setUploadPhase] = useState<UploadPhase>("select")
  const [uploadProgress, setUploadProgress] = useState(0)
  const [dataset, setDataset] = useState<DatasetRecord | null>(null)
  const [mappingRows, setMappingRows] = useState<ConnectionRow[]>(defaultMappings)
  const timerRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current)
      }
    }
  }, [])

  const completion = useMemo(() => Math.round(((step + 1) / chapters.length) * 100), [step])

  function startUpload(file: File) {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current)
    }

    setUploadPhase("uploading")
    setUploadProgress(0)

    timerRef.current = window.setInterval(() => {
      setUploadProgress((current) => {
        const next = Math.min(current + 10, 100)
        if (next === 100) {
          if (timerRef.current !== null) {
            window.clearInterval(timerRef.current)
          }

          setDataset({
            id: crypto.randomUUID(),
            name: file.name,
            rows: 2487,
            columns: 7,
            uploadDate: formatUploadDate(),
            status: "Ready",
            previewRows: mockPreviewRows,
          })
          setUploadPhase("success")
        }

        return next
      })
    }, 180)
  }

  function canContinueCurrentStep() {
    if (step === 0) return question.trim().length > 12
    if (step === 1) return audience !== null && goal !== null
    if (step === 2) return informationSource !== null
    if (step === 3) return informationSource === "nothing" || dataset !== null
    return true
  }

  function nextStep() {
    if (step < chapters.length - 1) {
      setStep((current) => current + 1)
    }
  }

  function previousStep() {
    if (step > 0) {
      setStep((current) => current - 1)
    }
  }

  function updateMapping(id: string, choice: MappingChoice) {
    setMappingRows((current) => current.map((row) => (row.id === id ? { ...row, choice } : row)))
  }

  function beginInvestigation() {
    const audienceLabel = audienceOptions.find((option) => option.value === audience)?.label
    const goalLabel = goalOptions.find((option) => option.value === goal)?.label

    localStorage.setItem(
      "blip-investigation-draft-v1",
      JSON.stringify({
        question,
        audience: audienceLabel,
        goal: goalLabel,
        datasetName: dataset?.name,
      })
    )

    router.push("/investigations/workspace")
  }

  return (
    <PageContainer className="py-5 sm:py-6">
      <div className="mx-auto w-full max-w-5xl space-y-6">
        <section className="rounded-2xl border border-border bg-card p-5 sm:p-6">
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm font-medium text-muted-foreground">Investigation Creation</p>
            <p className="text-sm text-muted-foreground">{completion}% complete</p>
          </div>

          <div className="mt-4 grid grid-cols-7 gap-2">
            {chapters.map((chapter, index) => (
              <button
                key={chapter}
                type="button"
                onClick={() => {
                  if (index <= step) setStep(index)
                }}
                className={cn(
                  "rounded-lg border px-2 py-2 text-xs font-medium transition-colors",
                  index === step && "border-primary bg-primary/10 text-primary",
                  index < step && "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400",
                  index > step && "border-border bg-muted/20 text-muted-foreground"
                )}
              >
                <span className="hidden sm:inline">{chapter}</span>
                <span className="sm:hidden">{index + 1}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-border bg-card p-5 sm:p-6">
          {step === 0 ? (
            <div className="space-y-5">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight">What would we like to understand today?</h1>
                <p className="mt-1 text-sm text-muted-foreground">Start with a clear business question.</p>
              </div>

              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                className="min-h-36 w-full resize-none rounded-xl border border-input bg-background p-4 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                placeholder="Describe the question we want to investigate..."
              />

              <div>
                <p className="mb-2 text-sm font-medium text-muted-foreground">Example questions</p>
                <div className="flex flex-wrap gap-2">
                  {questionExamples.map((example) => (
                    <Button key={example} type="button" variant="outline" size="sm" onClick={() => setQuestion(example)}>
                      {example}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          ) : null}

          {step === 1 ? (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Context</h2>
                <p className="mt-1 text-sm text-muted-foreground">Tell us who this investigation supports and what outcome matters most.</p>
              </div>

              <div className="space-y-3">
                <p className="text-sm font-medium">Who is this investigation for?</p>
                <div className="grid gap-2 sm:grid-cols-2">
                  {audienceOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setAudience(option.value)}
                      className={cn(
                        "rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                        audience === option.value ? "border-primary bg-primary/10 text-primary" : "border-border bg-background"
                      )}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <p className="text-sm font-medium">Goal</p>
                <div className="grid gap-2 sm:grid-cols-2">
                  {goalOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setGoal(option.value)}
                      className={cn(
                        "rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                        goal === option.value ? "border-primary bg-primary/10 text-primary" : "border-border bg-background"
                      )}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : null}

          {step === 2 ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">What information do we already have?</h2>
                <p className="mt-1 text-sm text-muted-foreground">Choose the option that best matches your current situation.</p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {infoOptions.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setInformationSource(option.value)}
                    className={cn(
                      "rounded-xl border p-4 text-left transition-colors",
                      informationSource === option.value ? "border-primary bg-primary/10" : "border-border bg-background"
                    )}
                  >
                    <p className="font-medium">{option.label}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{option.description}</p>
                  </button>
                ))}
              </div>

              {informationSource === "nothing" ? (
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-700 dark:text-emerald-400">
                  You can continue without adding information now. We&apos;ll guide you when you&apos;re ready.
                </div>
              ) : null}
            </div>
          ) : null}

          {step === 3 ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Upload</h2>
                <p className="mt-1 text-sm text-muted-foreground">Add your information when ready.</p>
              </div>

              {informationSource === "nothing" ? (
                <div className="rounded-xl border border-border bg-muted/20 p-4 text-sm text-muted-foreground">
                  You can continue now without an upload. We&apos;ll help you add information later.
                </div>
              ) : (
                <>
                  {uploadPhase === "select" ? (
                    <FileUploadZone
                      onFileSelected={(file) => {
                        if (file) {
                          startUpload(file)
                        }
                      }}
                    />
                  ) : null}
                  {uploadPhase === "uploading" ? <UploadProgress value={uploadProgress} /> : null}
                  {uploadPhase === "success" && dataset ? (
                    <div className="space-y-4">
                      <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
                        <p className="font-medium text-emerald-700 dark:text-emerald-400">Your data is ready.</p>
                        <p className="mt-1 text-sm text-emerald-700/90 dark:text-emerald-400/90">
                          We&apos;ve prepared a preview below.
                        </p>
                      </div>
                      <DatasetPreviewTable rows={dataset.previewRows} />
                    </div>
                  ) : null}
                </>
              )}
            </div>
          ) : null}

          {step === 4 ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Understanding Your Information</h2>
                <p className="mt-1 text-sm text-muted-foreground">Here is what we noticed and why it matters.</p>
              </div>
              <InformationHealthSummary issues={informationIssues(dataset !== null)} />
            </div>
          ) : null}

          {step === 5 ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Connecting Information</h2>
                <p className="mt-1 text-sm text-muted-foreground">Confirm suggested matches, confidence, and make any overrides you need.</p>
              </div>
              <ConnectionMappingTable rows={mappingRows} onChoiceChange={updateMapping} />
            </div>
          ) : null}

          {step === 6 ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Ready</h2>
                <p className="mt-1 text-sm text-muted-foreground">Everything is prepared.</p>
              </div>

              <div className="grid gap-3">
                <div className="rounded-lg border border-border bg-muted/20 px-4 py-3 text-sm font-medium">
                  <span className="inline-flex items-center gap-2">
                    <CheckCircle2 className="size-4 text-emerald-500" />
                    Question ✓
                  </span>
                </div>
                <div className="rounded-lg border border-border bg-muted/20 px-4 py-3 text-sm font-medium">
                  <span className="inline-flex items-center gap-2">
                    <CheckCircle2 className="size-4 text-emerald-500" />
                    Information ✓
                  </span>
                </div>
                <div className="rounded-lg border border-border bg-muted/20 px-4 py-3 text-sm font-medium">
                  <span className="inline-flex items-center gap-2">
                    <CheckCircle2 className="size-4 text-emerald-500" />
                    Connections ✓
                  </span>
                </div>
              </div>

              <Button className="h-10 px-5" onClick={beginInvestigation}>Begin Investigation</Button>
            </div>
          ) : null}

          <div className="mt-6 flex items-center justify-between border-t border-border pt-5">
            <Button type="button" variant="ghost" onClick={previousStep} disabled={step === 0}>
              <ArrowLeft className="size-4" />
              Back
            </Button>

            {step < chapters.length - 1 ? (
              <Button type="button" onClick={nextStep} disabled={!canContinueCurrentStep()}>
                Continue
                <ArrowRight className="size-4" />
              </Button>
            ) : null}
          </div>
        </section>
      </div>
    </PageContainer>
  )
}
