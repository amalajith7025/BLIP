"use client"

import { PageContainer } from "@/components/common/page-container"
import { WorkspaceCenterPanel } from "@/components/investigations/workspace/workspace-center-panel"
import { WorkspaceLeftPanel } from "@/components/investigations/workspace/workspace-left-panel"
import { WorkspaceRightPanel } from "@/components/investigations/workspace/workspace-right-panel"
import { useWorkspaceState } from "@/components/investigations/workspace/use-workspace-state"

export function InvestigationWorkspace() {
  const { state, hydrated, summaryCounts, pushMessage, addBookmark } = useWorkspaceState()

  if (!hydrated) {
    return (
      <PageContainer className="py-6">
        <div className="rounded-2xl bg-card/80 p-8 text-sm text-muted-foreground shadow-sm ring-1 ring-white/5">
          Preparing your investigation workspace...
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer className="py-4 sm:py-5">
      <div className="grid gap-4 xl:grid-cols-[280px_minmax(0,1fr)_320px]">
        <WorkspaceLeftPanel state={state} summaryCounts={summaryCounts} />
        <WorkspaceCenterPanel state={state} onSubmitPrompt={pushMessage} onAddBookmark={addBookmark} />
        <WorkspaceRightPanel state={state} />
      </div>
    </PageContainer>
  )
}
