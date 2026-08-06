"use client"

import { useEffect, useMemo, useState } from "react"
import { ArrowLeft, ArrowRight, CheckCircle2, LoaderCircle } from "lucide-react"

import { FileUploadZone } from "@/components/datasets/file-upload-zone"
import { UploadProgress } from "@/components/datasets/upload-progress"
import { PageContainer } from "@/components/common/page-container"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
  type BusinessGoalResponse,
  type InvestigationFindingsResponse,
  type InvestigationStatusResponse,
  type SemanticProfileResponse,
  generateSemanticProfile,
  getBusinessGoals,
  getInvestigationFindings,
  getInvestigationStatus,
  startInvestigation,
  uploadDataset,
} from "@/services/investigation-api"

type UploadPhase = "select" | "uploading" | "success" | "error"

const chapters = [
  "Upload Dataset",
  "Semantic Profile",
  "Choose Business Goal",
  "Run Investigation",
  "Execution Progress",
  "Findings",
]

export function InvestigationCreationWizard() {
  const [step, setStep] = useState(0)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadPhase, setUploadPhase] = useState<UploadPhase>("select")
  const [uploadProgress, setUploadProgress] = useState(0)
  const [datasetId, setDatasetId] = useState<string | null>(null)
  const [semanticProfile, setSemanticProfile] = useState<SemanticProfileResponse | null>(null)
  const [goals, setGoals] = useState<BusinessGoalResponse[]>([])
  const [selectedGoalId, setSelectedGoalId] = useState<string | null>(null)
  const [investigationId, setInvestigationId] = useState<string | null>(null)
  const [status, setStatus] = useState<InvestigationStatusResponse | null>(null)
  const [findings, setFindings] = useState<InvestigationFindingsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const completion = useMemo(() => Math.round(((step + 1) / chapters.length) * 100), [step])

  useEffect(() => {
    if (step !== 4 || !investigationId) {
      return
    }

    let active = true
    const intervalId = window.setInterval(async () => {
      try {
        const current = await getInvestigationStatus(investigationId)
        if (!active) {
          return
        }

        setStatus(current)

        if (current.status === "completed") {
          const findingsResponse = await getInvestigationFindings(investigationId)
          if (!active) {
            return
          }
          setFindings(findingsResponse)
          setStep(5)
          window.clearInterval(intervalId)
        }

        if (current.status === "failed") {
          setError(current.warnings[0] ?? "Investigation failed")
          window.clearInterval(intervalId)
        }
      } catch (err) {
        if (!active) {
          return
        }
        const message = err instanceof Error ? err.message : "Failed to monitor investigation"
        setError(message)
        window.clearInterval(intervalId)
      }
    }, 1200)

    return () => {
      active = false
      window.clearInterval(intervalId)
    }
  }, [investigationId, step])

  async function handleUploadStep() {
    if (!selectedFile) {
      setError("Select a dataset file before continuing")
      return
    }

    setLoading(true)
    setError(null)
    setUploadPhase("uploading")
    setUploadProgress(35)

    try {
      const uploaded = await uploadDataset(selectedFile)
      setUploadProgress(100)
      setDatasetId(uploaded.dataset_id)
      setUploadPhase("success")
      setStep(1)
    } catch (err) {
      setUploadPhase("error")
      setUploadProgress(0)
      const message = err instanceof Error ? err.message : "Dataset upload failed"
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  async function handleSemanticProfileStep() {
    if (!datasetId) {
      setError("Upload dataset before generating semantic profile")
      return
    }

    setLoading(true)
    setError(null)
    try {
      const profile = await generateSemanticProfile(datasetId)
      const goalsResponse = await getBusinessGoals()
      setSemanticProfile(profile)
      setGoals(goalsResponse)
      setStep(2)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Semantic profiling failed"
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  async function handleStartInvestigation() {
    if (!datasetId || !selectedGoalId) {
      setError("Select a business goal before running investigation")
      return
    }

    setLoading(true)
    setError(null)
    try {
      const started = await startInvestigation(datasetId, selectedGoalId)
      setInvestigationId(started.investigation_id)
      setStatus({
        investigation_id: started.investigation_id,
        status: started.status,
        progress: started.progress,
        current_step: started.current_step,
        warnings: [],
      })
      setStep(4)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to start investigation"
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  async function nextStep() {
    if (loading) {
      return
    }

    if (step === 0) {
      await handleUploadStep()
      return
    }

    if (step === 1) {
      await handleSemanticProfileStep()
      return
    }

    if (step === 2) {
      if (!selectedGoalId) {
        setError("Choose a business goal before continuing")
        return
      }
      setStep(3)
      return
    }

    if (step === 3) {
      await handleStartInvestigation()
    }
  }

  function previousStep() {
    if (loading || step === 4) {
      return
    }
    if (step > 0) {
      setStep((current) => current - 1)
    }
  }

  function resetWorkflow() {
    setStep(0)
    setSelectedFile(null)
    setUploadPhase("select")
    setUploadProgress(0)
    setDatasetId(null)
    setSemanticProfile(null)
    setSelectedGoalId(null)
    setInvestigationId(null)
    setStatus(null)
    setFindings(null)
    setError(null)
  }

  return (
    <PageContainer className="py-5 sm:py-6">
      <div className="mx-auto w-full max-w-5xl space-y-6">
        <section className="rounded-2xl border border-border bg-card p-5 sm:p-6">
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm font-medium text-muted-foreground">Investigation Creation</p>
            <p className="text-sm text-muted-foreground">{completion}% complete</p>
          </div>

          <div className="mt-4 grid grid-cols-6 gap-2">
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
                <h1 className="text-2xl font-semibold tracking-tight">Upload dataset</h1>
                <p className="mt-1 text-sm text-muted-foreground">Step 1: Add a CSV or Excel file to begin your investigation.</p>
              </div>

              <FileUploadZone
                onFileSelected={(file) => {
                  setSelectedFile(file)
                  setError(null)
                }}
              />

              {selectedFile ? (
                <p className="text-sm text-muted-foreground">
                  Selected file: <span className="font-medium text-foreground">{selectedFile.name}</span>
                </p>
              ) : null}

              {uploadPhase === "uploading" ? <UploadProgress value={uploadProgress} /> : null}

              {uploadPhase === "success" ? (
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-700 dark:text-emerald-400">
                  Dataset uploaded successfully.
                </div>
              ) : null}
            </div>
          ) : null}

          {step === 1 ? (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Display semantic profile</h2>
                <p className="mt-1 text-sm text-muted-foreground">Step 2: BLIP is understanding your dataset structure and quality.</p>
              </div>

              <div className="rounded-xl border border-border bg-muted/20 p-4">
                <p className="text-sm text-muted-foreground">Understanding your dataset...</p>
                <p className="mt-1 text-sm text-muted-foreground">Click Continue to generate the semantic profile.</p>
              </div>

              {semanticProfile ? (
                <div className="space-y-4">
                  <div className="grid gap-3 sm:grid-cols-4">
                    <div className="rounded-lg border border-border bg-background p-3">
                      <p className="text-xs text-muted-foreground">Columns</p>
                      <p className="mt-1 text-lg font-semibold">{semanticProfile.columns}</p>
                    </div>
                    <div className="rounded-lg border border-border bg-background p-3">
                      <p className="text-xs text-muted-foreground">Measures</p>
                      <p className="mt-1 text-lg font-semibold">{semanticProfile.measures}</p>
                    </div>
                    <div className="rounded-lg border border-border bg-background p-3">
                      <p className="text-xs text-muted-foreground">Dimensions</p>
                      <p className="mt-1 text-lg font-semibold">{semanticProfile.dimensions}</p>
                    </div>
                    <div className="rounded-lg border border-border bg-background p-3">
                      <p className="text-xs text-muted-foreground">Health score</p>
                      <p className="mt-1 text-lg font-semibold">{Math.round(semanticProfile.health_score * 100)}%</p>
                    </div>
                  </div>

                  <div className="overflow-hidden rounded-xl border border-border">
                    <table className="w-full border-collapse text-sm">
                      <thead className="bg-muted/20 text-left text-xs uppercase tracking-wide text-muted-foreground">
                        <tr>
                          <th className="px-3 py-2">Column</th>
                          <th className="px-3 py-2">Type</th>
                          <th className="px-3 py-2">Primitive</th>
                          <th className="px-3 py-2">Missing</th>
                        </tr>
                      </thead>
                      <tbody>
                        {semanticProfile.columns_profile.map((column) => (
                          <tr key={column.name} className="border-t border-border/70">
                            <td className="px-3 py-2">{column.name}</td>
                            <td className="px-3 py-2 text-muted-foreground">{column.data_type}</td>
                            <td className="px-3 py-2">{column.primitive}</td>
                            <td className="px-3 py-2">{column.missing_values}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}

          {step === 2 ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Choose Business Goal</h2>
                <p className="mt-1 text-sm text-muted-foreground">Step 3: Choose what you want BLIP to achieve.</p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {goals.map((goal) => (
                  <button
                    key={goal.goal_id}
                    type="button"
                    onClick={() => {
                      setSelectedGoalId(goal.goal_id)
                      setError(null)
                    }}
                    className={cn(
                      "rounded-xl border p-4 text-left transition-colors",
                      selectedGoalId === goal.goal_id ? "border-primary bg-primary/10" : "border-border bg-background"
                    )}
                  >
                    <p className="font-medium">{goal.name}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{goal.description}</p>
                    <p className="mt-2 text-xs uppercase tracking-wide text-muted-foreground">{goal.business_purpose}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          {step === 3 ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Run Investigation</h2>
                <p className="mt-1 text-sm text-muted-foreground">Step 4: BLIP will execute the selected goal against your semantic profile.</p>
              </div>

              <div className="rounded-xl border border-border bg-muted/20 p-4 text-sm text-muted-foreground">
                Planning the investigation and preparing analytical capability execution.
              </div>
            </div>
          ) : null}

          {step === 4 ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Execution Progress</h2>
                <p className="mt-1 text-sm text-muted-foreground">Step 5: Track investigation progress across the BLIP pipeline.</p>
              </div>

              <div className="rounded-xl border border-border bg-card p-4">
                <p className="inline-flex items-center gap-2 text-sm font-medium text-foreground">
                  <LoaderCircle className="size-4 animate-spin" />
                  {status?.current_step ?? "Starting investigation..."}
                </p>
                <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary transition-all"
                    style={{ width: `${status?.progress ?? 0}%` }}
                  />
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{status?.progress ?? 0}% complete</p>
              </div>

              <div className="space-y-2 rounded-xl border border-border bg-muted/20 p-4 text-sm text-muted-foreground">
                <p>Understanding your dataset...</p>
                <p>Planning the investigation...</p>
                <p>Executing analytical capabilities...</p>
                <p>Building findings...</p>
              </div>
            </div>
          ) : null}

          {step === 5 && findings ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-2xl font-semibold tracking-tight">Findings</h2>
                <p className="mt-1 text-sm text-muted-foreground">Step 6: Review structured findings with supporting analyses and evidence.</p>
              </div>

              <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
                <p className="inline-flex items-center gap-2 text-sm font-medium text-emerald-700 dark:text-emerald-400">
                  <CheckCircle2 className="size-4" />
                  Investigation complete with confidence {Math.round(findings.confidence * 100)}%
                </p>
              </div>

              <div className="space-y-3">
                {findings.findings_collection.findings.map((finding) => (
                  <article key={finding.id} className="rounded-xl border border-border bg-card p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="text-base font-semibold">{finding.title}</h3>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="rounded-full border border-border px-2 py-1">{finding.severity}</span>
                        <span className="rounded-full border border-border px-2 py-1">{Math.round(finding.confidence * 100)}% confidence</span>
                      </div>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">{finding.description}</p>
                    <p className="mt-2 text-xs text-muted-foreground">Supporting analyses: {finding.supporting_analyses.join(", ")}</p>

                    <details className="mt-3 rounded-lg border border-border bg-muted/20 p-3">
                      <summary className="cursor-pointer text-sm font-medium">Inspect supporting evidence</summary>
                      <div className="mt-3 space-y-2">
                        {finding.supporting_evidence.map((evidence, index) => (
                          <div key={`${finding.id}-${index}`} className="rounded-md border border-border bg-background p-2 text-sm">
                            <p className="font-medium">{evidence.capability_name} • {evidence.evidence_type}</p>
                            <p className="text-muted-foreground">Value: {evidence.evidence_value}</p>
                            <p className="text-xs text-muted-foreground">Trace: {evidence.trace_reference}</p>
                          </div>
                        ))}
                      </div>
                    </details>
                  </article>
                ))}
              </div>

              <Button type="button" variant="outline" onClick={resetWorkflow}>
                Start another investigation
              </Button>
            </div>
          ) : null}

          {error ? (
            <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-700 dark:text-red-300">
              {error}
            </div>
          ) : null}

          <div className="mt-6 flex items-center justify-between border-t border-border pt-5">
            <Button type="button" variant="ghost" onClick={previousStep} disabled={step === 0 || loading || step === 4}>
              <ArrowLeft className="size-4" />
              Back
            </Button>

            {step < 4 ? (
              <Button type="button" onClick={nextStep} disabled={loading}>
                {loading ? (
                  <>
                    <LoaderCircle className="size-4 animate-spin" />
                    Working...
                  </>
                ) : (
                  <>
                    Continue
                    <ArrowRight className="size-4" />
                  </>
                )}
              </Button>
            ) : null}

            {step === 4 ? (
              <Button type="button" variant="outline" disabled>
                Monitoring progress...
              </Button>
            ) : null}
          </div>
        </section>
      </div>
    </PageContainer>
  )
}
