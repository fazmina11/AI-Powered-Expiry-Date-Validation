"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Package,
  Calendar,
  MapPin,
  AlertTriangle,
  CheckCircle2,
  Clock,
  XCircle,
  Shield,
  User,
  FileText,
  Camera,
  ArrowLeft,
  Loader2,
  Info,
  ChevronRight,
  Clipboard,
} from "lucide-react";
import { apiFetch } from "@/services/apiService";
import { cn } from "@/lib/utils";

// ─── Types ───────────────────────────────────────────────────────────────────

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

// ─── Status Config ────────────────────────────────────────────────────────────

interface StatusStep {
  key: string;
  label: string;
  desc: string;
  icon: React.ElementType;
  activeColor: string;
  completedColor: string;
}

const STATUS_TIMELINE: StatusStep[] = [
  {
    key: "PENDING",
    label: "Report Submitted",
    desc: "Your report has been received and is in our queue.",
    icon: FileText,
    activeColor: "text-blue-600 bg-blue-50 border-blue-200",
    completedColor: "text-green-600 bg-green-50 border-green-200",
  },
  {
    key: "UNDER_REVIEW",
    label: "Report Verified",
    desc: "Our safety team is reviewing your report for accuracy and completeness.",
    icon: Shield,
    activeColor: "text-blue-600 bg-blue-50 border-blue-200",
    completedColor: "text-green-600 bg-green-50 border-green-200",
  },
  {
    key: "VERIFIED",
    label: "Investigation Started",
    desc: "A formal investigation has been opened by our product safety team.",
    icon: AlertTriangle,
    activeColor: "text-amber-600 bg-amber-50 border-amber-200",
    completedColor: "text-green-600 bg-green-50 border-green-200",
  },
  {
    key: "RESOLVED",
    label: "Investigation Completed",
    desc: "The investigation is complete and corrective actions have been taken.",
    icon: CheckCircle2,
    activeColor: "text-green-600 bg-green-50 border-green-200",
    completedColor: "text-green-600 bg-green-50 border-green-200",
  },
  {
    key: "CLOSED",
    label: "Case Closed",
    desc: "This report has been closed. Thank you for contributing to consumer safety.",
    icon: CheckCircle2,
    activeColor: "text-green-600 bg-green-50 border-green-200",
    completedColor: "text-green-600 bg-green-50 border-green-200",
  },
];

const STATUS_ORDER: Record<string, number> = {
  PENDING: 0,
  UNDER_REVIEW: 1,
  VERIFIED: 2,
  RESOLVED: 3,
  REJECTED: 4,
};

function getStatusConfig(status: string) {
  switch (status) {
    case "PENDING":
      return { label: "Submitted", color: "bg-gray-100 text-gray-700", dot: "bg-gray-500" };
    case "UNDER_REVIEW":
      return { label: "Under Review", color: "bg-blue-100 text-blue-700", dot: "bg-blue-500" };
    case "VERIFIED":
      return { label: "Investigation Open", color: "bg-amber-100 text-amber-700", dot: "bg-amber-500" };
    case "RESOLVED":
      return { label: "Resolved", color: "bg-green-100 text-green-700", dot: "bg-green-500" };
    case "REJECTED":
      return { label: "Closed", color: "bg-red-100 text-red-700", dot: "bg-red-500" };
    default:
      return { label: status, color: "bg-gray-100 text-gray-700", dot: "bg-gray-400" };
  }
}

const ISSUE_TYPE_LABELS: Record<string, string> = {
  LEAKAGE: "💧 Leakage / Spillage",
  WRONG_PRODUCT: "🔄 Wrong Product",
  DAMAGED_PACKAGING: "📦 Damaged Packaging",
  FOREIGN_OBJECT: "⚠️ Foreign Object Found",
  EXPIRED_PRODUCT: "📅 Expired Product",
  BAD_SMELL: "👃 Bad Smell / Odour",
  CONTAMINATION: "☣️ Contamination",
  OTHER: "❓ Other Issue",
};

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function DetailSkeleton() {
  return (
    <div className="space-y-6 animate-pulse py-8">
      <div className="h-8 bg-gray-200 rounded w-64" />
      <div className="h-6 bg-gray-200 rounded-full w-28" />
      <div className="bg-white rounded-2xl p-6 space-y-4 border border-gray-100">
        <div className="h-5 bg-gray-200 rounded w-40" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-4">
            <div className="h-4 bg-gray-200 rounded w-24" />
            <div className="h-4 bg-gray-200 rounded flex-1" />
          </div>
        ))}
      </div>
      <div className="bg-white rounded-2xl p-6 border border-gray-100 space-y-4">
        <div className="h-5 bg-gray-200 rounded w-36" />
        {STATUS_TIMELINE.map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0" />
            <div className="flex-1 space-y-2 pt-1">
              <div className="h-4 bg-gray-200 rounded w-40" />
              <div className="h-3 bg-gray-200 rounded w-full" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Section Card ─────────────────────────────────────────────────────────────

function SectionCard({
  title,
  icon: Icon,
  iconColor,
  children,
}: {
  title: string;
  icon: React.ElementType;
  iconColor: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center gap-2">
        <Icon className={cn("w-5 h-5", iconColor)} />
        <h2 className="font-semibold text-gray-900 text-sm">{title}</h2>
      </div>
      <div className="p-6">{children}</div>
    </div>
  );
}

function InfoRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex gap-3 py-2.5 border-b border-gray-100 last:border-0">
      <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider w-32 flex-shrink-0 pt-0.5">
        {label}
      </span>
      <span className={cn("text-sm text-gray-900 flex-1", mono && "font-mono text-gray-700")}>
        {value || "—"}
      </span>
    </div>
  );
}

// ─── Status Timeline Component ─────────────────────────────────────────────────

function StatusTimeline({ status }: { status: string }) {
  const currentOrder = STATUS_ORDER[status] ?? -1;
  const isRejected = status === "REJECTED";

  return (
    <div className="space-y-0">
      {isRejected ? (
        // Special case for rejected
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex gap-3">
          <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-700">Report Closed</p>
            <p className="text-sm text-red-600 mt-1">
              After review, your report could not be verified with the available information.
              You may submit a new report with additional evidence.
            </p>
          </div>
        </div>
      ) : (
        STATUS_TIMELINE.map((step, i) => {
          const stepOrder = STATUS_ORDER[step.key] ?? i;
          const isCompleted = currentOrder > stepOrder;
          const isActive = currentOrder === stepOrder;
          const isPending = currentOrder < stepOrder;
          const Icon = step.icon;

          return (
            <div key={step.key} className="flex gap-4">
              {/* Icon + Line */}
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    "w-9 h-9 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all",
                    isCompleted
                      ? "border-green-400 bg-green-500 text-white"
                      : isActive
                      ? "border-blue-400 bg-blue-500 text-white shadow-md shadow-blue-200"
                      : "border-gray-200 bg-gray-50 text-gray-300"
                  )}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : (
                    <Icon className={cn("w-4 h-4", isActive && "animate-pulse")} />
                  )}
                </div>
                {i < STATUS_TIMELINE.length - 1 && (
                  <div
                    className={cn(
                      "w-0.5 h-8 my-1 rounded transition-all",
                      isCompleted ? "bg-green-300" : "bg-gray-200"
                    )}
                  />
                )}
              </div>

              {/* Content */}
              <div className={cn(
                "pb-6 flex-1 pt-1",
                isPending && "opacity-40"
              )}>
                <div className="flex items-center gap-2 mb-1">
                  <h4 className={cn(
                    "font-semibold text-sm",
                    isCompleted ? "text-green-700" : isActive ? "text-blue-700" : "text-gray-400"
                  )}>
                    {step.label}
                  </h4>
                  {isActive && (
                    <span className="flex items-center gap-1 text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                      Current
                    </span>
                  )}
                  {isCompleted && (
                    <span className="text-xs text-green-600 font-medium">✓ Done</span>
                  )}
                </div>
                <p className="text-xs text-gray-500 leading-relaxed">{step.desc}</p>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}

// ─── What Happens Next ────────────────────────────────────────────────────────

function WhatHappensNext({ status }: { status: string }) {
  const messages: Record<string, { msg: string; icon: React.ElementType; color: string }> = {
    PENDING: {
      msg: "Your report is in our queue. Our safety team will begin reviewing it within 24 hours.",
      icon: Clock,
      color: "text-blue-600 bg-blue-50 border-blue-200",
    },
    UNDER_REVIEW: {
      msg: "Our safety team is actively reviewing your report. If additional information is needed, you may be contacted.",
      icon: Shield,
      color: "text-blue-700 bg-blue-50 border-blue-200",
    },
    VERIFIED: {
      msg: "A formal product safety investigation has been launched. Our officers will conduct a thorough examination.",
      icon: AlertTriangle,
      color: "text-amber-700 bg-amber-50 border-amber-200",
    },
    RESOLVED: {
      msg: "The investigation is complete. Corrective actions have been recommended and implemented where appropriate.",
      icon: CheckCircle2,
      color: "text-green-700 bg-green-50 border-green-200",
    },
    REJECTED: {
      msg: "This report could not be verified. You may submit a new report with additional photos or evidence.",
      icon: Info,
      color: "text-red-700 bg-red-50 border-red-200",
    },
  };

  const config = messages[status] || messages["PENDING"];
  const Icon = config.icon;

  return (
    <div className={cn("rounded-xl border p-4 flex gap-3", config.color)}>
      <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
      <div>
        <p className="font-semibold text-sm mb-0.5">What happens next?</p>
        <p className="text-sm leading-relaxed">{config.msg}</p>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function ReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const reportId = params.id as string;

  const [report, setReport] = useState<ProductReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [investigationCase, setInvestigationCase] = useState<any | null>(null);
  const [latestUpdate, setLatestUpdate] = useState<string | null>(null);

  const fetchCaseDetails = async (barcode: string, batchNumber: string) => {
    try {
      // 1. Fetch clusters
      const clustersRes = await apiFetch<any>("/community/clusters?limit=100");
      const clustersList = Array.isArray(clustersRes) ? clustersRes : (clustersRes.data || []);
      
      const matchingCluster = clustersList.find(
        (c: any) => c.barcode === barcode && c.batch_number === batchNumber
      );
      
      if (matchingCluster) {
        // 2. Fetch cases for this cluster
        const casesRes = await apiFetch<any>(`/community/cases?cluster_id=${matchingCluster.id}`);
        const casesList = Array.isArray(casesRes) ? casesRes : (casesRes.data || []);
        
        if (casesList.length > 0) {
          const caseObj = casesList[0];
          setInvestigationCase(caseObj);
          
          // Determine latest update
          if (caseObj.notes && caseObj.notes.length > 0) {
            const sortedNotes = [...caseObj.notes].sort(
              (a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );
            setLatestUpdate(sortedNotes[0].note);
          } else if (caseObj.timeline && caseObj.timeline.length > 0) {
            const sortedTimeline = [...caseObj.timeline].sort(
              (a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );
            setLatestUpdate(sortedTimeline[0].event_description || sortedTimeline[0].description);
          }
        }
      }
    } catch (err) {
      console.error("Error fetching case details:", err);
    }
  };

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch<any>(`/community/reports/${reportId}`);
        const reportData = res.data || res;
        setReport(reportData);
        if (reportData) {
          fetchCaseDetails(reportData.barcode, reportData.batch_number);
        }
      } catch (e: any) {
        setError("We couldn't find this report. It may have been removed or the link is invalid.");
      } finally {
        setLoading(false);
      }
    };
    if (reportId) fetchReport();
  }, [reportId]);

  const copyReportId = () => {
    navigator.clipboard.writeText(report?.id || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto">
        <DetailSkeleton />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-2xl mx-auto py-16 text-center">
        <div className="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
          <XCircle className="w-10 h-10 text-red-400" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Report Not Found</h2>
        <p className="text-gray-500 mb-8 max-w-sm mx-auto">{error}</p>
        <button
          onClick={() => router.push("/community/my-reports")}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-all"
        >
          Back to My Reports
        </button>
      </div>
    );
  }

  const statusConfig = getStatusConfig(report.status);

  return (
    <div className="py-8">
      <div className="max-w-2xl mx-auto">
        {/* Back button */}
        <button
          onClick={() => router.push("/community/my-reports")}
          className="flex items-center gap-2 text-gray-500 hover:text-blue-600 transition-colors mb-6 group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">Back to My Reports</span>
        </button>

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{report.product_name}</h1>
            <div className="flex items-center gap-2 mt-2">
              <span className={cn(
                "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold",
                statusConfig.color
              )}>
                <span className={cn("w-1.5 h-1.5 rounded-full animate-pulse", statusConfig.dot)} />
                {statusConfig.label}
              </span>
              <span className="text-xs text-gray-400">
                Submitted {new Date(report.created_at).toLocaleDateString("en-IN", {
                  day: "numeric", month: "long", year: "numeric"
                })}
              </span>
            </div>
          </div>

          {/* Report ID Copy */}
          <button
            onClick={copyReportId}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl text-sm font-mono text-gray-600 transition-all"
          >
            <Clipboard className="w-4 h-4" />
            {copied ? "Copied!" : `#${report.id.substring(0, 8).toUpperCase()}`}
          </button>
        </div>

        <div className="space-y-5">
          {/* What Happens Next */}
          <WhatHappensNext status={report.status} />

          {/* Progress Tracker */}
          <SectionCard title="Investigation Status" icon={Shield} iconColor="text-blue-600">
            <StatusTimeline status={report.status} />
          </SectionCard>

          {/* Investigation Updates */}
          {investigationCase && (
            <SectionCard title="Investigation Updates" icon={Shield} iconColor="text-blue-600">
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Assigned Officer</span>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-600">
                        <User className="w-4 h-4" />
                      </div>
                      <span className="text-sm font-medium text-gray-900">
                        {investigationCase.assigned_officer || "Assigning officer..."}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Latest Status</span>
                    <p className="text-sm font-medium text-gray-900 mt-1.5 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                      {investigationCase.status}
                    </p>
                  </div>
                </div>

                {latestUpdate && (
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Latest Update</span>
                    <div className="mt-1 bg-gray-50 rounded-xl p-3.5 border border-gray-100 text-sm text-gray-700 leading-relaxed">
                      {latestUpdate}
                    </div>
                  </div>
                )}

                {investigationCase.resolution && (
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Resolution Summary</span>
                    <div className="mt-1 bg-green-50/50 rounded-xl p-3.5 border border-green-100 text-sm text-green-800 leading-relaxed">
                      {investigationCase.resolution}
                    </div>
                  </div>
                )}

                {investigationCase.final_decision && (
                  <div>
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Recommendations / Decision</span>
                    <div className="mt-1">
                      <span className="text-sm font-semibold text-blue-700 bg-blue-50 px-3 py-2 rounded-lg inline-block">
                        📢 {investigationCase.final_decision.replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </SectionCard>
          )}

          {/* Product Information */}
          <SectionCard title="Product Information" icon={Package} iconColor="text-blue-600">
            <div>
              <InfoRow label="Product" value={report.product_name} />
              <InfoRow label="Barcode" value={report.barcode} mono />
              <InfoRow label="Batch No." value={report.batch_number || "Not provided"} mono />
              <InfoRow
                label="Purchase Date"
                value={report.purchase_date
                  ? new Date(report.purchase_date).toLocaleDateString("en-IN", {
                    day: "numeric", month: "long", year: "numeric"
                  })
                  : "Not provided"
                }
              />
              <InfoRow
                label="Store"
                value={report.store_name
                  ? `${report.store_name}${report.store_location ? `, ${report.store_location}` : ""}`
                  : "Not provided"
                }
              />
            </div>
          </SectionCard>

          {/* Issue Description */}
          <SectionCard title="Issue Details" icon={AlertTriangle} iconColor="text-amber-500">
            <div className="space-y-4">
              <div>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Issue Type</span>
                <p className="mt-1 font-medium text-gray-900">
                  {ISSUE_TYPE_LABELS[report.report_type] || report.report_type}
                </p>
              </div>
              <div>
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Description</span>
                <p className="mt-2 text-sm text-gray-700 leading-relaxed bg-gray-50 rounded-xl p-4 border border-gray-100">
                  {report.description}
                </p>
              </div>
            </div>
          </SectionCard>

          {/* Evidence */}
          {report.images && report.images.length > 0 && (
            <SectionCard title={`Evidence Photos (${report.images.length})`} icon={Camera} iconColor="text-violet-500">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {report.images.map((img, i) => (
                  <button
                    key={img.id}
                    onClick={() => setSelectedImage(img.image_url)}
                    className="relative aspect-square rounded-xl overflow-hidden bg-gray-100 border border-gray-200 hover:border-blue-400 transition-all group"
                  >
                    <img
                      src={img.image_url}
                      alt={`Evidence ${i + 1}`}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect fill="%23f3f4f6" width="100" height="100"/><text x="50" y="55" font-size="12" text-anchor="middle" fill="%236b7280">Photo ${i + 1}</text></svg>`;
                      }}
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                  </button>
                ))}
              </div>
            </SectionCard>
          )}

          {report.images && report.images.length === 0 && (
            <div className="bg-gray-50 rounded-2xl border border-gray-100 p-5 flex items-center gap-3">
              <Camera className="w-5 h-5 text-gray-300 flex-shrink-0" />
              <p className="text-sm text-gray-400 italic">No evidence photos were attached to this report</p>
            </div>
          )}

          {/* Submission Info */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>Submitted {new Date(report.created_at).toLocaleString("en-IN", {
                  day: "numeric", month: "short", year: "numeric",
                  hour: "2-digit", minute: "2-digit"
                })}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <User className="w-4 h-4" />
                <span>Community Reporter</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <FileText className="w-4 h-4" />
                <span className="font-mono text-xs">{report.id}</span>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="flex gap-3">
            <button
              onClick={() => router.push("/community/my-reports")}
              className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
              All Reports
            </button>
            <a
              href="/community/report"
              className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md transition-all"
            >
              <Shield className="w-4 h-4" />
              New Report
              <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      {/* Image Lightbox */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-3xl max-h-full" onClick={(e) => e.stopPropagation()}>
            <img
              src={selectedImage}
              alt="Evidence"
              className="max-w-full max-h-[85vh] rounded-2xl object-contain shadow-2xl"
            />
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-4 -right-4 w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-lg hover:bg-gray-100 transition-colors"
            >
              <XCircle className="w-6 h-6 text-gray-700" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
