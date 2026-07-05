"use client";

import { useState, useEffect } from "react";
import {
  FolderKanban,
  Search,
  Eye,
  Loader2,
  AlertCircle,
  Calendar,
  User,
} from "lucide-react";
import Link from "next/link";
import { apiFetch } from "@/services/apiService";

interface InvestigationCase {
  id: string;
  case_number: string;
  alert_id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  assigned_officer: string | null;
  opened_at: string;
  created_at: string;
}

export default function InvestigationCasesPage() {
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeStatusFilter, setActiveStatusFilter] = useState<"ALL" | "OPEN" | "UNDER_INVESTIGATION" | "RESOLVED" | "CLOSED">("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchCases = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      let url = "/community/cases?limit=100";
      if (activeStatusFilter !== "ALL") {
        url = `/community/cases?status=${activeStatusFilter}&limit=100`;
      }
      const res = await apiFetch<{ data: InvestigationCase[] } | InvestigationCase[]>(url);
      setCases(Array.isArray(res) ? res : ((res as any).data || []));
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load investigation cases database.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [activeStatusFilter]);

  const filteredCases = cases.filter((c) => {
    const query = searchQuery.toLowerCase();
    return (
      c.title.toLowerCase().includes(query) ||
      c.case_number.toLowerCase().includes(query) ||
      c.priority.toLowerCase().includes(query) ||
      (c.assigned_officer && c.assigned_officer.toLowerCase().includes(query))
    );
  });

  return (
    <div className="space-y-8 p-8 max-w-7xl mx-auto">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-950 flex items-center gap-3">
            <FolderKanban className="size-8 text-blue-600" />
            ICME Investigation Cases
          </h1>
          <p className="text-gray-500 mt-1">
            Track active investigative cases, assign officers, capture evidence trails, and coordinate safety reviews.
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
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gray-55/40 p-2 rounded-2xl border border-gray-200/60">
        {/* Tabs */}
        <div className="flex gap-1.5 flex-wrap">
          {[
            { key: "ALL", label: "All Cases" },
            { key: "OPEN", label: "Open" },
            { key: "UNDER_INVESTIGATION", label: "Under Investigation" },
            { key: "RESOLVED", label: "Resolved" },
            { key: "CLOSED", label: "Closed" },
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
            placeholder="Search cases, officers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-xl text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400 space-y-4">
          <Loader2 className="size-10 animate-spin text-blue-600" />
          <p className="text-sm font-semibold">Opening active investigation folders...</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-gray-500 font-bold text-[11px] uppercase tracking-wider">
                <th className="p-4">Case Code</th>
                <th className="p-4">Case Mission Title</th>
                <th className="p-4">Priority</th>
                <th className="p-4">Status</th>
                <th className="p-4">Assigned Officer</th>
                <th className="p-4">Date Deployed</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {filteredCases.length > 0 ? (
                filteredCases.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50/50">
                    <td className="p-4">
                      <span className="font-mono text-xs font-bold text-gray-700">
                        {c.case_number}
                      </span>
                    </td>
                    <td className="p-4">
                      <p className="font-bold text-gray-900 text-sm leading-snug">{c.title}</p>
                      <p className="text-xs text-gray-400 line-clamp-1 mt-0.5 max-w-sm">{c.description}</p>
                    </td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase border ${
                        c.priority === "CRITICAL" ? "text-red-700 bg-red-50 border-red-200" :
                        c.priority === "HIGH" ? "text-amber-700 bg-amber-50 border-amber-200" : "text-blue-700 bg-blue-50 border-blue-200"
                      }`}>
                        {c.priority}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase border ${
                        c.status === "RESOLVED" ? "text-green-700 bg-green-50 border-green-200" :
                        c.status === "CLOSED" ? "text-slate-700 bg-slate-50 border-slate-200" :
                        c.status === "ASSIGNED" ? "text-violet-700 bg-violet-50 border-violet-200" : "text-amber-700 bg-amber-50 border-amber-200"
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-4 text-gray-700">
                      {c.assigned_officer ? (
                        <span className="flex items-center gap-1">
                          <User className="size-3.5 text-gray-400" />
                          {c.assigned_officer}
                        </span>
                      ) : (
                        <span className="text-gray-400 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="p-4 text-gray-500 flex items-center gap-1 mt-2.5">
                      <Calendar className="size-3.5" />
                      {new Date(c.opened_at || c.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right">
                      <Link
                        href={`/community/cases/${c.id}`}
                        className="p-2 border border-gray-200 hover:bg-gray-55 rounded-xl transition-colors text-blue-600 font-bold text-xs inline-flex items-center gap-1.5 ml-auto"
                      >
                        <Eye className="size-3.5" /> Inspect Folder
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-gray-400">
                    No investigation cases registered.
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
