import { PageContainer } from "@/components/common/page-container"
import { SectionHeader } from "@/components/common/section-header"

export default function ReportsPage() {
  return (
    <PageContainer>
      <SectionHeader title="Reports" description="Generate and review business intelligence reports." />
      <div className="rounded-xl border border-dashed border-border bg-card p-10 text-center">
        <p className="text-sm text-muted-foreground">Reports content placeholder.</p>
      </div>
    </PageContainer>
  )
}
