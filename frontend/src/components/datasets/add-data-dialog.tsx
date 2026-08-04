"use client"

import { useEffect, useRef, useState } from "react"
import { UploadCloud, X } from "lucide-react"

import { mockPreviewRows } from "@/components/datasets/mock-preview"
import type { DatasetRecord } from "@/components/datasets/types"
import { UploadProgress } from "@/components/datasets/upload-progress"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type AddDataDialogProps = {
  open: boolean
  onClose: () => void
  onDatasetReady: (dataset: DatasetRecord) => void
}

type UploadPhase = "select" | "uploading" | "success"

function formatUploadDate() {
  return new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

export function AddDataDialog({ open, onClose, onDatasetReady }: AddDataDialogProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [phase, setPhase] = useState<UploadPhase>("select")
  const [lastDataset, setLastDataset] = useState<DatasetRecord | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const intervalRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current)
      }
    }
  }, [])

  if (!open) {
    return null
  }

  function resetAndClose() {
    setIsDragging(false)
    setProgress(0)
    setPhase("select")
    setLastDataset(null)
    onClose()
  }

  function startUpload(file: File) {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current)
    }

    setPhase("uploading")
    setProgress(0)

    intervalRef.current = window.setInterval(() => {
      setProgress((current) => {
        const next = Math.min(current + 10, 100)

        if (next === 100) {
          if (intervalRef.current !== null) {
            window.clearInterval(intervalRef.current)
          }

          const dataset: DatasetRecord = {
            id: crypto.randomUUID(),
            name: file.name,
            rows: 2487,
            columns: 7,
            uploadDate: formatUploadDate(),
            status: "Ready",
            previewRows: mockPreviewRows,
          }

          setLastDataset(dataset)
          onDatasetReady(dataset)
          setPhase("success")
        }

        return next
      })
    }, 180)
  }

  function onFileSelected(file: File | null) {
    if (!file) {
      return
    }

    startUpload(file)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-2xl rounded-2xl border border-border bg-card shadow-lg">
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold">Add Data</h2>
            <p className="text-sm text-muted-foreground">Bring a dataset into your project.</p>
          </div>
          <Button variant="ghost" size="icon" onClick={resetAndClose} aria-label="Close add data dialog">
            <X className="size-4" />
          </Button>
        </div>

        <div className="space-y-5 px-6 py-5">
          {phase === "select" ? (
            <>
              <div
                onDragOver={(event) => {
                  event.preventDefault()
                  setIsDragging(true)
                }}
                onDragLeave={(event) => {
                  event.preventDefault()
                  setIsDragging(false)
                }}
                onDrop={(event) => {
                  event.preventDefault()
                  setIsDragging(false)
                  const droppedFile = event.dataTransfer.files?.[0] ?? null
                  onFileSelected(droppedFile)
                }}
                className={cn(
                  "rounded-xl border-2 border-dashed p-8 text-center transition-colors",
                  isDragging ? "border-primary bg-primary/5" : "border-border bg-muted/20"
                )}
              >
                <div className="mx-auto mb-3 flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <UploadCloud className="size-5" />
                </div>
                <h3 className="text-base font-semibold">Drag and drop your file here</h3>
                <p className="mt-1 text-sm text-muted-foreground">CSV, Excel (.xlsx), or Excel (.xls)</p>

                <div className="mt-5">
                  <input
                    ref={inputRef}
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    className="hidden"
                    onChange={(event) => onFileSelected(event.target.files?.[0] ?? null)}
                  />
                  <Button variant="outline" onClick={() => inputRef.current?.click()}>
                    Browse Files
                  </Button>
                </div>
              </div>

              <div className="rounded-lg border border-border bg-muted/20 p-4 text-sm text-muted-foreground">
                <p className="font-medium text-foreground">Accepted file types</p>
                <ul className="mt-2 space-y-1">
                  <li>CSV</li>
                  <li>Excel (.xlsx)</li>
                  <li>Excel (.xls)</li>
                </ul>
              </div>
            </>
          ) : null}

          {phase === "uploading" ? <UploadProgress value={progress} /> : null}

          {phase === "success" ? (
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
              <p className="font-medium text-emerald-700 dark:text-emerald-400">Your data is ready.</p>
              <p className="mt-1 text-sm text-emerald-700/90 dark:text-emerald-400/90">
                We&apos;ve prepared a preview below.
              </p>
              {lastDataset ? <p className="mt-3 text-sm text-foreground">Dataset: {lastDataset.name}</p> : null}
              <div className="mt-4">
                <Button onClick={resetAndClose}>Done</Button>
              </div>
            </div>
          ) : null}
        </div>

        {phase !== "success" ? (
          <div className="flex justify-end border-t border-border px-6 py-4">
            <Button variant="ghost" onClick={resetAndClose}>
              Cancel
            </Button>
          </div>
        ) : null}
      </div>
    </div>
  )
}
