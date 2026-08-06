"use client"

import { useEffect, useMemo, useState } from "react"

import { createInitialWorkspaceState } from "@/components/investigations/workspace/mock-state"
import type { InvestigationDraft, WorkspaceArtifact, WorkspaceMessage, WorkspaceState } from "@/components/investigations/workspace/types"

const WORKSPACE_STORAGE_KEY = "blip-workspace-state-v1"
const DRAFT_STORAGE_KEY = "blip-investigation-draft-v1"

function nowLabel() {
  return new Date().toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  })
}

function normalizeTitle(text: string) {
  const clean = text.trim()
  if (!clean) return "New finding"
  return clean.length > 56 ? `${clean.slice(0, 56)}...` : clean
}

function nextArtifactId() {
  return crypto.randomUUID()
}

function parseJson<T>(raw: string | null): T | null {
  if (!raw) return null
  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

export function useWorkspaceState() {
  const [state, setState] = useState<WorkspaceState>(() => {
    if (typeof window === "undefined") {
      return createInitialWorkspaceState()
    }

    const savedState = parseJson<WorkspaceState>(localStorage.getItem(WORKSPACE_STORAGE_KEY))
    if (savedState) {
      return savedState
    }

    const draft = parseJson<InvestigationDraft>(localStorage.getItem(DRAFT_STORAGE_KEY))
    const next = createInitialWorkspaceState(draft ?? undefined)
    localStorage.setItem(WORKSPACE_STORAGE_KEY, JSON.stringify(next))
    return next
  })
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      setHydrated(true)
    })

    return () => {
      window.cancelAnimationFrame(frame)
    }
  }, [])

  useEffect(() => {
    if (!hydrated) return
    localStorage.setItem(WORKSPACE_STORAGE_KEY, JSON.stringify(state))
  }, [state, hydrated])

  const summaryCounts = useMemo(
    () => ({
      conversation: state.messages.length,
      insights: state.savedInsights.length,
      charts: state.generatedCharts.length,
      tables: state.generatedTables.length,
      notes: state.notes.length,
      bookmarks: state.bookmarks.length,
    }),
    [state]
  )

  function pushMessage(prompt: string) {
    const userMessage: WorkspaceMessage = {
      id: crypto.randomUUID(),
      author: "You",
      content: prompt,
      createdAt: nowLabel(),
    }

    const workspaceMessage: WorkspaceMessage = {
      id: crypto.randomUUID(),
      author: "Workspace",
      content:
        "We found a meaningful movement connected to this question. The updated chart, table, and recommendation are now ready.",
      createdAt: nowLabel(),
    }

    const title = normalizeTitle(prompt)

    const newArtifacts: WorkspaceArtifact[] = [
      {
        id: nextArtifactId(),
        type: "insight",
        title: `Finding: ${title}`,
        summary: "This question reveals a noticeable regional movement worth a deeper check.",
        createdAt: nowLabel(),
      },
      {
        id: nextArtifactId(),
        type: "chart",
        title: `Trend view: ${title}`,
        summary: "Prepared a trend comparison to highlight where movement accelerated.",
        createdAt: nowLabel(),
      },
      {
        id: nextArtifactId(),
        type: "table",
        title: `Breakdown table: ${title}`,
        summary: "Added a table to compare segments side by side.",
        createdAt: nowLabel(),
      },
      {
        id: nextArtifactId(),
        type: "recommendation",
        title: `Recommendation: ${title}`,
        summary: "Check recent policy and service changes in the top-moving segment.",
        createdAt: nowLabel(),
      },
    ]

    setState((current) => ({
      ...current,
      messages: [...current.messages, userMessage, workspaceMessage],
      artifacts: [...newArtifacts, ...current.artifacts],
      savedInsights: [newArtifacts[0].summary, ...current.savedInsights],
      generatedCharts: [newArtifacts[1].title, ...current.generatedCharts],
      generatedTables: [newArtifacts[2].title, ...current.generatedTables],
      recommendations: [newArtifacts[3].summary, ...current.recommendations],
      notes: [`Checked: ${title}`, ...current.notes],
      timeline: [...current.timeline, `Question explored: ${title}`],
      currentVisualization: newArtifacts[1].title,
    }))
  }

  function addBookmark(value: string) {
    const clean = value.trim()
    if (!clean) return
    setState((current) => {
      if (current.bookmarks.includes(clean)) return current
      return { ...current, bookmarks: [clean, ...current.bookmarks] }
    })
  }

  return {
    state,
    hydrated,
    summaryCounts,
    pushMessage,
    addBookmark,
  }
}
