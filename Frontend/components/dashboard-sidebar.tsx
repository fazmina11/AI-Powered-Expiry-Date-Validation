"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Package, Settings, LogOut, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const sidebarItems = [
  { name: "Home", href: "/dashboard", icon: Home },
  { name: "Inventory", href: "/dashboard/inventory", icon: Package },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-black text-white flex flex-col z-50">
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="size-10 rounded-lg bg-primary/20 flex items-center justify-center">
            <Sparkles className="size-6 text-primary" />
          </div>
          <span className="text-xl font-bold">YourBrand</span>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {sidebarItems.map((item) => {
          const isActive = pathname === item.href;
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
      </nav>

      <div className="p-4 border-t border-white/10">
        <button className="flex items-center gap-3 w-full px-4 py-3 rounded-lg text-white/60 hover:bg-white/5 hover:text-white transition-all duration-200">
          <LogOut className="size-5" />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
}
