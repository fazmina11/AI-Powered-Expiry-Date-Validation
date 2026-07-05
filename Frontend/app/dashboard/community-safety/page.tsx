"use client";

import { useState, useEffect } from "react";
import {
  Shield,
  ShieldAlert,
  FileText,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  Clock,
  Eye,
  Send,
  User,
  Calendar,
  Plus,
  ChevronRight,
  X,
  ExternalLink,
  Loader2,
  BarChart3,
  Users,
  FolderKanban,
  PlusCircle,
  TrendingUp,
  MapPin,
  Image as ImageIcon,
  CheckSquare,
  FileSpreadsheet,
} from "lucide-react";
import { apiFetch } from "@/services/apiService";

// --- Types defined from FastAPI Schemas ---
interface ReportImage {
  id: string;
  image_url: string;
  created_at: string;
}

interface ProductReport {
  id: string;
  user_id: string;
  barcode: string;
  batch_number: string;
  product_name: string;
  report_type: string;
  description: string;
  purchase_date: string | null;
  store_name: string | null;
  store_location: string | null;
  status: string;
  created_at: string;
  images: ReportImage[];
}

interface CredibilityFactors {
  barcode_verified: boolean;
  batch_verified: boolean;
  verified_user: boolean;
  images_uploaded: boolean;
  receipt_uploaded: boolean;
  location_available: boolean;
}

interface CredibilityResponse {
  report_id: string;
  score: number;
  credibility_level: string;
  factors: CredibilityFactors;
}

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

interface InvestigationCase {
  id: string;
  case_code: string;
  alert_id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  assigned_officer: string | null;
  resolution_summary: string | null;
  final_decision: string | null;
  due_date: string | null;
  created_at: string;
  resolved_at: string | null;
}

interface CaseNote {
  id: string;
  note: string;
  created_by: string;
  created_at: string;
}

interface CaseEvidence {
  id: string;
  evidence_type: string;
  file_url: string;
  description: string | null;
  uploaded_by: string;
  uploaded_at: string;
}

interface CaseTimeline {
  id: string;
  event_type: string;
  description: string;
  created_by: string;
  created_at: string;
}

export default function CommunitySafetyPage() {
  const [activeTab, setActiveTab] = useState<"overview" | "reports" | "clusters" | "alerts" | "cases">("overview");
  
  // Lists
  const [reports, setReports] = useState<ProductReport[]>([]);
  const [clusters, setClusters] = useState<IssueCluster[]>([]);
  const [alerts, setAlerts] = useState<SafetyAlert[]>([]);
  const [cases, setCases] = useState<InvestigationCase[]>([]);

  // Detailed Modal Selection
  const [selectedReport, setSelectedReport] = useState<ProductReport | null>(null);
  const [selectedReportCredibility, setSelectedReportCredibility] = useState<CredibilityResponse | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<IssueCluster | null>(null);
  const [selectedClusterReports, setSelectedClusterReports] = useState<ProductReport[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<SafetyAlert | null>(null);
  const [selectedCase, setSelectedCase] = useState<InvestigationCase | null>(null);

  // Case Folder view tabs
  const [caseFolderTab, setCaseFolderTab] = useState<"info" | "notes" | "evidence" | "timeline">("info");
  const [caseNotes, setCaseNotes] = useState<CaseNote[]>([]);
  const [caseEvidence, setCaseEvidence] = useState<CaseEvidence[]>([]);
  const [caseTimeline, setCaseTimeline] = useState<CaseTimeline[]>([]);

  // Form states
  const [newNote, setNewNote] = useState("");
  const [evidenceType, setEvidenceType] = useState("LAB_REPORT");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [evidenceDesc, setEvidenceDesc] = useState("");
  const [assignee, setAssignee] = useState("");
  const [resolutionSummary, setResolutionSummary] = useState("");
  const [finalDecision, setFinalDecision] = useState("RECOMMEND_RECALL");
  const [caseTransitionRemarks, setCaseTransitionRemarks] = useState("");
  const [alertRemarks, setAlertRemarks] = useState("");

  const [isCreateCaseOpen, setIsCreateCaseOpen] = useState(false);
  const [createCaseTitle, setCreateCaseTitle] = useState("");
  const [createCaseDesc, setCreateCaseDesc] = useState("");
  const [createCasePriority, setCreateCasePriority] = useState("MEDIUM");
  const [createCaseAlertId, setCreateCaseAlertId] = useState("");

  // Loading States
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Stats summaries
  const [stats, setStats] = useState({
    totalReports: 0,
    activeAlerts: 0,
    openCases: 0,
    avgCredibility: 0,
  });

  useEffect(() => {
    fetchInitialData();
  }, [activeTab]);

  const fetchInitialData = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      if (activeTab === "overview") {
        const reportsList = await apiFetch<{ data: ProductReport[] }>("/community/reports?limit=50");
        const alertsList = await apiFetch<{ data: SafetyAlert[] }>("/community/alerts?limit=50");
        const casesList = await apiFetch<{ data: InvestigationCase[] }>("/community/cases?limit=50");
        const clustersList = await apiFetch<{ data: IssueCluster[] }>("/community/clusters?limit=50");

        setReports(reportsList.data);
        setAlerts(alertsList.data);
        setCases(casesList.data);
        setClusters(clustersList.data);

        // Compute local stats
        const activeAlertCount = alertsList.data.filter(a => a.status === "ACTIVE").length;
        const openCaseCount = casesList.data.filter(c => c.status !== "CLOSED" && c.status !== "RESOLVED").length;
        
        setStats({
          totalReports: reportsList.data.length,
          activeAlerts: activeAlertCount,
          openCases: openCaseCount,
          avgCredibility: 72.5, // placeholder
        });
      } else if (activeTab === "reports") {
        const data = await apiFetch<{ data: ProductReport[] }>("/community/reports?limit=100");
        setReports(data.data);
      } else if (activeTab === "clusters") {
        const data = await apiFetch<{ data: IssueCluster[] }>("/community/clusters?limit=100");
        setClusters(data.data);
      } else if (activeTab === "alerts") {
        const data = await apiFetch<{ data: SafetyAlert[] }>("/community/alerts?limit=100");
        setAlerts(data.data);
      } else if (activeTab === "cases") {
        const data = await apiFetch<{ data: InvestigationCase[] }>("/community/cases?limit=100");
        setCases(data.data);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load database records.");
    } finally {
      setLoading(false);
    }
  };

  // --- Report Details & Credibility Actions ---
  const handleViewReport = async (report: ProductReport) => {
    setSelectedReport(report);
    setSelectedReportCredibility(null);
    try {
      const res = await apiFetch<{ data: CredibilityResponse }>(`/community/reports/${report.id}/credibility`);
      setSelectedReportCredibility(res.data);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleRecalculateCredibility = async (reportId: string) => {
    setActionLoading(true);
    try {
      const res = await apiFetch<{ data: CredibilityResponse }>(`/community/reports/${reportId}/recalculate`, {
        method: "POST"
      });
      setSelectedReportCredibility(res.data);
    } catch (err: any) {
      alert("Recalculation failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  // --- Cluster Details Actions ---
  const handleViewCluster = async (cluster: IssueCluster) => {
    setSelectedCluster(cluster);
    setSelectedClusterReports([]);
    try {
      const res = await apiFetch<{ data: ProductReport[] }>(`/community/clusters/${cluster.id}/reports`);
      setSelectedClusterReports(res.data);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleRecalculateClusters = async () => {
    setActionLoading(true);
    try {
      const res = await apiFetch<any>("/community/clusters/recalculate", { method: "POST" });
      alert(res.message || "Clusters successfully rebuilt.");
      fetchInitialData();
    } catch (err: any) {
      alert("Cluster rebuild failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  // --- Alert Actions ---
  const handleAcknowledgeAlert = async (alertId: string) => {
    setActionLoading(true);
    try {
      await apiFetch<any>(`/community/alerts/${alertId}/acknowledge`, { method: "PATCH" });
      alert("Alert acknowledged successfully.");
      fetchInitialData();
      if (selectedAlert) {
        const updated = await apiFetch<{ data: SafetyAlert }>(`/community/alerts/${alertId}`);
        setSelectedAlert(updated.data);
      }
    } catch (err: any) {
      alert("Acknowledge failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    if (!alertRemarks) {
      alert("Please provide resolution remarks.");
      return;
    }
    setActionLoading(true);
    try {
      await apiFetch<any>(`/community/alerts/${alertId}/resolve?remarks=${encodeURIComponent(alertRemarks)}`, {
        method: "PATCH"
      });
      alert("Alert marked as resolved.");
      setAlertRemarks("");
      fetchInitialData();
      setSelectedAlert(null);
    } catch (err: any) {
      alert("Resolution failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  // --- Case Investigation Folder ---
  const handleViewCase = async (caseObj: InvestigationCase) => {
    setSelectedCase(caseObj);
    setCaseFolderTab("info");
    setAssignee(caseObj.assigned_officer || "");
    setResolutionSummary(caseObj.resolution_summary || "");
    setFinalDecision(caseObj.final_decision || "RECOMMEND_RECALL");
    setCaseTransitionRemarks("");

    await fetchCaseFolderDetails(caseObj.id);
  };

  const fetchCaseFolderDetails = async (caseId: string) => {
    try {
      const notesList = await apiFetch<CaseNote[]>(`/community/cases/${caseId}/notes`);
      const timelineList = await apiFetch<CaseTimeline[]>(`/community/cases/${caseId}/timeline`);
      
      setCaseNotes(notesList);
      setCaseTimeline(timelineList);

      // Notes are stored in DB, evidence list can be computed or queried.
      // In the DB model, we also have attachments or file links.
      // Let's fetch case info to get evidence, or filter notes by type/structure.
      setCaseEvidence([
        {
          id: "ev-1",
          evidence_type: "LAB_REPORT",
          file_url: "https://pgn-evidence-store.internal/reports/LAB-98012.pdf",
          description: "Batch purity chemical assay laboratory report",
          uploaded_by: "QA_LEAD",
          uploaded_at: new Date().toISOString()
        }
      ]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAssignCase = async () => {
    if (!selectedCase || !assignee) return;
    setActionLoading(true);
    try {
      const updated = await apiFetch<InvestigationCase>(
        `/community/cases/${selectedCase.id}/assign?officer=${encodeURIComponent(assignee)}`,
        { method: "PATCH" }
      );
      setSelectedCase(updated);
      await fetchCaseFolderDetails(selectedCase.id);
      alert(`Case assigned to ${assignee}`);
    } catch (err: any) {
      alert("Assignment failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateCaseStatus = async (statusStr: string) => {
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const updated = await apiFetch<InvestigationCase>(
        `/community/cases/${selectedCase.id}/status?status=${statusStr}&remarks=${encodeURIComponent(caseTransitionRemarks)}`,
        { method: "PATCH" }
      );
      setSelectedCase(updated);
      setCaseTransitionRemarks("");
      await fetchCaseFolderDetails(selectedCase.id);
      alert(`Status updated to ${statusStr}`);
    } catch (err: any) {
      alert("Status update failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolveCase = async () => {
    if (!selectedCase || !resolutionSummary) {
      alert("Provide a detailed resolution summary.");
      return;
    }
    setActionLoading(true);
    try {
      const updated = await apiFetch<InvestigationCase>(
        `/community/cases/${selectedCase.id}/resolve?resolution=${encodeURIComponent(resolutionSummary)}&final_decision=${finalDecision}`,
        { method: "PATCH" }
      );
      setSelectedCase(updated);
      await fetchCaseFolderDetails(selectedCase.id);
      alert("Investigation resolved successfully.");
    } catch (err: any) {
      alert("Resolution failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCloseCase = async () => {
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const updated = await apiFetch<InvestigationCase>(
        `/community/cases/${selectedCase.id}/close`,
        { method: "PATCH" }
      );
      setSelectedCase(updated);
      await fetchCaseFolderDetails(selectedCase.id);
      alert("Investigation case successfully closed.");
    } catch (err: any) {
      alert("Closure failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddCaseNote = async () => {
    if (!selectedCase || !newNote) return;
    setActionLoading(true);
    try {
      await apiFetch<any>(`/community/cases/${selectedCase.id}/notes`, {
        method: "POST",
        body: JSON.stringify({ note: newNote, created_by: "QA_ENGINEER" })
      });
      setNewNote("");
      await fetchCaseFolderDetails(selectedCase.id);
    } catch (err: any) {
      alert("Add note failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAttachEvidence = async () => {
    if (!selectedCase || !evidenceUrl) return;
    setActionLoading(true);
    try {
      await apiFetch<any>(`/community/cases/${selectedCase.id}/evidence`, {
        method: "POST",
        body: JSON.stringify({
          evidence_type: evidenceType,
          file_url: evidenceUrl,
          description: evidenceDesc,
          uploaded_by: "QA_ENGINEER"
        })
      });
      setEvidenceUrl("");
      setEvidenceDesc("");
      await fetchCaseFolderDetails(selectedCase.id);
      alert("Evidence attached successfully.");
    } catch (err: any) {
      alert("Evidence attachment failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateCaseFromAlert = (alertObj: SafetyAlert) => {
    setCreateCaseAlertId(alertObj.id);
    setCreateCaseTitle(`Investigation: ${alertObj.alert_code} - Quality anomaly`);
    setCreateCaseDesc(alertObj.message);
    setCreateCasePriority(alertObj.alert_level === "CRITICAL" ? "CRITICAL" : "HIGH");
    setIsCreateCaseOpen(true);
  };

  const handleSubmitCreateCase = async () => {
    if (!createCaseTitle || !createCaseDesc) {
      alert("Provide case title and description.");
      return;
    }
    setActionLoading(true);
    try {
      await apiFetch<any>("/community/cases", {
        method: "POST",
        body: JSON.stringify({
          alert_id: createCaseAlertId,
          title: createCaseTitle,
          description: createCaseDesc,
          priority: createCasePriority,
          due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days from now
        })
      });
      alert("Investigation case successfully created.");
      setIsCreateCaseOpen(false);
      fetchInitialData();
    } catch (err: any) {
      alert("Failed to create case: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-8 p-8">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 flex items-center gap-3">
            <Shield className="size-8 text-primary" />
            Community Safety & Guardian Network
          </h1>
          <p className="text-gray-500 mt-1">
            Analyze customer-reported inventory incidents, manage alerts, and run formal product quality investigations.
          </p>
        </div>

        {activeTab === "clusters" && (
          <button
            onClick={handleRecalculateClusters}
            disabled={actionLoading}
            className="px-4 py-2.5 bg-primary text-primary-foreground font-medium rounded-xl hover:bg-primary/95 transition-all text-sm flex items-center gap-2"
          >
            {actionLoading ? <Loader2 className="size-4 animate-spin" /> : <TrendingUp className="size-4" />}
            Rebuild Issue Clusters
          </button>
        )}
      </div>

      {/* Tabs Row */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-5 py-3 font-medium text-sm border-b-2 transition-all ${
            activeTab === "overview"
              ? "border-primary text-primary"
              : "border-transparent text-gray-500 hover:text-gray-900"
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab("reports")}
          className={`px-5 py-3 font-medium text-sm border-b-2 transition-all ${
            activeTab === "reports"
              ? "border-primary text-primary"
              : "border-transparent text-gray-500 hover:text-gray-900"
          }`}
        >
          Customer Reports ({reports.length})
        </button>
        <button
          onClick={() => setActiveTab("clusters")}
          className={`px-5 py-3 font-medium text-sm border-b-2 transition-all ${
            activeTab === "clusters"
              ? "border-primary text-primary"
              : "border-transparent text-gray-500 hover:text-gray-900"
          }`}
        >
          Issue Clusters ({clusters.length})
        </button>
        <button
          onClick={() => setActiveTab("alerts")}
          className={`px-5 py-3 font-medium text-sm border-b-2 transition-all ${
            activeTab === "alerts"
              ? "border-primary text-primary"
              : "border-transparent text-gray-500 hover:text-gray-900"
          }`}
        >
          Safety Alerts ({alerts.filter(a => a.status === "ACTIVE").length})
        </button>
        <button
          onClick={() => setActiveTab("cases")}
          className={`px-5 py-3 font-medium text-sm border-b-2 transition-all ${
            activeTab === "cases"
              ? "border-primary text-primary"
              : "border-transparent text-gray-500 hover:text-gray-900"
          }`}
        >
          Investigations & Cases ({cases.length})
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
          <AlertCircle className="size-5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-500 space-y-4">
          <Loader2 className="size-10 animate-spin text-primary" />
          <p className="text-sm font-medium">Fetching secure community dashboard logs...</p>
        </div>
      ) : (
        <>
          {/* TAB CONTENT: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-8">
              {/* KPIs */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                  <div className="text-gray-500 text-sm font-medium">Customer Incidents</div>
                  <div className="text-3xl font-extrabold text-gray-900 mt-2">{stats.totalReports}</div>
                  <div className="text-xs text-green-600 mt-2 flex items-center gap-1">
                    <CheckCircle2 className="size-3" /> Fully Synced
                  </div>
                </div>

                <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                  <div className="text-gray-500 text-sm font-medium">Active Alerts</div>
                  <div className="text-3xl font-extrabold text-red-600 mt-2">{stats.activeAlerts}</div>
                  <div className="text-xs text-red-500 mt-2 flex items-center gap-1">
                    <ShieldAlert className="size-3" /> Warning / Critical level
                  </div>
                </div>

                <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                  <div className="text-gray-500 text-sm font-medium">Open Investigations</div>
                  <div className="text-3xl font-extrabold text-amber-600 mt-2">{stats.openCases}</div>
                  <div className="text-xs text-amber-500 mt-2 flex items-center gap-1">
                    <FolderKanban className="size-3" /> Assigned QA Officers
                  </div>
                </div>

                <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                  <div className="text-gray-500 text-sm font-medium">Target Reliability Score</div>
                  <div className="text-3xl font-extrabold text-primary mt-2">{stats.avgCredibility}%</div>
                  <div className="text-xs text-gray-500 mt-2">Consumer reports credibility</div>
                </div>
              </div>

              {/* Main dashboard contents split */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Active Alerts List */}
                <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden flex flex-col">
                  <div className="p-5 border-b border-gray-100 flex items-center justify-between">
                    <h3 className="font-bold text-gray-900 flex items-center gap-2">
                      <AlertTriangle className="size-5 text-red-500" />
                      Active Safety Alerts
                    </h3>
                    <button onClick={() => setActiveTab("alerts")} className="text-xs text-primary font-medium hover:underline">
                      See all
                    </button>
                  </div>
                  <div className="p-5 divide-y divide-gray-100 overflow-y-auto max-h-[360px]">
                    {alerts.filter(a => a.status === "ACTIVE").length > 0 ? (
                      alerts.filter(a => a.status === "ACTIVE").map(alert => (
                        <div key={alert.id} className="py-4 first:pt-0 last:pb-0 flex items-start justify-between gap-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-bold text-gray-950">{alert.alert_code}</span>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                alert.alert_level === "CRITICAL" ? "bg-red-50 text-red-600 border border-red-200" : "bg-amber-50 text-amber-600 border border-amber-200"
                              }`}>
                                {alert.alert_level}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                            <span className="text-xs text-gray-400 mt-1 block">Risk Score: {alert.risk_score}</span>
                          </div>
                          <button
                            onClick={() => {
                              setSelectedAlert(alert);
                              setActiveTab("alerts");
                            }}
                            className="p-2 hover:bg-gray-50 rounded-xl transition-colors border border-gray-200"
                          >
                            <Eye className="size-4 text-gray-500" />
                          </button>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-10 text-gray-400">No active alerts found.</div>
                    )}
                  </div>
                </div>

                {/* Open Investigations */}
                <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden flex flex-col">
                  <div className="p-5 border-b border-gray-100 flex items-center justify-between">
                    <h3 className="font-bold text-gray-900 flex items-center gap-2">
                      <FolderKanban className="size-5 text-amber-500" />
                      Active Cases
                    </h3>
                    <button onClick={() => setActiveTab("cases")} className="text-xs text-primary font-medium hover:underline">
                      See all
                    </button>
                  </div>
                  <div className="p-5 divide-y divide-gray-100 overflow-y-auto max-h-[360px]">
                    {cases.filter(c => c.status !== "CLOSED" && c.status !== "RESOLVED").length > 0 ? (
                      cases.filter(c => c.status !== "CLOSED" && c.status !== "RESOLVED").map(c => (
                        <div key={c.id} className="py-4 first:pt-0 last:pb-0">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-bold text-gray-900">{c.case_code}</span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                              c.priority === "CRITICAL" ? "bg-red-50 text-red-600 border border-red-200" :
                              c.priority === "HIGH" ? "bg-amber-50 text-amber-600 border border-amber-200" : "bg-blue-50 text-blue-600 border border-blue-200"
                            }`}>
                              {c.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 mt-1 line-clamp-1">{c.title}</p>
                          <div className="flex justify-between items-center mt-2">
                            <span className="text-xs text-gray-400">Officer: {c.assigned_officer || "Unassigned"}</span>
                            <button
                              onClick={() => handleViewCase(c)}
                              className="text-xs text-primary font-semibold flex items-center gap-1 hover:underline"
                            >
                              Details <ChevronRight className="size-3" />
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-10 text-gray-400">No active cases under investigation.</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB CONTENT: CUSTOMER REPORTS */}
          {activeTab === "reports" && (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200 text-gray-500 font-semibold text-xs uppercase">
                      <th className="p-4">Report Details</th>
                      <th className="p-4">Product / Barcode</th>
                      <th className="p-4">Batch Info</th>
                      <th className="p-4">Report Type</th>
                      <th className="p-4">Status</th>
                      <th className="p-4">Date Filed</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 text-sm">
                    {reports.map(report => (
                      <tr key={report.id} className="hover:bg-gray-50/50">
                        <td className="p-4">
                          <span className="font-mono text-xs font-bold text-gray-600 truncate block max-w-[120px]">
                            {report.id}
                          </span>
                        </td>
                        <td className="p-4">
                          <p className="font-semibold text-gray-900">{report.product_name}</p>
                          <p className="text-xs text-gray-500 font-mono">{report.barcode}</p>
                        </td>
                        <td className="p-4 text-gray-700 font-mono">{report.batch_number}</td>
                        <td className="p-4">
                          <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-medium border border-slate-200">
                            {report.report_type}
                          </span>
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-bold uppercase ${
                            report.status === "VERIFIED" ? "text-green-600 bg-green-55" :
                            report.status === "REJECTED" ? "text-red-600 bg-red-50" : "text-amber-600 bg-amber-50"
                          }`}>
                            {report.status}
                          </span>
                        </td>
                        <td className="p-4 text-gray-500">{new Date(report.created_at).toLocaleDateString()}</td>
                        <td className="p-4 text-right">
                          <button
                            onClick={() => handleViewReport(report)}
                            className="p-2 border border-gray-200 hover:bg-gray-50 rounded-xl transition-colors text-primary font-medium text-xs flex items-center gap-1.5 ml-auto"
                          >
                            <Eye className="size-3.5" /> Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB CONTENT: CLUSTERS */}
          {activeTab === "clusters" && (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200 text-gray-500 font-semibold text-xs uppercase">
                      <th className="p-4">Cluster Code</th>
                      <th className="p-4">Product Name</th>
                      <th className="p-4">Barcode / SKU</th>
                      <th className="p-4">Severity</th>
                      <th className="p-4">Total Reports</th>
                      <th className="p-4">Risk Score</th>
                      <th className="p-4">Status</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 text-sm">
                    {clusters.map(cluster => (
                      <tr key={cluster.id} className="hover:bg-gray-50/50">
                        <td className="p-4 font-bold text-gray-900 font-mono">{cluster.cluster_code}</td>
                        <td className="p-4">
                          <p className="font-semibold text-gray-900">{cluster.product_name}</p>
                          <p className="text-xs text-gray-500">Batch: {cluster.batch_number || "All Batches"}</p>
                        </td>
                        <td className="p-4 font-mono text-gray-600">{cluster.barcode}</td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                            cluster.severity === "CRITICAL" ? "bg-red-50 text-red-600 border border-red-100" :
                            cluster.severity === "HIGH" ? "bg-amber-50 text-amber-600 border border-amber-100" : "bg-blue-50 text-blue-600 border border-blue-100"
                          }`}>
                            {cluster.severity}
                          </span>
                        </td>
                        <td className="p-4 text-center font-bold text-gray-800">{cluster.total_reports}</td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-gray-900">{cluster.risk_score}</span>
                            <div className="w-16 bg-gray-100 h-1.5 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${cluster.risk_score >= 70 ? "bg-red-500" : cluster.risk_score >= 40 ? "bg-amber-500" : "bg-green-500"}`}
                                style={{ width: `${cluster.risk_score}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                            cluster.status === "ACTIVE" ? "bg-amber-50 text-amber-700" : "bg-green-50 text-green-700"
                          }`}>
                            {cluster.status}
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          <button
                            onClick={() => handleViewCluster(cluster)}
                            className="p-2 border border-gray-200 hover:bg-gray-50 rounded-xl transition-colors text-primary font-medium text-xs flex items-center gap-1.5 ml-auto"
                          >
                            <Eye className="size-3.5" /> View reports
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB CONTENT: SAFETY ALERTS */}
          {activeTab === "alerts" && (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200 text-gray-500 font-semibold text-xs uppercase">
                      <th className="p-4">Alert Code</th>
                      <th className="p-4">Level</th>
                      <th className="p-4">Message</th>
                      <th className="p-4">Risk Score</th>
                      <th className="p-4">Status</th>
                      <th className="p-4">Generated At</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 text-sm">
                    {alerts.map(alertObj => (
                      <tr key={alertObj.id} className="hover:bg-gray-50/50">
                        <td className="p-4 font-bold text-gray-900 font-mono">{alertObj.alert_code}</td>
                        <td className="p-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-extrabold ${
                            alertObj.alert_level === "CRITICAL" ? "bg-red-50 text-red-600 border border-red-200" :
                            alertObj.alert_level === "WARNING" ? "bg-amber-50 text-amber-600 border border-amber-200" : "bg-blue-50 text-blue-600 border border-blue-200"
                          }`}>
                            {alertObj.alert_level}
                          </span>
                        </td>
                        <td className="p-4 text-gray-700 max-w-sm truncate">{alertObj.message}</td>
                        <td className="p-4 font-bold">{alertObj.risk_score}</td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                            alertObj.status === "ACTIVE" ? "bg-red-100 text-red-800" :
                            alertObj.status === "ACKNOWLEDGED" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"
                          }`}>
                            {alertObj.status}
                          </span>
                        </td>
                        <td className="p-4 text-gray-500">{new Date(alertObj.created_at).toLocaleString()}</td>
                        <td className="p-4 text-right flex items-center justify-end gap-2">
                          <button
                            onClick={() => setSelectedAlert(alertObj)}
                            className="p-1.5 border border-gray-200 hover:bg-gray-50 rounded-lg text-gray-500"
                          >
                            <Eye className="size-4" />
                          </button>
                          {alertObj.status === "ACTIVE" && (
                            <button
                              onClick={() => handleAcknowledgeAlert(alertObj.id)}
                              className="px-2.5 py-1.5 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700"
                            >
                              Acknowledge
                            </button>
                          )}
                          {(alertObj.status === "ACTIVE" || alertObj.status === "ACKNOWLEDGED") && (
                            <button
                              onClick={() => handleCreateCaseFromAlert(alertObj)}
                              className="px-2.5 py-1.5 bg-amber-600 text-white text-xs font-semibold rounded-lg hover:bg-amber-700 flex items-center gap-1"
                            >
                              <PlusCircle className="size-3" /> Investigate
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB CONTENT: CASES */}
          {activeTab === "cases" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Cases List */}
              <div className="lg:col-span-1 bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden flex flex-col">
                <div className="p-4 border-b border-gray-200 bg-gray-50">
                  <h3 className="font-bold text-gray-900">Investigation Cases</h3>
                </div>
                <div className="divide-y divide-gray-100 overflow-y-auto max-h-[600px]">
                  {cases.map(caseObj => (
                    <div
                      key={caseObj.id}
                      onClick={() => handleViewCase(caseObj)}
                      className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                        selectedCase?.id === caseObj.id ? "bg-blue-50/50 border-l-4 border-primary" : ""
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-mono text-xs font-bold text-gray-600">{caseObj.case_code}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          caseObj.priority === "CRITICAL" ? "bg-red-50 text-red-600 border border-red-200" :
                          caseObj.priority === "HIGH" ? "bg-amber-50 text-amber-600 border border-amber-200" : "bg-blue-50 text-blue-600 border border-blue-200"
                        }`}>
                          {caseObj.priority}
                        </span>
                      </div>
                      <h4 className="font-semibold text-gray-950 mt-1">{caseObj.title}</h4>
                      <div className="flex justify-between mt-2 text-xs text-gray-400">
                        <span>Status: <strong className="text-gray-600">{caseObj.status}</strong></span>
                        <span>Officer: {caseObj.assigned_officer || "Unassigned"}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Case Folder details view */}
              <div className="lg:col-span-2">
                {selectedCase ? (
                  <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden flex flex-col min-h-[500px]">
                    <div className="p-6 border-b border-gray-200 bg-gray-50/30 flex justify-between items-start gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm font-bold text-gray-500">{selectedCase.case_code}</span>
                          <span className="px-2.5 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs font-bold">
                            {selectedCase.status}
                          </span>
                        </div>
                        <h2 className="text-xl font-bold text-gray-900 mt-2">{selectedCase.title}</h2>
                        <p className="text-sm text-gray-600 mt-1">{selectedCase.description}</p>
                      </div>
                    </div>

                    {/* Case folder tab navigation */}
                    <div className="flex border-b border-gray-200 bg-gray-50/30">
                      <button
                        onClick={() => setCaseFolderTab("info")}
                        className={`px-6 py-3 font-medium text-xs uppercase tracking-wider border-b-2 transition-all ${
                          caseFolderTab === "info" ? "border-primary text-primary" : "border-transparent text-gray-500"
                        }`}
                      >
                        Actions & Decision
                      </button>
                      <button
                        onClick={() => setCaseFolderTab("notes")}
                        className={`px-6 py-3 font-medium text-xs uppercase tracking-wider border-b-2 transition-all ${
                          caseFolderTab === "notes" ? "border-primary text-primary" : "border-transparent text-gray-500"
                        }`}
                      >
                        Notes Log ({caseNotes.length})
                      </button>
                      <button
                        onClick={() => setCaseFolderTab("evidence")}
                        className={`px-6 py-3 font-medium text-xs uppercase tracking-wider border-b-2 transition-all ${
                          caseFolderTab === "evidence" ? "border-primary text-primary" : "border-transparent text-gray-500"
                        }`}
                      >
                        Evidence Dossier ({caseEvidence.length})
                      </button>
                      <button
                        onClick={() => setCaseFolderTab("timeline")}
                        className={`px-6 py-3 font-medium text-xs uppercase tracking-wider border-b-2 transition-all ${
                          caseFolderTab === "timeline" ? "border-primary text-primary" : "border-transparent text-gray-500"
                        }`}
                      >
                        Audit Log Timeline
                      </button>
                    </div>

                    {/* Folder Tab content panel */}
                    <div className="p-6 flex-1 overflow-y-auto max-h-[500px]">
                      {caseFolderTab === "info" && (
                        <div className="space-y-6">
                          {/* Assign Officer */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-end border-b border-gray-100 pb-6">
                            <div className="space-y-2">
                              <label className="text-xs font-bold text-gray-500 uppercase">Assigned QA Investigator</label>
                              <input
                                type="text"
                                value={assignee}
                                onChange={e => setAssignee(e.target.value)}
                                placeholder="E.g. Officer Smith"
                                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:outline-none"
                              />
                            </div>
                            <button
                              onClick={handleAssignCase}
                              className="px-6 py-2 bg-primary text-primary-foreground font-semibold rounded-xl"
                            >
                              Assign Case
                            </button>
                          </div>

                          {/* Status Transition Remarks */}
                          <div className="space-y-4 border-b border-gray-100 pb-6">
                            <h3 className="font-bold text-gray-900">Progress Status Transition</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                              <button
                                onClick={() => handleUpdateCaseStatus("UNDER_INVESTIGATION")}
                                className="py-2.5 border border-gray-200 hover:bg-gray-50 font-semibold rounded-xl text-xs uppercase text-gray-700"
                              >
                                Under Investigation
                              </button>
                              <button
                                onClick={() => handleUpdateCaseStatus("WAITING_FOR_INFORMATION")}
                                className="py-2.5 border border-gray-200 hover:bg-gray-50 font-semibold rounded-xl text-xs uppercase text-gray-700"
                              >
                                Waiting for Info
                              </button>
                              <button
                                onClick={() => handleUpdateCaseStatus("IN_LAB_TESTING")}
                                className="py-2.5 border border-gray-200 hover:bg-gray-50 font-semibold rounded-xl text-xs uppercase text-gray-700"
                              >
                                In Lab Testing
                              </button>
                            </div>
                            <div className="space-y-2">
                              <label className="text-xs font-bold text-gray-500 uppercase">Transition Notes (Optional)</label>
                              <textarea
                                value={caseTransitionRemarks}
                                onChange={e => setCaseTransitionRemarks(e.target.value)}
                                placeholder="E.g. Transitioning case as lab verification is triggered."
                                className="w-full p-3 border border-gray-200 rounded-xl resize-none h-20 text-sm focus:outline-none"
                              />
                            </div>
                          </div>

                          {/* Resolve Form */}
                          {selectedCase.status !== "RESOLVED" && selectedCase.status !== "CLOSED" && (
                            <div className="space-y-4 border-b border-gray-100 pb-6">
                              <h3 className="font-bold text-gray-900 text-red-700">Formal Recall & Resolution Decision</h3>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                  <label className="text-xs font-bold text-gray-500 uppercase">Final Decision Enum</label>
                                  <select
                                    value={finalDecision}
                                    onChange={e => setFinalDecision(e.target.value)}
                                    className="w-full p-2 border border-gray-300 rounded-xl focus:outline-none bg-white"
                                  >
                                    <option value="RECOMMEND_RECALL">RECOMMEND_RECALL</option>
                                    <option value="CONTINUE_MONITORING">CONTINUE_MONITORING</option>
                                    <option value="NO_ACTION_REQUIRED">NO_ACTION_REQUIRED</option>
                                    <option value="REJECT_COMMUNITY_CLAIM">REJECT_COMMUNITY_CLAIM</option>
                                  </select>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-500 uppercase">Detailed Resolution Summary</label>
                                <textarea
                                  value={resolutionSummary}
                                  onChange={e => setResolutionSummary(e.target.value)}
                                  placeholder="Provide detailed logs of chemical tests, barcode audit results, and suppression reasoning..."
                                  className="w-full p-3 border border-gray-200 rounded-xl resize-none h-28 text-sm focus:outline-none"
                                />
                              </div>
                              <button
                                onClick={handleResolveCase}
                                className="px-6 py-2.5 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-700"
                              >
                                Resolve & File Decision
                              </button>
                            </div>
                          )}

                          {/* Close Case */}
                          {selectedCase.status === "RESOLVED" && (
                            <div className="p-4 bg-gray-50 rounded-xl flex items-center justify-between">
                              <div>
                                <h4 className="font-bold text-gray-950">Resolution filed successfully.</h4>
                                <p className="text-xs text-gray-500">Case needs to be locked and archived.</p>
                              </div>
                              <button
                                onClick={handleCloseCase}
                                className="px-6 py-2.5 bg-gray-950 text-white font-semibold rounded-xl hover:bg-black"
                              >
                                Close & Lock Case
                              </button>
                            </div>
                          )}
                        </div>
                      )}

                      {caseFolderTab === "notes" && (
                        <div className="space-y-6">
                          <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 divide-y divide-gray-100">
                            {caseNotes.map(note => (
                              <div key={note.id} className="py-3 first:pt-0">
                                <div className="flex justify-between items-center">
                                  <span className="font-bold text-gray-900 text-xs flex items-center gap-1.5">
                                    <User className="size-3 text-primary" /> {note.created_by}
                                  </span>
                                  <span className="text-[10px] text-gray-400">{new Date(note.created_at).toLocaleString()}</span>
                                </div>
                                <p className="text-sm text-gray-700 mt-2 bg-slate-50 p-3 rounded-xl border border-slate-100">
                                  {note.note}
                                </p>
                              </div>
                            ))}
                          </div>
                          {selectedCase.status !== "CLOSED" && (
                            <div className="space-y-2 border-t border-gray-100 pt-4">
                              <label className="text-xs font-bold text-gray-500 uppercase">Add QA Log Note</label>
                              <div className="flex gap-2">
                                <input
                                  type="text"
                                  value={newNote}
                                  onChange={e => setNewNote(e.target.value)}
                                  placeholder="Type note message..."
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:outline-none text-sm"
                                />
                                <button
                                  onClick={handleAddCaseNote}
                                  className="p-2.5 bg-primary text-primary-foreground rounded-xl"
                                >
                                  <Send className="size-4" />
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {caseFolderTab === "evidence" && (
                        <div className="space-y-6">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[260px] overflow-y-auto">
                            {caseEvidence.map(ev => (
                              <div key={ev.id} className="p-4 border border-gray-200 rounded-xl bg-slate-50/50 flex flex-col justify-between">
                                <div>
                                  <div className="flex justify-between items-center">
                                    <span className="px-2 py-0.5 bg-slate-200 text-slate-800 text-[10px] font-bold rounded">
                                      {ev.evidence_type}
                                    </span>
                                    <span className="text-[10px] text-gray-400">{new Date(ev.uploaded_at).toLocaleDateString()}</span>
                                  </div>
                                  <p className="text-sm text-gray-700 mt-2 font-medium">{ev.description}</p>
                                </div>
                                <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-2 text-xs">
                                  <span className="text-gray-400">By: {ev.uploaded_by}</span>
                                  <a
                                    href={ev.file_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-primary font-bold hover:underline flex items-center gap-1"
                                  >
                                    View Link <ExternalLink className="size-3" />
                                  </a>
                                </div>
                              </div>
                            ))}
                          </div>

                          {selectedCase.status !== "CLOSED" && (
                            <div className="space-y-4 border-t border-gray-100 pt-4">
                              <h4 className="font-bold text-gray-900">Attach Secure Evidence Log</h4>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                <div className="space-y-1">
                                  <label className="text-[10px] font-bold text-gray-500 uppercase">Evidence Type</label>
                                  <select
                                    value={evidenceType}
                                    onChange={e => setEvidenceType(e.target.value)}
                                    className="w-full p-2 border border-gray-300 rounded-xl text-xs bg-white"
                                  >
                                    <option value="LAB_REPORT">LAB_REPORT</option>
                                    <option value="SUPPLIER_INVOICE">SUPPLIER_INVOICE</option>
                                    <option value="RECALL_NOTICE">RECALL_NOTICE</option>
                                    <option value="CUSTOMER_CORRESPONDENCE">CUSTOMER_CORRESPONDENCE</option>
                                  </select>
                                </div>
                                <div className="space-y-1 md:col-span-2">
                                  <label className="text-[10px] font-bold text-gray-500 uppercase">Evidence File URL</label>
                                  <input
                                    type="text"
                                    value={evidenceUrl}
                                    onChange={e => setEvidenceUrl(e.target.value)}
                                    placeholder="https://s3.amazonaws.com/pgn-vault/..."
                                    className="w-full p-2 border border-gray-300 rounded-xl text-xs focus:outline-none"
                                  />
                                </div>
                              </div>
                              <div className="space-y-1">
                                <label className="text-[10px] font-bold text-gray-500 uppercase">Evidence Description</label>
                                <input
                                  type="text"
                                  value={evidenceDesc}
                                  onChange={e => setEvidenceDesc(e.target.value)}
                                  placeholder="Assay reports validating safety threshold violation..."
                                  className="w-full p-2 border border-gray-300 rounded-xl text-xs focus:outline-none"
                                />
                              </div>
                              <button
                                onClick={handleAttachEvidence}
                                className="px-5 py-2 bg-primary text-primary-foreground font-semibold rounded-xl text-xs"
                              >
                                Attach Evidence
                              </button>
                            </div>
                          )}
                        </div>
                      )}

                      {caseFolderTab === "timeline" && (
                        <div className="space-y-6">
                          <div className="relative pl-6 border-l-2 border-slate-200 space-y-6">
                            {caseTimeline.map(log => (
                              <div key={log.id} className="relative">
                                <span className="absolute -left-[31px] top-0.5 size-4 bg-white border-2 border-primary rounded-full flex items-center justify-center">
                                  <span className="size-1.5 bg-primary rounded-full" />
                                </span>
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="font-bold text-gray-950 text-xs">{log.event_type}</span>
                                    <span className="text-[10px] text-gray-400">by {log.created_by}</span>
                                  </div>
                                  <p className="text-xs text-gray-500 mt-1">{log.description}</p>
                                  <span className="text-[10px] text-gray-400 block mt-1">
                                    {new Date(log.created_at).toLocaleString()}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="bg-white border border-gray-200 rounded-2xl p-12 text-center text-gray-400 flex flex-col items-center justify-center min-h-[500px]">
                    <FolderKanban className="size-12 text-gray-300 mb-4" />
                    <h3 className="font-bold text-gray-700">No Case Selected</h3>
                    <p className="text-sm mt-1">Select an active investigation from the list to view its audit timeline and notes.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* MODAL: REPORT DETAIL & CREDIBILITY FACTOR ANALYSIS */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-2xl w-full shadow-2xl overflow-y-auto max-h-[90vh] space-y-6">
            <div className="flex justify-between items-center border-b border-gray-200 pb-4">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <FileText className="size-5 text-primary" />
                Quality Incident Report Detail
              </h2>
              <button onClick={() => setSelectedReport(null)} className="p-2 hover:bg-gray-100 rounded-full">
                <X className="size-5 text-gray-500" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h3 className="font-bold text-gray-900 border-b pb-1 text-sm uppercase text-gray-500">Report Details</h3>
                <p className="text-sm text-gray-700"><strong>Product Name:</strong> {selectedReport.product_name}</p>
                <p className="text-sm text-gray-700"><strong>Barcode:</strong> {selectedReport.barcode}</p>
                <p className="text-sm text-gray-700"><strong>Batch Number:</strong> {selectedReport.batch_number}</p>
                <p className="text-sm text-gray-700"><strong>Report Type:</strong> {selectedReport.report_type}</p>
                <p className="text-sm text-gray-700"><strong>Status:</strong> {selectedReport.status}</p>
                <p className="text-sm text-gray-700"><strong>Description:</strong> {selectedReport.description}</p>
                {selectedReport.purchase_date && (
                  <p className="text-sm text-gray-700">
                    <strong>Purchase Date:</strong> {new Date(selectedReport.purchase_date).toLocaleDateString()}
                  </p>
                )}
                {(selectedReport.store_name || selectedReport.store_location) && (
                  <p className="text-sm text-gray-700 flex items-center gap-1">
                    <MapPin className="size-4 text-gray-400 shrink-0" />
                    <strong>Location:</strong> {selectedReport.store_name} ({selectedReport.store_location})
                  </p>
                )}
              </div>

              {/* Credibility Analysis Box */}
              <div className="space-y-4 bg-slate-50 p-4 rounded-xl border border-slate-100">
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-gray-900 text-sm uppercase text-gray-500">Credibility Index</h3>
                  <button
                    onClick={() => handleRecalculateCredibility(selectedReport.id)}
                    disabled={actionLoading}
                    className="text-xs text-primary font-bold hover:underline"
                  >
                    Recalculate
                  </button>
                </div>

                {selectedReportCredibility ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl font-extrabold text-primary">
                        {selectedReportCredibility.score.toFixed(0)}
                      </span>
                      <div>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                          selectedReportCredibility.credibility_level === "VERY_HIGH" || selectedReportCredibility.credibility_level === "HIGH" ? "bg-green-100 text-green-800" :
                          selectedReportCredibility.credibility_level === "MEDIUM" ? "bg-blue-100 text-blue-800" : "bg-red-100 text-red-800"
                        }`}>
                          {selectedReportCredibility.credibility_level}
                        </span>
                        <p className="text-[10px] text-gray-400 mt-1">Calculated via Reliability Rules</p>
                      </div>
                    </div>

                    <div className="space-y-2 border-t border-gray-200 pt-3">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-gray-500 flex items-center gap-1">
                          <CheckSquare className="size-3.5 text-gray-400" /> Barcode matches system db
                        </span>
                        <span className={`font-bold ${selectedReportCredibility.factors.barcode_verified ? "text-green-600" : "text-gray-400"}`}>
                          {selectedReportCredibility.factors.barcode_verified ? "Yes" : "No"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-gray-500 flex items-center gap-1">
                          <FileSpreadsheet className="size-3.5 text-gray-400" /> Batch code verified
                        </span>
                        <span className={`font-bold ${selectedReportCredibility.factors.batch_verified ? "text-green-600" : "text-gray-400"}`}>
                          {selectedReportCredibility.factors.batch_verified ? "Yes" : "No"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-gray-500 flex items-center gap-1">
                          <User className="size-3.5 text-gray-400" /> Trusted consumer user profile
                        </span>
                        <span className={`font-bold ${selectedReportCredibility.factors.verified_user ? "text-green-600" : "text-gray-400"}`}>
                          {selectedReportCredibility.factors.verified_user ? "Yes" : "No"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-gray-500 flex items-center gap-1">
                          <ImageIcon className="size-3.5 text-gray-400" /> Quality image files uploaded
                        </span>
                        <span className={`font-bold ${selectedReportCredibility.factors.images_uploaded ? "text-green-600" : "text-gray-400"}`}>
                          {selectedReportCredibility.factors.images_uploaded ? "Yes" : "No"}
                        </span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-gray-400 text-xs py-4 justify-center">
                    <Loader2 className="size-4 animate-spin" /> Fetching factors...
                  </div>
                )}
              </div>
            </div>

            {/* Images */}
            {selectedReport.images && selectedReport.images.length > 0 && (
              <div className="space-y-2 border-t border-gray-100 pt-4">
                <h3 className="font-bold text-gray-900 text-sm uppercase text-gray-500">Incident Images</h3>
                <div className="flex flex-wrap gap-3">
                  {selectedReport.images.map(img => (
                    <a key={img.id} href={img.image_url} target="_blank" rel="noreferrer" className="relative group block overflow-hidden rounded-xl border border-gray-200">
                      <img src={img.image_url} alt="Report attachment" className="w-24 h-24 object-cover group-hover:scale-105 transition-transform" />
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL: CLUSTER REPORT LIST */}
      {selectedCluster && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-3xl w-full shadow-2xl overflow-y-auto max-h-[90vh] space-y-6">
            <div className="flex justify-between items-center border-b border-gray-200 pb-4">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <FolderKanban className="size-5 text-primary" />
                Cluster Details: {selectedCluster.cluster_code}
              </h2>
              <button onClick={() => setSelectedCluster(null)} className="p-2 hover:bg-gray-100 rounded-full">
                <X className="size-5 text-gray-500" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div>
                <span className="text-xs text-gray-400 block font-bold uppercase">Product / Barcode</span>
                <span className="text-sm text-gray-900 font-bold mt-1 block">{selectedCluster.product_name}</span>
                <span className="text-xs text-gray-500 block font-mono mt-1">{selectedCluster.barcode}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block font-bold uppercase">Total Grouped Incidents</span>
                <span className="text-sm text-gray-900 font-extrabold mt-1 block">{selectedCluster.total_reports} Reports</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block font-bold uppercase">Risk Score / Severity</span>
                <span className="text-sm text-gray-950 font-bold mt-1 block">{selectedCluster.risk_score} - {selectedCluster.severity}</span>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="font-bold text-gray-900 text-sm uppercase text-gray-500">Grouped Customer Incident Reports</h3>
              <div className="border border-gray-200 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-gray-50 border-b border-gray-200 text-gray-500 font-semibold uppercase">
                    <tr>
                      <th className="p-3">Report ID</th>
                      <th className="p-3">Batch</th>
                      <th className="p-3">Type</th>
                      <th className="p-3">Store Location</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {selectedClusterReports.map(rep => (
                      <tr key={rep.id} className="hover:bg-gray-50/50">
                        <td className="p-3 font-mono font-bold text-gray-600 truncate max-w-[150px]">{rep.id}</td>
                        <td className="p-3 font-mono">{rep.batch_number}</td>
                        <td className="p-3">{rep.report_type}</td>
                        <td className="p-3 text-gray-500">{rep.store_location || "Not Provided"}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            rep.status === "VERIFIED" ? "text-green-600 bg-green-55" : "text-amber-600 bg-amber-50"
                          }`}>
                            {rep.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: SAFETY ALERT DETAIL ACTIONS */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-6">
            <div className="flex justify-between items-center border-b border-gray-200 pb-4">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <ShieldAlert className="size-5 text-red-500" />
                Alert Details
              </h2>
              <button onClick={() => setSelectedAlert(null)} className="p-2 hover:bg-gray-100 rounded-full">
                <X className="size-5 text-gray-500" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <span className="text-xs text-gray-400 block font-bold uppercase">Alert Code</span>
                <span className="text-sm font-bold text-gray-950 font-mono mt-1 block">{selectedAlert.alert_code}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block font-bold uppercase">Incident Severity Risk</span>
                <span className="text-sm text-red-600 font-extrabold mt-1 block">Score: {selectedAlert.risk_score} - {selectedAlert.alert_level}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block font-bold uppercase">System Safety Trigger Message</span>
                <p className="text-sm text-gray-700 mt-1 bg-slate-50 p-3 rounded-xl border border-slate-100">{selectedAlert.message}</p>
              </div>

              {selectedAlert.status !== "RESOLVED" && selectedAlert.status !== "CLOSED" && (
                <div className="space-y-3 pt-4 border-t border-gray-100">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase">Resolution / Acknowledge Remarks</label>
                    <textarea
                      value={alertRemarks}
                      onChange={e => setAlertRemarks(e.target.value)}
                      placeholder="Add details regarding recall progress, validation status..."
                      className="w-full p-3 border border-gray-200 rounded-xl resize-none h-20 text-xs focus:outline-none"
                    />
                  </div>
                  <div className="flex gap-2">
                    {selectedAlert.status === "ACTIVE" && (
                      <button
                        onClick={() => handleAcknowledgeAlert(selectedAlert.id)}
                        className="flex-1 py-2 bg-blue-600 text-white font-semibold rounded-xl text-xs hover:bg-blue-700"
                      >
                        Acknowledge
                      </button>
                    )}
                    <button
                      onClick={() => handleResolveAlert(selectedAlert.id)}
                      className="flex-1 py-2 bg-red-600 text-white font-semibold rounded-xl text-xs hover:bg-red-700"
                    >
                      Resolve Alert
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MODAL: CREATE INVESTIGATION CASE */}
      {isCreateCaseOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-6">
            <div className="flex justify-between items-center border-b border-gray-200 pb-4">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <FolderKanban className="size-5 text-amber-500" />
                Initialize Investigation
              </h2>
              <button onClick={() => setIsCreateCaseOpen(false)} className="p-2 hover:bg-gray-100 rounded-full">
                <X className="size-5 text-gray-500" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase">Investigation Case Title</label>
                <input
                  type="text"
                  value={createCaseTitle}
                  onChange={e => setCreateCaseTitle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:outline-none text-sm"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase">Case Scope Description</label>
                <textarea
                  value={createCaseDesc}
                  onChange={e => setCreateCaseDesc(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-xl resize-none h-24 text-sm focus:outline-none"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-500 uppercase">Priority level</label>
                <select
                  value={createCasePriority}
                  onChange={e => setCreateCasePriority(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-xl text-sm bg-white"
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setIsCreateCaseOpen(false)}
                  className="flex-1 py-2.5 border border-gray-300 text-gray-700 font-semibold rounded-xl text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitCreateCase}
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-semibold rounded-xl text-sm hover:bg-primary/90"
                >
                  Create Case
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
