import type { InvestigationDraft, WorkspaceState } from "@/components/investigations/workspace/types"

function nowLabel() {
  return new Date().toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  })
}

export function createInitialWorkspaceState(draft?: InvestigationDraft): WorkspaceState {
  const question = draft?.question?.trim() || "What is driving revenue changes across regions this quarter?"

  return {
    title: "Regional Revenue Investigation",
    question,
    status: "In Progress",
    timeline: ["Investigation created", "Information connected", "Workspace prepared"],
    audience: draft?.audience || "My Team",
    goal: draft?.goal || "Understand",
    datasets: [draft?.datasetName || "Q3_revenue_snapshot.xlsx"],
    dimensions: ["Region", "Segment", "Product"],
    measures: ["Revenue", "Orders", "Complaints"],
    healthScore: 89,
    questionConfidence: 86,
    filters: ["Quarter: Q3", "Currency: USD"],
    currentVisualization: "Revenue trend by region",
    futureSupportStatus: "Ready for future guidance features",
    messages: [
      {
        id: "m-1",
        author: "Workspace",
        content:
          "We prepared your investigation. Start with a focused question and we will keep every finding organized for you.",
        createdAt: nowLabel(),
      },
    ],
    artifacts: [
      {
        id: "a-1",
        type: "insight",
        title: "Starting finding",
        summary: "Revenue softening appears concentrated in two regions.",
        createdAt: nowLabel(),
      },
      {
        id: "a-2",
        type: "chart",
        title: "Revenue trend by region",
        summary: "Monthly trend prepared for comparison.",
        createdAt: nowLabel(),
      },
      {
        id: "a-3",
        type: "table",
        title: "Region and segment breakdown",
        summary: "Prepared a sortable comparison table.",
        createdAt: nowLabel(),
      },
      {
        id: "a-4",
        type: "metric",
        title: "Quarter revenue",
        summary: "$4.8M total revenue captured.",
        createdAt: nowLabel(),
      },
      {
        id: "a-5",
        type: "recommendation",
        title: "Next step",
        summary: "Review Europe and APAC order volume changes.",
        createdAt: nowLabel(),
      },
    ],
    savedInsights: ["Revenue softening appears concentrated in Europe and APAC."],
    generatedCharts: ["Revenue trend by region"],
    generatedTables: ["Region and segment breakdown"],
    notes: ["Focus on changes after pricing update."],
    bookmarks: ["Europe revenue movement"],
    recommendations: ["Compare order volume and complaints by region over the last 6 months."],
    kpis: [
      { id: "k1", label: "Revenue", value: "$4.8M", change: "-6.2%" },
      { id: "k2", label: "Orders", value: "12,940", change: "-3.1%" },
      { id: "k3", label: "Complaints", value: "482", change: "+8.4%" },
    ],
  }
}
