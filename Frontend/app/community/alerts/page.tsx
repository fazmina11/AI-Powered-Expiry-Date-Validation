"use client";

import { useState, useEffect } from "react";
import {
  AlertTriangle,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Calendar,
  X,
  FileText,
  BadgeAlert,
  Search,
  Eye,
  Settings,
  Shield,
  FolderKanban,
  Hammer,
} from "lucide-react";
import { apiFetch } from "@/services/apiService";

interface SafetyAlert {
  id: string;
  alert_code: string;
  cluster_id: string;
  alert_level: string;
  risk_score: number;
  status: string;
  message: string;
  created_at: string;
  resolved_at: string | null;
}

export default function SafetyAlertsPage() {
  const [alerts, setAlerts] = useState<SafetyAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeTabFilter, setActiveTabFilter] = useState<"ALL" | "ACTIVE" | "ACKNOWLEDGED" | "RESOLVED" | "CLOSED">("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  // Resolving modal states
  const [selectedAlertToResolve, setSelectedAlertToResolve] = useState<SafetyAlert | null>(null);
  const [resolveRemarks, setResolveRemarks] = useState("");

  // Create case modal states
  const [selectedAlertToCase, setSelectedAlertToCase] = useState<SafetyAlert | null>(null);
  const [caseTitle, setCaseTitle] = useState("");
  const [caseDesc, setCaseDesc] = useState("");
  const [casePriority, setCasePriority] = useState("MEDIUM");

  const fetchAlerts = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      let url = "/community/alerts?limit=100";
      if (activeTabFilter !== "ALL") {
        url = `/community/alerts?status=${activeTabFilter}&limit=100`;
      }
      const res = await apiFetch<{ data: SafetyAlert[] }>(url);
      setAlerts(Array.isArray(res) ? res : (res.data || []));
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load safety alerts database.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [activeTabFilter]);

  const handleAcknowledgeAlert = async (alertId: string) => {
    setActionLoading(true);
    try {
      await apiFetch<any>(`/community/alerts/${alertId}/acknowledge`, { method: "PATCH" });
      alert("Alert successfully acknowledged and logged!");
      fetchAlerts();
    } catch (err: any) {
      alert("Acknowledge action failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolveAlert = async () => {
    if (!selectedAlertToResolve) return;
    if (!resolveRemarks) {
      alert("Please provide detailed resolution remarks.");
      return;
    }
    setActionLoading(true);
    try {
      await apiFetch<any>(`/community/alerts/${selectedAlertToResolve.id}/resolve?remarks=${encodeURIComponent(resolveRemarks)}`, {
        method: "PATCH",
      });
      alert("Alert marked as resolved and threat logs archived.");
      setSelectedAlertToResolve(null);
      setResolveRemarks("");
      fetchAlerts();
    } catch (err: any) {
      alert("Resolve action failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateCase = async () => {
    if (!selectedAlertToCase) return;
    if (!caseTitle || !caseDesc) {
      alert("Provide a case title and investigative description.");
      return;
    }
    setActionLoading(true);
    try {
      await apiFetch<any>("/community/cases", {
        method: "POST",
        body: JSON.stringify({
          alert_id: selectedAlertToCase.id,
          title: caseTitle,
          description: caseDesc,
          priority: casePriority,
          due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        }),
      });
      alert("Investigation case successfully launched under ICME!");
      setSelectedAlertToCase(null);
      setCaseTitle("");
      setCaseDesc("");
      fetchAlerts();
    } catch (err: any) {
      alert("Failed to spin up case: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const openCreateCaseModal = (alertObj: SafetyAlert) => {
    setSelectedAlertToCase(alertObj);
    setCaseTitle(`Investigation Case: ${alertObj.alert_code}`);
    setCaseDesc(alertObj.message);
    setCasePriority(alertObj.alert_level === "CRITICAL" ? "CRITICAL" : "HIGH");
  };

  const filteredAlerts = alerts.filter((a) => {
    const query = searchQuery.toLowerCase();
    return (
      a.alert_code.toLowerCase().includes(query) ||
      a.message.toLowerCase().includes(query) ||
      a.alert_level.toLowerCase().includes(query)
    );
  });

  return (
    <div className="space-y-8 p-8 max-w-7xl mx-auto">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-950 flex items-center gap-3">
            <AlertTriangle className="size-8 text-blue-600" />
            CSAE Safety Alerts
          </h1>
          <p className="text-gray-500 mt-1">
            System warnings and broadcasts triggered automatically by high-risk customer quality anomaly trends.
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
            { key: "ALL", label: "All Alerts" },
            { key: "ACTIVE", label: "Active" },
            { key: "ACKNOWLEDGED", label: "Acknowledged" },
            { key: "RESOLVED", label: "Resolved" },
            { key: "CLOSED", label: "Closed" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTabFilter(tab.key as any)}
              className={`px-4 py-2 text-xs font-semibold rounded-xl transition-all ${
                activeTabFilter === tab.key
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
            placeholder="Search alerts code, message..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-xl text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
          />
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400 space-y-4">
          <Loader2 className="size-10 animate-spin text-blue-600" />
          <p className="text-sm font-semibold">Running safety alert diagnostics...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredAlerts.length > 0 ? (
            filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className="bg-white border border-gray-200/80 p-6 rounded-2xl shadow-sm flex flex-col justify-between hover:shadow-md transition-all gap-4"
              >
                <div>
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-xs font-black text-gray-700 bg-gray-50 border border-gray-150 px-2 py-0.5 rounded">
                      {alert.alert_code}
                    </span>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase border ${
                      alert.alert_level === "CRITICAL" ? "text-red-700 bg-red-50 border-red-200" :
                      alert.alert_level === "HIGH_RISK" ? "text-amber-700 bg-amber-50 border-amber-200" : "text-blue-700 bg-blue-50 border-blue-200"
                    }`}>
                      {alert.alert_level}
                    </span>
                  </div>

                  <p className="text-sm text-gray-800 font-semibold mt-4 leading-relaxed">{alert.message}</p>

                  <div className="mt-4 flex items-center justify-between text-xs text-gray-400 font-medium font-mono">
                    <span>Risk score: {alert.risk_score} CIE</span>
                    <span className="flex items-center gap-1">
                      <Calendar className="size-3.5" />
                      {new Date(alert.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="border-t border-gray-100 pt-4 flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-2">
                  <span className={`text-[10px] font-black uppercase text-center sm:text-left ${
                    alert.status === "ACTIVE" ? "text-red-600 bg-red-50 border border-red-100 px-2 py-0.5 rounded-full" :
                    alert.status === "RESOLVED" ? "text-green-600 bg-green-50 border border-green-100 px-2 py-0.5 rounded-full" : "text-gray-500 bg-gray-50 px-2 py-0.5 rounded-full"
                  }`}>
                    {alert.status}
                  </span>

                  <div className="flex gap-2 justify-end">
                    {alert.status === "ACTIVE" && (
                      <button
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                        disabled={actionLoading}
                        className="px-3 py-1.5 border border-gray-200 hover:bg-gray-50 text-gray-700 font-bold text-xs rounded-xl transition-all"
                      >
                        Acknowledge
                      </button>
                    )}

                    {(alert.status === "ACTIVE" || alert.status === "ACKNOWLEDGED") && (
                      <>
                        <button
                          onClick={() => setSelectedAlertToResolve(alert)}
                          className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white font-bold text-xs rounded-xl transition-all shadow-sm"
                        >
                          Resolve
                        </button>
                        <button
                          onClick={() => openCreateCaseModal(alert)}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl transition-all shadow-sm flex items-center gap-1"
                        >
                          <FolderKanban className="size-3.5" />
                          Launch Case
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-2 text-center py-12 text-gray-400 bg-white border border-gray-200 rounded-2xl shadow-sm">
              No safety alerts logged.
            </div>
          )}
        </div>
      )}

      {/* Modal: Resolve Remarks */}
      {selectedAlertToResolve && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex justify-between items-start border-b border-gray-100 pb-3">
              <h3 className="text-lg font-bold text-gray-950 flex items-center gap-2">
                <CheckCircle2 className="size-5 text-green-600" />
                Resolve Alert: {selectedAlertToResolve.alert_code}
              </h3>
              <button onClick={() => setSelectedAlertToResolve(null)} className="p-1 hover:bg-gray-100 rounded-lg text-gray-400">
                <X className="size-5" />
              </button>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Resolution Remarks</label>
              <textarea
                rows={4}
                value={resolveRemarks}
                onChange={(e) => setResolveRemarks(e.target.value)}
                placeholder="Detail what corrective action has been performed to isolate / resolve this concern..."
                className="w-full p-3 border border-gray-200 rounded-xl text-xs bg-white text-gray-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
              ></textarea>
            </div>

            <div className="flex justify-end gap-2 border-t border-gray-100 pt-3">
              <button
                onClick={() => setSelectedAlertToResolve(null)}
                className="px-4 py-2 border border-gray-200 hover:bg-gray-100 rounded-xl text-xs font-semibold text-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={handleResolveAlert}
                disabled={actionLoading}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-bold text-xs rounded-xl shadow-sm"
              >
                {actionLoading ? <Loader2 className="size-3.5 animate-spin" /> : "Confirm Resolution"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Create Investigation Case */}
      {selectedAlertToCase && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-2xl max-w-lg w-full p-6 space-y-6">
            <div className="flex justify-between items-start border-b border-gray-100 pb-3">
              <h3 className="text-lg font-bold text-gray-950 flex items-center gap-2">
                <FolderKanban className="size-5 text-blue-600" />
                Launch Investigation Case
              </h3>
              <button onClick={() => setSelectedAlertToCase(null)} className="p-1 hover:bg-gray-100 rounded-lg text-gray-400">
                <X className="size-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Case Folder Title</label>
                <input
                  type="text"
                  value={caseTitle}
                  onChange={(e) => setCaseTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Investigation Mission / Context</label>
                <textarea
                  rows={4}
                  value={caseDesc}
                  onChange={(e) => setCaseDesc(e.target.value)}
                  className="w-full p-3 border border-gray-200 rounded-xl text-xs bg-white text-gray-900"
                ></textarea>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Alert Code Reference</label>
                  <input
                    type="text"
                    disabled
                    value={selectedAlertToCase.alert_code}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-gray-50 text-gray-500 font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Priority Level</label>
                  <select
                    value={casePriority}
                    onChange={(e) => setCasePriority(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900 focus:outline-none"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 border-t border-gray-100 pt-3">
              <button
                onClick={() => setSelectedAlertToCase(null)}
                className="px-4 py-2 border border-gray-200 hover:bg-gray-100 rounded-xl text-xs font-semibold text-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateCase}
                disabled={actionLoading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm"
              >
                {actionLoading ? <Loader2 className="size-3.5 animate-spin" /> : "Deploy Investigation Task"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
