"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { ChevronsLeftRight } from "lucide-react"

import { navItems } from "@/components/layout/nav-items"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type SidebarProps = {
  collapsed: boolean
  onToggle: () => void
  onNavigate?: () => void
}

export function Sidebar({ collapsed, onToggle, onNavigate }: SidebarProps) {
  const pathname = usePathname()

  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r border-border bg-sidebar transition-all duration-200",
        collapsed ? "w-20" : "w-64"
      )}
    >
      <div className="flex h-16 items-center justify-between border-b border-sidebar-border px-3">
        <div className="flex items-center gap-2 overflow-hidden">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-sm font-semibold text-primary-foreground">
            B
          </div>
          {!collapsed ? <span className="truncate text-sm font-semibold tracking-wide">BLIP Platform</span> : null}
        </div>
        <Button variant="ghost" size="icon" onClick={onToggle} aria-label="Collapse sidebar" className="hidden md:inline-flex">
          <ChevronsLeftRight className="size-4" />
        </Button>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const active = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex h-10 items-center rounded-lg px-3 text-sm transition-colors",
                collapsed ? "justify-center" : "gap-3",
                active
                  ? "bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
              title={collapsed ? item.label : undefined}
            >
              <Icon className="size-4 shrink-0" />
              {!collapsed ? <span>{item.label}</span> : null}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
