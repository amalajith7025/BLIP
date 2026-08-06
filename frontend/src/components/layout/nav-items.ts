import {
  BookMarked,
  BarChart3,
  Home,
  Search,
  Settings,
  type LucideIcon,
} from "lucide-react"

export type NavItem = {
  label: string
  href: string
  icon: LucideIcon
}

export const navItems: NavItem[] = [
  { label: "Home", href: "/", icon: Home },
  { label: "Investigations", href: "/investigations/workspace", icon: Search },
  { label: "Reports", href: "/reports", icon: BarChart3 },
  { label: "Library", href: "/library", icon: BookMarked },
  { label: "Settings", href: "/settings", icon: Settings },
]
