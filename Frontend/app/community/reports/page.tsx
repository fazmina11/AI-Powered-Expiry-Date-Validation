"use client";

import { useState, useEffect } from "react";
import {
  FileText,
  Search,
  Eye,
  Loader2,
  AlertCircle,
  Calendar,
} from "lucide-react";
import Link from "next/link";
import { apiFetch } from "@/services/apiService";

interface ReportImage {
  id: string;
  image_url: string;
}

interface ProductReport {
  id: string;
  user_id: string;
  barcode: string;
  batch_number: string;
  product_name: string;
  report_type: string;
  severity: string;
  description: string;
  status: string;
  created_at: string;
  images: ReportImage[];
}

export default function CommunityReportsPage() {
  const [reports, setReports] = useState<ProductReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeStatusFilter, setActiveStatusFilter] = useState<"ALL" | "PENDING" | "UNDER_REVIEW" | "VERIFIED" | "REJECTED">("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchReports = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const url = activeStatusFilter === "ALL" 
        ? "/community/reports?limit=100" 
        : `/community/reports?status=${activeStatusFilter}&limit=100`;
      
      const res = await apiFetch<{ data: ProductReport[] } | ProductReport[]>(url);
      // Backend standard response standardizer maps lists or envelopes
      const data = Array.isArray(res) ? res : res.data || [];
      setReports(data);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load community reports database.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [activeStatusFilter]);

  const filteredReports = reports.filter((r) => {
    const query = searchQuery.toLowerCase();
    return (
      r.product_name.toLowerCase().includes(query) ||
      r.barcode.toLowerCase().includes(query) ||
      r.batch_number.toLowerCase().includes(query) ||
      r.id.toLowerCase().includes(query)
    );
  });

  return (
    <div className="space-y-8 p-8 max-w-7xl mx-auto">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-950 flex items-center gap-3">
            <FileText className="size-8 text-blue-600" />
            Community Incident Reports
          </h1>
          <p className="text-gray-500 mt-1">
            Browse and inspect crowd-sourced product quality reports submitted by community members.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
          <AlertCircle className="size-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Toolbar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gray-50 p-2 rounded-2xl border border-gray-200/60">
        {/* Tabs */}
        <div className="flex gap-1.5 flex-wrap">
          {[
            { key: "ALL", label: "All Reports" },
            { key: "PENDING", label: "Pending" },
            { key: "UNDER_REVIEW", label: "Under Review" },
            { key: "VERIFIED", label: "Verified" },
            { key: "REJECTED", label: "Rejected" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveStatusFilter(tab.key as any)}
              className={`px-4 py-2 text-xs font-semibold rounded-xl transition-all ${
                activeStatusFilter === tab.key
                  ? "bg-white text-gray-900 shadow-sm border border-gray-200"
                  : "text-gray-500 hover:text-gray-900 hover:bg-white/40"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-2.5 size-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search report details..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-xl text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400 space-y-4">
          <Loader2 className="size-10 animate-spin text-blue-600" />
          <p className="text-sm font-semibold">Retrieving product report logs...</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-55 border-b border-gray-200 text-gray-500 font-bold text-[11px] uppercase tracking-wider">
                <th className="p-4">Report UUID</th>
                <th className="p-4">Product / Barcode</th>
                <th className="p-4">Batch Number</th>
                <th className="p-4">Report Type</th>
                <th className="p-4">Severity</th>
                <th className="p-4">Status</th>
                <th className="p-4">Date Filed</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {filteredReports.length > 0 ? (
                filteredReports.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-55/50">
                    <td className="p-4">
                      <span className="font-mono text-xs font-bold text-gray-600 block max-w-[120px] truncate">
                        {report.id}
                      </span>
                    </td>
                    <td className="p-4">
                      <p className="font-bold text-gray-900 text-sm leading-snug">{report.product_name}</p>
                      <p className="text-xs text-gray-500 font-mono mt-0.5">{report.barcode}</p>
                    </td>
                    <td className="p-4 text-gray-700 font-mono">{report.batch_number}</td>
                    <td className="p-4">
                      <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-semibold border border-slate-200/80">
                        {report.report_type}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase ${
                        report.severity === "CRITICAL" ? "text-red-700 bg-red-50 border border-red-200" :
                        report.severity === "HIGH" ? "text-amber-700 bg-amber-50 border border-amber-200" : "text-blue-700 bg-blue-50 border border-blue-200"
                      }`}>
                        {report.severity}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase ${
                        report.status === "VERIFIED" ? "text-green-700 bg-green-50 border border-green-200" :
                        report.status === "REJECTED" ? "text-red-700 bg-red-50 border border-red-200" : "text-amber-700 bg-amber-50 border border-amber-200"
                      }`}>
                        {report.status}
                      </span>
                    </td>
                    <td className="p-4 text-gray-500 flex items-center gap-1 mt-2.5">
                      <Calendar className="size-3.5" />
                      {new Date(report.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right">
                      <Link
                        href={`/community/reports/${report.id}`}
                        className="p-2 border border-gray-200 hover:bg-gray-55 rounded-xl transition-colors text-blue-600 font-bold text-xs inline-flex items-center gap-1.5 ml-auto"
                      >
                        <Eye className="size-3.5" /> Inspect
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-gray-400">
                    No community reports found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
