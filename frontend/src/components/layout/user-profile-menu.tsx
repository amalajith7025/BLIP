"use client"

import { ChevronDown, LogOut, Settings, User } from "lucide-react"

import { Button } from "@/components/ui/button"

export function UserProfileMenu() {
  return (
    <details className="relative">
      <summary className="list-none">
        <Button variant="ghost" className="h-9 gap-2 px-2 text-sm text-foreground">
          <span className="flex size-7 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
            BL
          </span>
          <span className="hidden text-left sm:block">
            <span className="block leading-none">BLIP User</span>
            <span className="text-xs text-muted-foreground">Admin</span>
          </span>
          <ChevronDown className="size-4 text-muted-foreground" />
        </Button>
      </summary>
      <div className="absolute right-0 z-20 mt-2 w-52 overflow-hidden rounded-lg border border-border bg-popover shadow-lg">
        <button className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-accent" type="button">
          <User className="size-4" />
          Profile
        </button>
        <button className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-accent" type="button">
          <Settings className="size-4" />
          Preferences
        </button>
        <div className="mx-3 border-t border-border" />
        <button className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-destructive hover:bg-destructive/10" type="button">
          <LogOut className="size-4" />
          Sign Out
        </button>
      </div>
    </details>
  )
}
