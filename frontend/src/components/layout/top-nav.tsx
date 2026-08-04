"use client"

import { Bell, Menu, Search } from "lucide-react"

import { ThemeToggle } from "@/components/layout/theme-toggle"
import { UserProfileMenu } from "@/components/layout/user-profile-menu"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

type TopNavProps = {
  onOpenMobileMenu: () => void
}

export function TopNav({ onOpenMobileMenu }: TopNavProps) {
  return (
    <header className="sticky top-0 z-10 flex h-16 items-center gap-3 border-b border-border bg-background/95 px-4 backdrop-blur sm:px-6">
      <Button variant="ghost" size="icon" onClick={onOpenMobileMenu} className="md:hidden" aria-label="Open sidebar">
        <Menu className="size-5" />
      </Button>

      <div className="relative w-full max-w-xl">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search investigations, reports, data..." className="h-10 pl-9" />
      </div>

      <div className="ml-auto flex items-center gap-1 sm:gap-2">
        <ThemeToggle />
        <Button variant="ghost" size="icon" aria-label="Notifications" className="text-muted-foreground hover:text-foreground">
          <Bell className="size-4" />
        </Button>
        <UserProfileMenu />
      </div>
    </header>
  )
}
