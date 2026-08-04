import { PageContainer } from "@/components/common/page-container"
import { ContinueInvestigationCard } from "@/components/home/continue-investigation-card"
import {
  continueInvestigation,
  pinnedItems,
  recentInvestigations,
} from "@/components/home/home-data"
import { HomeHero } from "@/components/home/home-hero"
import { PinnedItemsSection } from "@/components/home/pinned-items-section"
import { RecentInvestigationsSection } from "@/components/home/recent-investigations-section"

export function HomeExperience() {
  return (
    <PageContainer className="py-4 sm:py-5 md:h-[calc(100vh-4rem)] md:overflow-hidden">
      <div className="grid h-full gap-4 md:grid-rows-[auto_auto_1fr]">
        <HomeHero />
        <ContinueInvestigationCard item={continueInvestigation} />
        <div className="grid gap-4 lg:grid-cols-2">
          <PinnedItemsSection items={pinnedItems} />
          <RecentInvestigationsSection items={recentInvestigations} />
        </div>
      </div>
    </PageContainer>
  )
}
