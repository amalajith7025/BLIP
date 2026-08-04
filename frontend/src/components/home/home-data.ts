export type ContinueInvestigation = {
  title: string
  context: string
  updatedAt: string
}

export type PinnedItem = {
  id: string
  title: string
  subtitle: string
}

export type RecentInvestigation = {
  id: string
  title: string
  status: string
  updatedAt: string
}

export const continueInvestigation: ContinueInvestigation = {
  title: "Q3 Revenue Variance Review",
  context: "North America and Europe performance",
  updatedAt: "Updated 2 hours ago",
}

export const pinnedItems: PinnedItem[] = [
  {
    id: "pin-1",
    title: "Monthly Leadership Report",
    subtitle: "Pinned by Operations",
  },
  {
    id: "pin-2",
    title: "Customer Churn Signals",
    subtitle: "Pinned by Commercial Team",
  },
  {
    id: "pin-3",
    title: "Supply Chain Snapshot",
    subtitle: "Pinned by Strategy",
  },
]

export const recentInvestigations: RecentInvestigation[] = [
  {
    id: "inv-1",
    title: "Pricing Changes by Segment",
    status: "In progress",
    updatedAt: "Today",
  },
  {
    id: "inv-2",
    title: "Customer Expansion Opportunities",
    status: "Ready to review",
    updatedAt: "Yesterday",
  },
  {
    id: "inv-3",
    title: "Cost Movement by Region",
    status: "In progress",
    updatedAt: "2 days ago",
  },
]
