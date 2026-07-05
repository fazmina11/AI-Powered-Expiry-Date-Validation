"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  FileText,
  ChevronRight,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  RefreshCw,
  Shield,
  SortAsc,
  SortDesc,
  ShieldCheck,
  Package,
} from "lucide-react";
import { apiFetch } from "@/services/apiService";
import { cn } from "@/lib/utils";

// ─── Types ──────────────────────────────────────────────────────────────────

interface ProductReport {
  id: string;
  product_name: string;
  barcode: string;
  batch_number: string;
  report_type: string;
  description: string;
  status: string;
  created_at: string;
  images: { id: string; image_url: string }[];
  store_name: string | null;
}

// ─── Status helpers ──────────────────────────────────────────────────────────

function getStatusConfig(status: string) {
  switch (status) {
    case "PENDING":
      return {
        label: "Submitted",
        color: "bg-gray-100 text-gray-700",
        dot: "bg-gray-500",
        icon: Clock,
        progress: 20,
      };
    case "UNDER_REVIEW":
      return {
        label: "Under Review",
        color: "bg-blue-100 text-blue-700",
        dot: "bg-blue-500",
        icon: Shield,
        progress: 40,
      };
    case "VERIFIED":
      return {
        label: "Investigation Open",
        color: "bg-amber-100 text-amber-700",
        dot: "bg-amber-500",
        icon: AlertTriangle,
        progress: 70,
      };
    case "RESOLVED":
      return {
        label: "Resolved",
        color: "bg-green-100 text-green-700",
        dot: "bg-green-500",
        icon: CheckCircle2,
        progress: 100,
      };
    case "REJECTED":
      return {
        label: "Closed",
        color: "bg-red-100 text-red-700",
        dot: "bg-red-500",
        icon: XCircle,
        progress: 100,
      };
    default:
      return {
        label: status,
        color: "bg-gray-100 text-gray-700",
        dot: "bg-gray-400",
        icon: Clock,
        progress: 10,
      };
  }
}

const ISSUE_TYPE_LABELS: Record<string, string> = {
  LEAKAGE: "Leakage",
  WRONG_PRODUCT: "Wrong Product",
  DAMAGED_PACKAGING: "Damaged Packaging",
  FOREIGN_OBJECT: "Foreign Object",
  EXPIRED_PRODUCT: "Expired Product",
  BAD_SMELL: "Bad Smell",
  CONTAMINATION: "Contamination",
  OTHER: "Other Issue",
};

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function SkeletonCard() {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 animate-pulse">
      <div className="flex justify-between mb-4">
        <div className="h-5 bg-gray-200 rounded w-40" />
        <div className="h-6 bg-gray-200 rounded-full w-24" />
      </div>
      <div className="h-4 bg-gray-200 rounded w-32 mb-3" />
      <div className="h-4 bg-gray-200 rounded w-full mb-2" />
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4" />
      <div className="h-2 bg-gray-200 rounded-full" />
    </div>
  );
}

// ─── Empty State ─────────────────────────────────────────────────────────────

function EmptyState() {
  return (
    <div className="text-center py-20">
      <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
        <FileText className="w-10 h-10 text-blue-300" />
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-2">No reports yet</h3>
      <p className="text-gray-500 mb-8 max-w-xs mx-auto">
        You haven't submitted any product safety reports. Be the first to help your community!
      </p>
      <Link
        href="/community/report"
        className="inline-flex items-center gap-2 px-8 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all"
      >
        <Shield className="w-5 h-5" />
        Report a Product
      </Link>
    </div>
  );
}

// ─── Report Card ─────────────────────────────────────────────────────────────

function ReportCard({ report }: { report: ProductReport }) {
  const statusConfig = getStatusConfig(report.status);
  const StatusIcon = statusConfig.icon;

  return (
    <Link href={`/community/my-reports/${report.id}`}>
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-start gap-3 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition-colors">
              <Package className="w-5 h-5 text-blue-600" />
            </div>
            <div className="min-w-0">
              <h3 className="font-semibold text-gray-900 truncate group-hover:text-blue-700 transition-colors">
                {report.product_name}
              </h3>
              <p className="text-xs text-gray-400 font-mono mt-0.5">
                {report.barcode}
              </p>
            </div>
          </div>

          <span className={cn(
            "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold flex-shrink-0",
            statusConfig.color
          )}>
            <span className={cn("w-1.5 h-1.5 rounded-full", statusConfig.dot)} />
            {statusConfig.label}
          </span>
        </div>

        {/* Issue Type + Date */}
        <div className="flex items-center gap-3 mb-3">
          <span className="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-lg font-medium">
            {ISSUE_TYPE_LABELS[report.report_type] || report.report_type}
          </span>
          <span className="text-xs text-gray-400">
            {new Date(report.created_at).toLocaleDateString("en-IN", {
              day: "numeric", month: "short", year: "numeric"
            })}
          </span>
          {report.images.length > 0 && (
            <span className="text-xs text-violet-500 font-medium">
              📷 {report.images.length} photo{report.images.length > 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* Description Preview */}
        <p className="text-sm text-gray-500 line-clamp-2 mb-4 leading-relaxed">
          {report.description}
        </p>

        {/* Progress Bar */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center gap-1.5">
              <StatusIcon className="w-3.5 h-3.5 text-gray-400" />
              <span className="text-xs text-gray-400">Progress</span>
            </div>
            <span className="text-xs font-medium text-gray-600">{statusConfig.progress}%</span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all",
                report.status === "RESOLVED" ? "bg-green-500" :
                report.status === "REJECTED" ? "bg-red-400" :
                report.status === "VERIFIED" ? "bg-amber-500" :
                report.status === "UNDER_REVIEW" ? "bg-blue-500" : "bg-gray-400"
              )}
              style={{ width: `${statusConfig.progress}%` }}
            />
          </div>
        </div>

        {/* Footer CTA */}
        <div className="flex items-center justify-end mt-3 gap-1 text-blue-600 group-hover:text-blue-700">
          <span className="text-sm font-medium">View Details</span>
          <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </Link>
  );
}

// ─── Main My Reports Page ─────────────────────────────────────────────────────

export default function MyReportsPage() {
  const [reports, setReports] = useState<ProductReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [sortOrder, setSortOrder] = useState<"newest" | "oldest">("newest");

  const loadReports = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch all reports from API
      const res = await apiFetch<any>("/community/reports?limit=100");
      const list: ProductReport[] = Array.isArray(res) ? res : (res.data || []);

      // Cross-reference with locally-stored report IDs to show user's reports
      const myIds: string[] = JSON.parse(localStorage.getItem("my_report_ids") || "[]");

      // Show user's own reports if any are tracked; otherwise show all (for demo)
      let filtered = myIds.length > 0
        ? list.filter((r) => myIds.includes(r.id))
        : list;

      setReports(filtered);
    } catch (e: any) {
      setError("We couldn't load your reports. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  // ── Filter & Search ──────────────────────────────────────────────────────────

  const filteredReports = reports
    .filter((r) => {
      const q = searchQuery.toLowerCase();
      const matchesSearch =
        !q ||
        r.product_name.toLowerCase().includes(q) ||
        r.barcode.toLowerCase().includes(q) ||
        r.description.toLowerCase().includes(q);
      const matchesStatus = statusFilter === "ALL" || r.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      const aTime = new Date(a.created_at).getTime();
      const bTime = new Date(b.created_at).getTime();
      return sortOrder === "newest" ? bTime - aTime : aTime - bTime;
    });

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="py-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">My Reports</h1>
          <p className="text-gray-500 mt-1">
            Track all your submitted product safety reports
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadReports}
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-200 hover:border-blue-300 rounded-xl text-sm font-medium text-gray-600 hover:text-blue-700 transition-all"
          >
            <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
            Refresh
          </button>
          <Link
            href="/community/report"
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-xl shadow-sm transition-all"
          >
            <Shield className="w-4 h-4" />
            New Report
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by product name, barcode…"
            className="w-full pl-10 pr-4 py-3 bg-white border border-gray-200 hover:border-blue-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 rounded-xl text-sm placeholder-gray-400 text-gray-900 transition-all outline-none"
          />
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-4 h-4 text-gray-400 flex-shrink-0" />
          {[
            { value: "ALL", label: "All" },
            { value: "PENDING", label: "Submitted" },
            { value: "UNDER_REVIEW", label: "Under Review" },
            { value: "VERIFIED", label: "Investigation" },
            { value: "RESOLVED", label: "Resolved" },
            { value: "REJECTED", label: "Closed" },
          ].map((f) => (
            <button
              key={f.value}
              onClick={() => setStatusFilter(f.value)}
              className={cn(
                "px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all",
                statusFilter === f.value
                  ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                  : "bg-white text-gray-600 border-gray-200 hover:border-blue-300"
              )}
            >
              {f.label}
            </button>
          ))}

          {/* Sort toggle */}
          <button
            onClick={() => setSortOrder((o) => (o === "newest" ? "oldest" : "newest"))}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border border-gray-200 bg-white text-gray-600 hover:border-blue-300 transition-all"
          >
            {sortOrder === "newest" ? (
              <><SortDesc className="w-3.5 h-3.5" />Newest</>
            ) : (
              <><SortAsc className="w-3.5 h-3.5" />Oldest</>
            )}
          </button>
        </div>
      </div>

      {/* Summary chips */}
      {!loading && reports.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6">
          {[
            { status: "PENDING", label: "Submitted", color: "bg-gray-100 text-gray-600" },
            { status: "UNDER_REVIEW", label: "Under Review", color: "bg-blue-100 text-blue-700" },
            { status: "VERIFIED", label: "Investigation", color: "bg-amber-100 text-amber-700" },
            { status: "RESOLVED", label: "Resolved", color: "bg-green-100 text-green-700" },
            { status: "REJECTED", label: "Closed", color: "bg-red-100 text-red-700" },
          ].map(({ status, label, color }) => {
            const count = reports.filter((r) => r.status === status).length;
            if (count === 0) return null;
            return (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={cn("px-3 py-1 rounded-full text-xs font-medium transition-all", color)}
              >
                {count} {label}
              </button>
            );
          })}
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-50 text-gray-500 border border-gray-200">
            {reports.length} total
          </span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-5 flex gap-3 mb-6">
          <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-700">Failed to load reports</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
            <button onClick={loadReports} className="mt-2 text-sm font-medium text-red-600 underline">Try again</button>
          </div>
        </div>
      )}

      {/* Reports List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
        </div>
      ) : filteredReports.length === 0 ? (
        reports.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
            <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-700 mb-2">No reports match your filters</h3>
            <p className="text-gray-400 text-sm mb-4">Try adjusting your search or filter criteria</p>
            <button
              onClick={() => { setSearchQuery(""); setStatusFilter("ALL"); }}
              className="text-blue-600 text-sm font-medium underline"
            >
              Clear all filters
            </button>
          </div>
        )
      ) : (
        <div className="space-y-4">
          {filteredReports.map((report) => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="flex justify-center py-8">
          <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
        </div>
      )}
    </div>
  );
}
