"use client"

import { useMemo, useState } from "react"

import { AddDataDialog } from "@/components/datasets/add-data-dialog"
import { DataEmptyState } from "@/components/datasets/data-empty-state"
import { DatasetCard } from "@/components/datasets/dataset-card"
import { DatasetPreviewTable } from "@/components/datasets/dataset-preview-table"
import type { DatasetRecord } from "@/components/datasets/types"
import { PageContainer } from "@/components/common/page-container"
import { SectionHeader } from "@/components/common/section-header"
import { Button } from "@/components/ui/button"

export function DataIntakePage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [datasets, setDatasets] = useState<DatasetRecord[]>([])
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null)

  const selectedDataset = useMemo(
    () => datasets.find((dataset) => dataset.id === selectedDatasetId) ?? datasets[0] ?? null,
    [datasets, selectedDatasetId]
  )

  function onDatasetReady(dataset: DatasetRecord) {
    setDatasets((current) => [dataset, ...current])
    setSelectedDatasetId(dataset.id)
  }

  return (
    <>
      <PageContainer>
        <SectionHeader
          title="Data"
          description="Bring datasets into your project and start your investigation with confidence."
          actions={
            <Button variant="outline" onClick={() => setIsDialogOpen(true)}>
              Add Data
            </Button>
          }
        />

        {datasets.length === 0 ? <DataEmptyState onAddData={() => setIsDialogOpen(true)} /> : null}

        {datasets.length > 0 ? (
          <div className="space-y-5">
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
              <p className="font-medium text-emerald-700 dark:text-emerald-400">Your data is ready.</p>
              <p className="mt-1 text-sm text-emerald-700/90 dark:text-emerald-400/90">
                We&apos;ve prepared a preview below.
              </p>
            </div>

            {datasets.map((dataset) => (
              <DatasetCard key={dataset.id} dataset={dataset} onPreview={() => setSelectedDatasetId(dataset.id)} />
            ))}

            {selectedDataset ? <DatasetPreviewTable rows={selectedDataset.previewRows} /> : null}
          </div>
        ) : null}
      </PageContainer>

      <AddDataDialog
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onDatasetReady={onDatasetReady}
      />
    </>
  )
}
