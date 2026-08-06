"use client"

import { useRef, useState } from "react"
import { UploadCloud } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type FileUploadZoneProps = {
  onFileSelected: (file: File | null) => void
  acceptedLabel?: string
}

export function FileUploadZone({
  onFileSelected,
  acceptedLabel = "CSV, Excel (.xlsx), or Excel (.xls)",
}: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  return (
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
      <p className="mt-1 text-sm text-muted-foreground">{acceptedLabel}</p>

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
  )
}
