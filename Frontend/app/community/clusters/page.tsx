"use client";

import { useState, useEffect } from "react";
import {
  ShieldAlert,
  Loader2,
  AlertTriangle,
  RefreshCw,
  Search,
  Eye,
  Calendar,
  X,
  FileText,
  BadgeAlert,
  CheckCircle2,
} from "lucide-react";
import { apiFetch } from "@/services/apiService";

interface IssueCluster {
  id: string;
  cluster_code: string;
  barcode: string;
  product_name: string;
  batch_number: string;
  issue_type: string;
  severity: string;
  status: string;
  total_reports: number;
  risk_score: number;
  first_reported_at: string;
  last_reported_at: string;
}

interface ProductReport {
  id: string;
  barcode: string;
  batch_number: string;
  product_name: string;
  report_type: string;
  severity: string;
  description: string;
  purchase_date: string | null;
  store_name: string | null;
  store_location: string | null;
  status: string;
  created_at: string;
}

export default function IssueClustersPage() {
  const [clusters, setClusters] = useState<IssueCluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Detailed Modal Selection
  const [selectedCluster, setSelectedCluster] = useState<IssueCluster | null>(null);
  const [clusterReports, setClusterReports] = useState<ProductReport[]>([]);
  const [modalLoading, setModalLoading] = useState(false);

  const fetchClusters = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await apiFetch<{ data: IssueCluster[] } | IssueCluster[]>("/community/clusters?limit=100");
      const data = Array.isArray(res) ? res : res.data || [];
      setClusters(data);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load issue clusters index.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, []);

  const handleRebuildClusters = async () => {
    setRebuilding(true);
    try {
      const res = await apiFetch<{ success: boolean; message: string }>("/community/clusters/recalculate", {
        method: "POST",
      });
      alert(res.message || "Issue clusters index cleared and rebuilt successfully!");
      fetchClusters();
    } catch (err: any) {
      alert("Cluster rebuild failed: " + err.message);
    } finally {
      setRebuilding(false);
    }
  };

  const handleViewClusterReports = async (cluster: IssueCluster) => {
    setSelectedCluster(cluster);
    setClusterReports([]);
    setModalLoading(true);
    try {
      const res = await apiFetch<{ data: ProductReport[] } | ProductReport[]>(`/community/clusters/${cluster.id}/reports`);
      const reportsData = Array.isArray(res) ? res : res.data || [];
      setClusterReports(reportsData);
    } catch (err) {
      console.error("Failed to fetch reports inside cluster:", err);
    } finally {
      setModalLoading(false);
    }
  };

  const filteredClusters = clusters.filter((c) => {
    const query = searchQuery.toLowerCase();
    return (
      c.product_name.toLowerCase().includes(query) ||
      c.barcode.toLowerCase().includes(query) ||
      c.cluster_code.toLowerCase().includes(query) ||
      c.issue_type.toLowerCase().includes(query)
    );
  });

  return (
    <div className="space-y-8 p-8 max-w-7xl mx-auto">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-950 flex items-center gap-3">
            <ShieldAlert className="size-8 text-blue-600" />
            PICE Issue Clusters
          </h1>
          <p className="text-gray-500 mt-1">
            Grouped quality concerns clustered automatically by product barcode, batch identification, and anomaly types.
          </p>
        </div>

        <button
          onClick={handleRebuildClusters}
          disabled={rebuilding || loading}
          className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm flex items-center gap-2 shadow-sm transition-all disabled:opacity-50"
        >
          {rebuilding ? <Loader2 className="size-4 animate-spin" /> : <RefreshCw className="size-4" />}
          Rebuild Issue Clusters
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
          <AlertTriangle className="size-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Toolbar */}
      <div className="flex justify-between items-center bg-gray-55/40 p-2 rounded-2xl border border-gray-200/60">
        <div className="text-xs text-gray-500 font-bold px-3 uppercase tracking-wider">
          Total Clusters Index: {filteredClusters.length}
        </div>

        {/* Search */}
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-2.5 size-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by barcode, cluster code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-xl text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
          />
        </div>
      </div>

      {loading && clusters.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400 space-y-4">
          <Loader2 className="size-10 animate-spin text-blue-600" />
          <p className="text-sm font-semibold">Running issue pattern clustering sweep...</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-gray-500 font-bold text-[11px] uppercase tracking-wider">
                <th className="p-4">Cluster Code</th>
                <th className="p-4">Product Anomaly / Barcode</th>
                <th className="p-4">Batch Number</th>
                <th className="p-4">Incident Type</th>
                <th className="p-4">Severity</th>
                <th className="p-4">Risk Index</th>
                <th className="p-4">Reports Count</th>
                <th className="p-4">Last Activity</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {filteredClusters.length > 0 ? (
                filteredClusters.map((cluster) => (
                  <tr key={cluster.id} className="hover:bg-gray-50/50">
                    <td className="p-4">
                      <span className="font-mono text-xs font-bold text-gray-700">
                        {cluster.cluster_code}
                      </span>
                    </td>
                    <td className="p-4">
                      <p className="font-bold text-gray-900 text-sm leading-snug">{cluster.product_name}</p>
                      <p className="text-xs text-gray-500 font-mono mt-0.5">{cluster.barcode}</p>
                    </td>
                    <td className="p-4 text-gray-700 font-mono">{cluster.batch_number}</td>
                    <td className="p-4">
                      <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-semibold border border-slate-200/80">
                        {cluster.issue_type}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase ${
                        cluster.severity === "CRITICAL" ? "text-red-700 bg-red-50 border border-red-200" :
                        cluster.severity === "HIGH" ? "text-amber-700 bg-amber-50 border border-amber-200" : "text-blue-700 bg-blue-50 border border-blue-200"
                      }`}>
                        {cluster.severity}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className={`font-black ${
                          cluster.risk_score >= 70 ? "text-red-600" :
                          cluster.risk_score >= 50 ? "text-amber-600" : "text-blue-600"
                        }`}>
                          {cluster.risk_score}
                        </span>
                        <div className="w-12 bg-gray-100 h-1.5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              cluster.risk_score >= 70 ? "bg-red-500" :
                              cluster.risk_score >= 50 ? "bg-amber-500" : "bg-blue-500"
                            }`}
                            style={{ width: `${cluster.risk_score}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4 text-gray-900 font-bold">{cluster.total_reports}</td>
                    <td className="p-4 text-gray-500 flex items-center gap-1 mt-2.5">
                      <Calendar className="size-3.5" />
                      {new Date(cluster.last_reported_at).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => handleViewClusterReports(cluster)}
                        className="p-2 border border-gray-200 hover:bg-gray-55 rounded-xl transition-colors text-blue-600 font-bold text-xs inline-flex items-center gap-1.5 ml-auto"
                      >
                        <Eye className="size-3.5" /> Reports Group
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-gray-400">
                    No issue clusters grouped.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Cluster Grouped Reports Drawer / Modal */}
      {selectedCluster && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-2xl max-w-4xl w-full max-h-[85vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <div>
                <h3 className="text-xl font-bold text-gray-950 flex items-center gap-2">
                  <BadgeAlert className="size-5 text-blue-600" />
                  Cluster Array: {selectedCluster.cluster_code}
                </h3>
                <p className="text-xs text-gray-500 mt-1 font-mono">
                  {selectedCluster.product_name} ({selectedCluster.barcode}) — {selectedCluster.batch_number}
                </p>
              </div>
              <button
                onClick={() => setSelectedCluster(null)}
                className="p-1.5 hover:bg-gray-200 rounded-xl text-gray-500 hover:text-gray-900 transition-all"
              >
                <X className="size-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1 bg-white">
              {modalLoading ? (
                <div className="flex flex-col items-center justify-center py-12 text-gray-400 space-y-4">
                  <Loader2 className="size-8 animate-spin text-blue-600" />
                  <p className="text-xs font-semibold">Loading associated incident trails...</p>
                </div>
              ) : clusterReports.length > 0 ? (
                <div className="space-y-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block">
                    Seeded/Linked Consumer Compliant Records
                  </span>
                  <div className="divide-y divide-gray-100 border border-gray-100 rounded-xl overflow-hidden shadow-sm">
                    {clusterReports.map((report) => (
                      <div key={report.id} className="p-4 hover:bg-gray-55/30 transition-all flex flex-col md:flex-row justify-between gap-4">
                        <div className="space-y-2 max-w-2xl">
                          <div className="flex items-center gap-3">
                            <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                              {report.id.substring(0, 8)}...
                            </span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                              report.severity === "CRITICAL" ? "bg-red-50 text-red-700 border border-red-150" : "bg-slate-100 text-slate-700"
                            }`}>
                              {report.severity}
                            </span>
                          </div>
                          <p className="text-xs font-mono text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-200 leading-relaxed">
                            {report.description}
                          </p>
                          <div className="flex items-center gap-4 text-[10px] text-gray-400">
                            <span>Store: {report.store_name || "N/A"} ({report.store_location || "N/A"})</span>
                            <span>Purchase: {report.purchase_date || "N/A"}</span>
                          </div>
                        </div>

                        <div className="flex flex-col justify-between items-end gap-2 shrink-0">
                          <span className="text-xs text-gray-400 flex items-center gap-1">
                            <Calendar className="size-3.5" />
                            {new Date(report.created_at).toLocaleDateString()}
                          </span>
                          <span className={`text-[10px] font-black px-2 py-0.5 rounded-full uppercase ${
                            report.status === "VERIFIED" ? "text-green-700 bg-green-50 border border-green-200" :
                            report.status === "REJECTED" ? "text-red-700 bg-red-50 border border-red-200" : "text-amber-700 bg-amber-50 border border-amber-200"
                          }`}>
                            {report.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-10 text-gray-400 text-sm">No linked incident records found.</div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-100 flex justify-end bg-gray-50">
              <button
                onClick={() => setSelectedCluster(null)}
                className="px-4 py-2 border border-gray-200 hover:bg-gray-100 rounded-xl text-sm font-semibold text-gray-700 transition-colors"
              >
                Close View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
