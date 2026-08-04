import { PageContainer } from "@/components/common/page-container"
import { SectionHeader } from "@/components/common/section-header"

export default function LibraryPage() {
  return (
    <PageContainer>
      <SectionHeader
        title="Library"
        description="Find saved resources and keep your team aligned."
      />
      <div className="rounded-xl border border-dashed border-border bg-card p-10 text-center">
        <p className="text-sm text-muted-foreground">Library placeholder content.</p>
      </div>
    </PageContainer>
  )
}
