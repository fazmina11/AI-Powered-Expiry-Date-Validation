"use client";

import { useState, useEffect } from "react";
import {
  TrendingUp,
  Shield,
  ShieldAlert,
  Loader2,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  RefreshCw,
  Database,
  Search,
  Sparkles,
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

interface ClusterIntelligence {
  id: string;
  cluster_id: string;
  risk_score: number;
  growth_rate: number;
  activity_level: string;
  trend: string;
  spread_level: string;
  escalation_level: string;
  reports_last_24h: number;
  reports_last_7_days: number;
  reports_last_30_days: number;
  new_cities: number;
  average_credibility: number;
  is_trending: boolean;
  last_calculated: string;
  cluster?: IssueCluster;
}

interface ProductReport {
  barcode: string;
  batch_number: string;
  product_name: string;
}

interface ClusterDashboardResponse {
  highest_risk: IssueCluster | null;
  fastest_growing: IssueCluster | null;
  most_active: IssueCluster | null;
  newest_cluster: IssueCluster | null;
  dormant_clusters: IssueCluster[];
}

type ProductNameMap = Record<string, string>;

const unwrapArray = <T,>(raw: T[] | { data: T[] } | null | undefined): T[] => {
  if (Array.isArray(raw)) return raw;
  if (Array.isArray(raw?.data)) return raw.data;
  return [];
};

const unwrapItem = <T,>(raw: T | { data: T } | null | undefined): T | null => {
  if (!raw) return null;
  return "data" in raw ? raw.data : raw;
};

const productNameKey = (barcode?: string, batchNumber?: string | null) => `${barcode || ""}|${batchNumber || ""}`;

const buildProductNameMap = (reports: any[]): ProductNameMap => {
  return reports.reduce<ProductNameMap>((acc, report) => {
    if (!report?.product_name) return acc;
    if (report.barcode) acc[report.barcode] ||= report.product_name;
    if (report.barcode) acc[productNameKey(report.barcode, report.batch_number)] ||= report.product_name;
    return acc;
  }, {});
};

const calculateClusterRisk = (cluster: any) => {
  if (typeof cluster.risk_score === "number") return cluster.risk_score;

  const totalReports = cluster.total_reports ?? cluster.affected_reports_count ?? 0;
  const affectedUsers = cluster.affected_users_count ?? 0;
  const severityBase: Record<string, number> = {
    LOW: 18,
    MEDIUM: 32,
    HIGH: 58,
    CRITICAL: 76,
  };
  const base = severityBase[cluster.severity] ?? 28;
  return Math.min(95, Math.round(base + Math.log2(totalReports + 1) * 7 + Math.min(10, affectedUsers)));
};

const normalizeCluster = (cluster: any, productNames: ProductNameMap = {}): IssueCluster => ({
  ...cluster,
  product_name:
    cluster.product_name ||
    productNames[productNameKey(cluster.barcode, cluster.batch_number)] ||
    productNames[cluster.barcode] ||
    "Uncatalogued product",
  issue_type: cluster.issue_type || cluster.primary_issue_type || "OTHER",
  total_reports: cluster.total_reports ?? cluster.affected_reports_count ?? 0,
  risk_score: calculateClusterRisk(cluster),
});

const normalizeDashboard = (raw: any, productNames: ProductNameMap = {}): ClusterDashboardResponse => ({
  highest_risk: raw?.highest_risk ? normalizeCluster(raw.highest_risk, productNames) : null,
  fastest_growing: raw?.fastest_growing ? normalizeCluster(raw.fastest_growing, productNames) : null,
  most_active: raw?.most_active ? normalizeCluster(raw.most_active, productNames) : null,
  newest_cluster: raw?.newest_cluster ? normalizeCluster(raw.newest_cluster, productNames) : null,
  dormant_clusters: unwrapArray<any>(raw?.dormant_clusters).map((cluster) => normalizeCluster(cluster, productNames)),
});

const getDisplayGrowthRate = (profile?: ClusterIntelligence | null) => {
  if (!profile) return 0;
  const weeklyReports = profile.reports_last_7_days ?? 0;
  if (weeklyReports <= 0) return 0;
  if (weeklyReports === 1) return 6;
  if (weeklyReports <= 3) return 14;
  if (weeklyReports <= 7) return 28;
  return Math.min(65, 28 + (weeklyReports - 7) * 4);
};

export default function CommunityIntelligencePage() {
  const [dashboard, setDashboard] = useState<ClusterDashboardResponse>({
    highest_risk: null,
    fastest_growing: null,
    most_active: null,
    newest_cluster: null,
    dormant_clusters: [],
  });

  const [profiles, setProfiles] = useState<ClusterIntelligence[]>([]);
  const [clusters, setClusters] = useState<Record<string, IssueCluster>>({});
  const [activeFilter, setActiveFilter] = useState<"all" | "trending" | "high-risk" | "dormant">("all");
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Fetch clusters to resolve details
      const [clustersRes, reportsRes] = await Promise.all([
        apiFetch<{ data: IssueCluster[] } | IssueCluster[]>("/community/clusters?limit=100"),
        apiFetch<{ data: ProductReport[] } | ProductReport[]>("/community/reports?limit=100"),
      ]);
      const productNames = buildProductNameMap(unwrapArray<any>(reportsRes));
      const clusterMap: Record<string, IssueCluster> = {};
      unwrapArray<any>(clustersRes).map((cluster) => normalizeCluster(cluster, productNames)).forEach((c) => {
        clusterMap[c.id] = c;
      });
      setClusters(clusterMap);

      // 2. Fetch dashboard summary
      const dashboardRaw = await apiFetch<{ data: ClusterDashboardResponse } | ClusterDashboardResponse>("/community/intelligence/dashboard");
      const dashboardRes = unwrapItem<any>(dashboardRaw);
      setDashboard(normalizeDashboard(dashboardRes, productNames));

      // 3. Fetch profiles based on selection
      let profilesData: ClusterIntelligence[] = [];
      if (activeFilter === "all") {
        const res = await apiFetch<{ data: ClusterIntelligence[] } | ClusterIntelligence[]>("/community/intelligence?limit=100");
        profilesData = unwrapArray<ClusterIntelligence>(res);
      } else if (activeFilter === "trending") {
        const res = await apiFetch<{ data: ClusterIntelligence[] } | ClusterIntelligence[]>("/community/intelligence/trending");
        profilesData = unwrapArray<ClusterIntelligence>(res);
      } else if (activeFilter === "high-risk") {
        const res = await apiFetch<{ data: ClusterIntelligence[] } | ClusterIntelligence[]>("/community/intelligence/high-risk");
        profilesData = unwrapArray<ClusterIntelligence>(res);
      } else if (activeFilter === "dormant") {
        const res = await apiFetch<{ data: ClusterIntelligence[] } | ClusterIntelligence[]>("/community/intelligence/dormant");
        profilesData = unwrapArray<ClusterIntelligence>(res);
      }

      setProfiles(profilesData.map((profile) => ({
        ...profile,
        cluster: clusterMap[profile.cluster_id],
      })));
    } catch (err) {
      console.error("Failed to load intelligence metrics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeFilter]);

  const handleRecalculate = async () => {
    setRecalculating(true);
    try {
      const res = await apiFetch<{ success: boolean; message: string }>("/community/intelligence/recalculate", {
        method: "POST",
      });
      alert(res.message || "Intelligence models re-calculated successfully!");
      fetchData();
    } catch (err: any) {
      alert("Recalculation failed: " + err.message);
    } finally {
      setRecalculating(false);
    }
  };

  const filteredProfiles = profiles.filter((p) => {
    const cluster = clusters[p.cluster_id];
    if (!cluster) return true;
    const query = searchQuery.toLowerCase();
    return (
      cluster.product_name.toLowerCase().includes(query) ||
      cluster.barcode.toLowerCase().includes(query) ||
      cluster.cluster_code.toLowerCase().includes(query)
    );
  });
  const profilesByClusterId = profiles.reduce<Record<string, ClusterIntelligence>>((acc, profile) => {
    acc[profile.cluster_id] = profile;
    return acc;
  }, {});
  const getClusterGrowthRate = (cluster: IssueCluster | null) => {
    if (!cluster) return 0;
    const profile = profilesByClusterId[cluster.id];
    if (profile) return getDisplayGrowthRate(profile);
    const reportVolume = cluster.total_reports ?? 0;
    if (reportVolume <= 1) return 6;
    if (reportVolume <= 3) return 14;
    if (reportVolume <= 7) return 28;
    return Math.min(65, 28 + (reportVolume - 7) * 4);
  };

  return (
    <div className="space-y-8 p-8 max-w-7xl mx-auto">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-gray-100 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-950 flex items-center gap-3">
            <Sparkles className="size-8 text-blue-600" />
            CIE Community Intelligence Engine
          </h1>
          <p className="text-gray-500 mt-1">
            Real-time threat assessments, risk-indexing profiles, and spatial cluster metrics processed by Cliste AI.
          </p>
        </div>

        <button
          onClick={handleRecalculate}
          disabled={recalculating || loading}
          className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm flex items-center gap-2 shadow-sm transition-all disabled:opacity-50"
        >
          {recalculating ? <Loader2 className="size-4 animate-spin" /> : <RefreshCw className="size-4" />}
          Force CIE Recalculation
        </button>
      </div>

      {loading && profiles.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400 space-y-4">
          <Loader2 className="size-10 animate-spin text-blue-600" />
          <p className="text-sm font-semibold">Running multi-dimensional intelligence sweep...</p>
        </div>
      ) : (
        <>
          {/* CIE Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Highest Risk */}
            <div className="bg-white border border-gray-200/80 p-5 rounded-2xl shadow-sm hover:shadow-md transition-all">
              <div className="flex justify-between items-start">
                <span className="text-gray-500 text-xs font-bold uppercase tracking-wider">Highest Risk</span>
                <span className="bg-red-50 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-red-200">
                  Critical Threat
                </span>
              </div>
              {dashboard.highest_risk ? (
                <div className="mt-4">
                  <p className="text-xl font-extrabold text-gray-900 leading-tight">
                    {dashboard.highest_risk.product_name}
                  </p>
                  <p className="text-xs text-gray-500 font-mono mt-1">{dashboard.highest_risk.cluster_code}</p>
                  <div className="mt-3 flex items-baseline gap-2">
                    <span className="text-2xl font-black text-red-600">{dashboard.highest_risk.risk_score}</span>
                    <span className="text-xs text-gray-400 font-medium">CIE Index</span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-400 mt-6">No threat clusters verified.</p>
              )}
            </div>

            {/* Fastest Growing */}
            <div className="bg-white border border-gray-200/80 p-5 rounded-2xl shadow-sm hover:shadow-md transition-all">
              <div className="flex justify-between items-start">
                <span className="text-gray-500 text-xs font-bold uppercase tracking-wider">Fastest Growing</span>
                <span className="bg-amber-50 text-amber-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-amber-200">
                  Rapid Growth
                </span>
              </div>
              {dashboard.fastest_growing ? (
                <div className="mt-4">
                  <p className="text-xl font-extrabold text-gray-900 leading-tight">
                    {dashboard.fastest_growing.product_name}
                  </p>
                  <p className="text-xs text-gray-500 font-mono mt-1">{dashboard.fastest_growing.cluster_code}</p>
                  <div className="mt-3 flex items-baseline gap-2">
                    <span className="text-2xl font-black text-amber-600 flex items-center">
                      <ArrowUpRight className="size-5 shrink-0" />
                      {getClusterGrowthRate(dashboard.fastest_growing)}%
                    </span>
                    <span className="text-xs text-gray-400 font-medium">Growth rate</span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-400 mt-6">No emerging trend clusters.</p>
              )}
            </div>

            {/* Most Active */}
            <div className="bg-white border border-gray-200/80 p-5 rounded-2xl shadow-sm hover:shadow-md transition-all">
              <div className="flex justify-between items-start">
                <span className="text-gray-500 text-xs font-bold uppercase tracking-wider">Most Active</span>
                <span className="bg-blue-50 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-blue-200">
                  High Activity
                </span>
              </div>
              {dashboard.most_active ? (
                <div className="mt-4">
                  <p className="text-xl font-extrabold text-gray-900 leading-tight">
                    {dashboard.most_active.product_name}
                  </p>
                  <p className="text-xs text-gray-500 font-mono mt-1">{dashboard.most_active.cluster_code}</p>
                  <div className="mt-3 flex items-baseline gap-2">
                    <span className="text-2xl font-black text-blue-600">{dashboard.most_active.total_reports}</span>
                    <span className="text-xs text-gray-400 font-medium">Consumer reports</span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-400 mt-6">No active report arrays.</p>
              )}
            </div>

            {/* Dormant Clusters */}
            <div className="bg-white border border-gray-200/80 p-5 rounded-2xl shadow-sm hover:shadow-md transition-all">
              <div className="flex justify-between items-start">
                <span className="text-gray-500 text-xs font-bold uppercase tracking-wider">Dormant (30d)</span>
                <span className="bg-slate-50 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-slate-200">
                  Inactive
                </span>
              </div>
              <div className="mt-4">
                <p className="text-3xl font-black text-gray-900">{dashboard.dormant_clusters.length}</p>
                <p className="text-xs text-gray-500 mt-2 font-medium">Issues with zero reports in last 30 days</p>
                <div className="mt-3 text-xs text-green-600 flex items-center gap-1 font-semibold">
                  <ArrowDownRight className="size-4" /> Containment Successful
                </div>
              </div>
            </div>
          </div>

          {/* Main Profiles Area */}
          <div className="space-y-6">
            {/* Toolbar */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gray-50 p-2 rounded-2xl border border-gray-200/60">
              {/* Tabs */}
              <div className="flex gap-1.5">
                {[
                  { key: "all", label: "All CIE Profiles" },
                  { key: "trending", label: "Trending Clusters" },
                  { key: "high-risk", label: "High Risk (>=50)" },
                  { key: "dormant", label: "Dormant (Inactive)" },
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveFilter(tab.key as any)}
                    className={`px-4 py-2 text-xs font-semibold rounded-xl transition-all ${
                      activeFilter === tab.key
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
                  placeholder="Search barcode or product..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-xl text-xs bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                />
              </div>
            </div>

            {/* CIE Table */}
            <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-55 border-b border-gray-200 text-gray-500 font-bold text-[11px] uppercase tracking-wider">
                    <th className="p-4">CIE Index / Cluster</th>
                    <th className="p-4">Risk Index</th>
                    <th className="p-4">Growth Rate</th>
                    <th className="p-4">Trend State</th>
                    <th className="p-4">Spread Level</th>
                    <th className="p-4">Escalation</th>
                    <th className="p-4">Volume (24h/7d/30d)</th>
                    <th className="p-4">Avg Credibility</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-sm">
                  {filteredProfiles.length > 0 ? (
                    filteredProfiles.map((p) => {
                      const cluster = clusters[p.cluster_id];
                      const displayGrowth = getDisplayGrowthRate(p);
                      return (
                        <tr key={p.id} className="hover:bg-gray-50/50">
                          <td className="p-4">
                            {cluster ? (
                              <div>
                                <p className="font-bold text-gray-900 text-sm leading-snug">{cluster.product_name}</p>
                                <div className="flex items-center gap-2 mt-0.5">
                                  <span className="text-xs font-mono font-bold text-gray-500">{cluster.cluster_code}</span>
                                  <span className="text-[10px] text-gray-400 font-mono">({cluster.barcode})</span>
                                </div>
                              </div>
                            ) : (
                              <span className="text-gray-400 font-mono text-xs">{p.cluster_id}</span>
                            )}
                          </td>
                          <td className="p-4">
                            <div className="flex items-center gap-2">
                              <span className={`font-black ${
                                p.risk_score >= 70 ? "text-red-600" :
                                p.risk_score >= 50 ? "text-amber-600" :
                                p.risk_score >= 25 ? "text-blue-600" : "text-green-600"
                              }`}>
                                {p.risk_score}
                              </span>
                              <div className="w-16 bg-gray-100 h-1.5 rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${
                                    p.risk_score >= 70 ? "bg-red-500" :
                                    p.risk_score >= 50 ? "bg-amber-500" :
                                    p.risk_score >= 25 ? "bg-blue-500" : "bg-green-500"
                                  }`}
                                  style={{ width: `${p.risk_score}%` }}
                                ></div>
                              </div>
                            </div>
                          </td>
                          <td className="p-4">
                            <span className={`font-bold flex items-center ${
                              displayGrowth > 45 ? "text-red-600" :
                              displayGrowth > 0 ? "text-amber-600" : "text-green-600"
                            }`}>
                              {displayGrowth > 0 ? "+" : ""}
                              {displayGrowth}%
                            </span>
                          </td>
                          <td className="p-4">
                            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                              p.trend === "RAPIDLY_GROWING" ? "bg-red-50 text-red-700 border-red-200" :
                              p.trend === "GROWING" ? "bg-amber-50 text-amber-700 border-amber-200" :
                              p.trend === "DECLINING" ? "bg-green-50 text-green-700 border-green-200" : "bg-slate-50 text-slate-700 border-slate-200"
                            }`}>
                              {p.trend}
                            </span>
                          </td>
                          <td className="p-4">
                            <span className="text-gray-700 font-medium text-xs">
                              {p.spread_level}
                            </span>
                          </td>
                          <td className="p-4">
                            <span className={`font-bold text-xs uppercase ${
                              p.escalation_level === "CRITICAL" ? "text-red-600" :
                              p.escalation_level === "SEVERE" ? "text-red-500" :
                              p.escalation_level === "ELEVATED" ? "text-amber-500" : "text-gray-500"
                            }`}>
                              {p.escalation_level}
                            </span>
                          </td>
                          <td className="p-4 font-mono text-xs text-gray-500">
                            {p.reports_last_24h} / {p.reports_last_7_days} / {p.reports_last_30_days}
                          </td>
                          <td className="p-4">
                            <div className="flex items-center gap-1.5">
                              <span className="font-bold text-gray-900">{p.average_credibility}%</span>
                              <span className="text-[10px] text-gray-400">CRCE</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan={8} className="text-center py-12 text-gray-400">
                        No cluster intelligence profiles found matching criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
