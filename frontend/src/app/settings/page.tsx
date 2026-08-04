import { PageContainer } from "@/components/common/page-container"
import { SectionHeader } from "@/components/common/section-header"

export default function SettingsPage() {
  return (
    <PageContainer>
      <SectionHeader title="Settings" description="Configure organization and platform preferences." />
      <div className="rounded-xl border border-dashed border-border bg-card p-10 text-center">
        <p className="text-sm text-muted-foreground">Settings content placeholder.</p>
      </div>
    </PageContainer>
  )
}
