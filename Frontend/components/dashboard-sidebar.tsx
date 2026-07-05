"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Home,
  Package,
  Settings,
  LogOut,
  Sparkles,
  ScanLine,
  AlertTriangle,
  Shield,
  FileText,
  ShieldAlert,
  TrendingUp,
  FolderKanban,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";

const sidebarItems = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Inventory", href: "/dashboard/inventory", icon: Package },
  { name: "Scan & Validate", href: "/dashboard/scan", icon: ScanLine },
  { name: "Alerts & Reviews", href: "/dashboard/alerts", icon: AlertTriangle },
  { name: "PGN Admin", href: "/dashboard/community-safety", icon: Shield },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

const communitySafetyItems = [
  { name: "Dashboard", href: "/dashboard/community-safety", icon: Shield },
  { name: "Community Reports", href: "/community/reports", icon: FileText },
  { name: "Issue Clusters", href: "/community/clusters", icon: ShieldAlert },
  { name: "Community Intelligence", href: "/community/intelligence", icon: TrendingUp },
  { name: "Safety Alerts", href: "/community/alerts", icon: AlertTriangle },
  { name: "Investigation Cases", href: "/community/cases", icon: FolderKanban },
];

export function DashboardSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-black text-white flex flex-col z-50">
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="size-10 rounded-lg bg-primary/20 flex items-center justify-center">
            <Sparkles className="size-6 text-primary" />
          </div>
          <span className="text-xl font-bold">Cliste AI</span>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
        <div className="space-y-1">
          {sidebarItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href) && !pathname.startsWith("/community"));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200",
                  isActive
                    ? "bg-white/10 text-white"
                    : "text-white/60 hover:bg-white/5 hover:text-white"
                )}
              >
                <item.icon className="size-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </div>

        <div className="space-y-1">
          <div className="px-4 py-1.5 text-xs font-semibold text-white/40 uppercase">
            Community Safety
          </div>
          {communitySafetyItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard/community-safety" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200",
                  isActive
                    ? "bg-white/10 text-white"
                    : "text-white/60 hover:bg-white/5 hover:text-white"
                )}
              >
                <item.icon className="size-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      <div className="p-4 border-t border-white/10">
        {user && (
          <div className="px-4 py-2 mb-2">
            <div className="text-sm font-medium text-white truncate">{user.name || user.email}</div>
            <div className="text-xs text-white/50 truncate">{user.email}</div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-4 py-3 rounded-lg text-white/60 hover:bg-white/5 hover:text-red-400 transition-all duration-200"
        >
          <LogOut className="size-5" />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
}
