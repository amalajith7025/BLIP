"use client"

import { useState } from "react"

import { Sidebar } from "@/components/layout/sidebar"
import { ThemeProvider } from "@/components/layout/theme-provider"
import { TopNav } from "@/components/layout/top-nav"
import { cn } from "@/lib/utils"

type AppShellProps = {
  children: React.ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)

  return (
    <ThemeProvider>
      <div className="flex min-h-screen bg-muted/30">
        <div className="hidden md:block">
          <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />
        </div>

        <div
          className={cn(
            "fixed inset-0 z-40 bg-black/30 transition-opacity md:hidden",
            mobileSidebarOpen ? "opacity-100" : "pointer-events-none opacity-0"
          )}
          onClick={() => setMobileSidebarOpen(false)}
          aria-hidden="true"
        />
        <div
          className={cn(
            "fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-200 md:hidden",
            mobileSidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <Sidebar
            collapsed={false}
            onToggle={() => setMobileSidebarOpen(false)}
            onNavigate={() => setMobileSidebarOpen(false)}
          />
        </div>

        <div className="flex min-h-screen flex-1 flex-col">
          <TopNav onOpenMobileMenu={() => setMobileSidebarOpen(true)} />
          <main className="flex-1">{children}</main>
        </div>
      </div>
    </ThemeProvider>
  )
}
