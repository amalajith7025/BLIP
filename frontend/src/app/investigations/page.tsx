import { PageContainer } from "@/components/common/page-container"
import { SectionHeader } from "@/components/common/section-header"

export default function InvestigationsPage() {
  return (
    <PageContainer>
      <SectionHeader
        title="Investigations"
        description="Choose a starting point and keep your work moving with clarity."
      />
      <div className="rounded-xl border border-dashed border-border bg-card p-10 text-center">
        <p className="text-sm text-muted-foreground">Investigation workspace placeholder.</p>
      </div>
    </PageContainer>
  )
}
