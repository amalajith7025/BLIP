export type WorkspaceMessage = {
  id: string
  author: "You" | "Workspace"
  content: string
  createdAt: string
}

export type WorkspaceArtifact = {
  id: string
  type: "insight" | "chart" | "table" | "metric" | "recommendation"
  title: string
  summary: string
  createdAt: string
}

export type WorkspaceKpi = {
  id: string
  label: string
  value: string
  change: string
}

export type WorkspaceState = {
  title: string
  question: string
  status: "In Progress" | "Ready"
  timeline: string[]
  audience: string
  goal: string
  datasets: string[]
  dimensions: string[]
  measures: string[]
  healthScore: number
  questionConfidence: number
  filters: string[]
  currentVisualization: string
  futureSupportStatus: string
  messages: WorkspaceMessage[]
  artifacts: WorkspaceArtifact[]
  savedInsights: string[]
  generatedCharts: string[]
  generatedTables: string[]
  notes: string[]
  bookmarks: string[]
  recommendations: string[]
  kpis: WorkspaceKpi[]
}

export type InvestigationDraft = {
  question?: string
  audience?: string
  goal?: string
  datasetName?: string
}
