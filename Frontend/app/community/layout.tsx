"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, Home, FileText, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { DashboardSidebar } from "@/components/dashboard-sidebar";

export default function CommunityLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  // Determine if this is an admin route
  const isAdminPath =
    pathname.startsWith("/community/reports") ||
    pathname.startsWith("/community/clusters") ||
    pathname.startsWith("/community/intelligence") ||
    pathname.startsWith("/community/alerts") ||
    pathname.startsWith("/community/cases");

  if (isAdminPath) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <DashboardSidebar />
        <main className="ml-64 flex-1 min-h-screen bg-white text-gray-900">
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: "linear-gradient(135deg, #f0f4ff 0%, #e8f5e9 50%, #f0f7ff 100%)" }}>
      {/* Top Nav */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-blue-100 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <Link href="/community" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-gray-900 text-sm leading-tight block">Community Safety</span>
              <span className="text-xs text-blue-600 leading-tight block">Product Guardian Network</span>
            </div>
          </Link>

          <nav className="hidden sm:flex items-center gap-1">
            <Link
              href="/community"
              className={cn(
                "flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all",
                pathname === "/community"
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <Home className="w-4 h-4" />
              Home
            </Link>
            <Link
              href="/community/my-reports"
              className={cn(
                "flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all",
                pathname.startsWith("/community/my-reports")
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <FileText className="w-4 h-4" />
              My Reports
            </Link>
          </nav>

          <Link
            href="/community/report"
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-all shadow-md hover:shadow-lg active:scale-95"
          >
            <span>+ Report Product</span>
          </Link>
        </div>
      </header>

      {/* Breadcrumb for sub-pages */}
      {pathname !== "/community" && (
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3">
          <nav className="flex items-center gap-1 text-sm text-gray-500">
            <Link href="/community" className="hover:text-blue-600 transition-colors">Home</Link>
            {pathname.startsWith("/community/report") && (
              <>
                <ChevronRight className="w-3 h-3" />
                <span className="text-gray-900 font-medium">Report a Product</span>
              </>
            )}
            {pathname.startsWith("/community/my-reports/") && (
              <>
                <ChevronRight className="w-3 h-3" />
                <Link href="/community/my-reports" className="hover:text-blue-600 transition-colors">My Reports</Link>
                <ChevronRight className="w-3 h-3" />
                <span className="text-gray-900 font-medium">Report Details</span>
              </>
            )}
            {pathname === "/community/my-reports" && (
              <>
                <ChevronRight className="w-3 h-3" />
                <span className="text-gray-900 font-medium">My Reports</span>
              </>
            )}
          </nav>
        </div>
      )}

      <main className="max-w-6xl mx-auto px-4 sm:px-6 pb-16">
        {children}
      </main>

      {/* Mobile Nav */}
      <div className="sm:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2 z-50">
        <div className="flex justify-around">
          <Link href="/community" className={cn("flex flex-col items-center gap-0.5 p-2 rounded-lg", pathname === "/community" ? "text-blue-600" : "text-gray-500")}>
            <Home className="w-5 h-5" />
            <span className="text-xs font-medium">Home</span>
          </Link>
          <Link href="/community/report" className="flex flex-col items-center gap-0.5 p-2 rounded-xl bg-blue-600 text-white -mt-5 shadow-lg px-5">
            <Shield className="w-5 h-5" />
            <span className="text-xs font-medium">Report</span>
          </Link>
          <Link href="/community/my-reports" className={cn("flex flex-col items-center gap-0.5 p-2 rounded-lg", pathname.startsWith("/community/my-reports") ? "text-blue-600" : "text-gray-500")}>
            <FileText className="w-5 h-5" />
            <span className="text-xs font-medium">My Reports</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
