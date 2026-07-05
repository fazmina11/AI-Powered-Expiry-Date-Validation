"use client";

import { useState, useEffect } from "react";
import {
  ArrowLeft,
  Shield,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Loader2,
  Calendar,
  MapPin,
  FileText,
  BadgeAlert,
  User,
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

const getImageUrl = (url: string) => {
  if (!url) return "";
  if (url.startsWith("http")) return url;
  return `http://localhost:8001${url}`;
};

export default function ReportDetailsPage({ params }: { params: { id: string } }) {
  const { id } = params;

  const [report, setReport] = useState<ProductReport | null>(null);
  const [credibility, setCredibility] = useState<CredibilityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const reportRes = await apiFetch<ProductReport>(`/community/reports/${id}`);
      setReport(reportRes);

      try {
        const credRes = await apiFetch<{ data: CredibilityResponse } | CredibilityResponse>(`/community/reports/${id}/credibility`);
        const credData = "data" in credRes ? credRes.data : credRes;
        setCredibility(credData);
      } catch (credErr) {
        console.error("Credibility fetch error:", credErr);
      }
    } catch (err: any) {
      setError(err.message || "Failed to retrieve report data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleRecalculate = async () => {
    setRecalculating(true);
    try {
      const res = await apiFetch<{ data: CredibilityResponse } | CredibilityResponse>(`/community/reports/${id}/recalculate`, {
        method: "POST",
      });
      const credData = "data" in res ? res.data : res;
      setCredibility(credData);
      alert("Credibility successfully recalculated via CSAE Rules!");
    } catch (err: any) {
      alert("Credibility calculation failed: " + err.message);
    } finally {
      setRecalculating(false);
    }
  };

  if (loading && !report) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-500 space-y-4">
        <Loader2 className="size-10 animate-spin text-blue-600" />
        <p className="text-sm font-semibold">Performing integrity check & audit load...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="p-8 max-w-3xl mx-auto space-y-6">
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
          <XCircle className="size-5 shrink-0" />
          <span>{error || "Report not found."}</span>
        </div>
        <Link href="/community/reports" className="inline-flex items-center gap-2 text-sm text-blue-600 font-bold hover:underline">
          <ArrowLeft className="size-4" /> Back to reports list
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-8 max-w-7xl mx-auto">
      {/* Breadcrumbs & Header */}
      <div className="space-y-4">
        <Link
          href="/community/reports"
          className="inline-flex items-center gap-2 text-xs text-gray-500 hover:text-blue-600 transition-colors font-bold uppercase tracking-wider"
        >
          <ArrowLeft className="size-4" /> Back to reports list
        </Link>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-950 flex items-center gap-3">
              <Shield className="size-8 text-blue-600" />
              Incident Audit: {report.product_name}
            </h1>
            <p className="text-sm text-gray-500 font-mono mt-1">Report ID: {report.id}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border ${
            report.status === "VERIFIED" ? "text-green-700 bg-green-50 border-green-200" :
            report.status === "REJECTED" ? "text-red-700 bg-red-50 border-red-200" : "text-amber-700 bg-amber-50 border-amber-200"
          }`}>
            Status: {report.status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Report Details & Images */}
        <div className="lg:col-span-2 space-y-8">
          {/* Card: Core Details */}
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
            <h3 className="text-lg font-bold text-gray-900 border-b border-gray-100 pb-3 flex items-center gap-2">
              <FileText className="size-5 text-gray-500" />
              Quality Incident Summary
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Product Name</span>
                <p className="text-sm font-semibold text-gray-900 mt-1">{report.product_name}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Barcode</span>
                <p className="text-sm font-mono text-gray-900 mt-1">{report.barcode}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Batch Number</span>
                <p className="text-sm font-mono text-gray-900 mt-1">{report.batch_number}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Report Type</span>
                <p className="text-sm font-semibold mt-1">
                  <span className="px-2.5 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded-full text-xs">
                    {report.report_type}
                  </span>
                </p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Severity Level</span>
                <p className="text-sm mt-1">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase ${
                    report.severity === "CRITICAL" ? "text-red-700 bg-red-50 border border-red-200" :
                    report.severity === "HIGH" ? "text-amber-700 bg-amber-50 border border-amber-200" : "text-blue-700 bg-blue-50 border border-blue-200"
                  }`}>
                    {report.severity}
                  </span>
                </p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Date Reported</span>
                <p className="text-sm text-gray-800 mt-1 flex items-center gap-1.5">
                  <Calendar className="size-4 text-gray-400" />
                  {new Date(report.created_at).toLocaleString()}
                </p>
              </div>
            </div>

            <div className="border-t border-gray-100 pt-6">
              <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Store & Purchase Info</span>
              <div className="mt-2 flex flex-col md:flex-row gap-4 md:gap-8 text-sm text-gray-700">
                <div className="flex items-center gap-2">
                  <MapPin className="size-4 text-gray-400" />
                  <span>{report.store_name || "N/A"} - {report.store_location || "N/A"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="size-4 text-gray-400" />
                  <span>Purchase Date: {report.purchase_date ? new Date(report.purchase_date).toLocaleDateString() : "N/A"}</span>
                </div>
              </div>
            </div>

            <div className="border-t border-gray-100 pt-6">
              <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider font-mono">Narrative Description</span>
              <p className="text-sm text-gray-700 mt-2 bg-gray-50 p-4 rounded-xl border border-gray-200 leading-relaxed font-mono">
                {report.description}
              </p>
            </div>
          </div>

          {/* Card: Images Evidence */}
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold text-gray-900 border-b border-gray-100 pb-3 flex items-center gap-2">
              <BadgeAlert className="size-5 text-gray-500" />
              Incident Visual Evidence ({report.images.length})
            </h3>
            {report.images.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 pt-2">
                {report.images.map((img) => (
                  <div key={img.id} className="relative aspect-video rounded-xl overflow-hidden border border-gray-200 bg-gray-55 shadow-sm group">
                    <img
                      src={getImageUrl(img.image_url)}
                      alt="Quality Defect Evidence File"
                      className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-10 text-gray-400 text-sm">No images attached with this quality complaint.</div>
            )}
          </div>
        </div>

        {/* Right Col: Credibility scorecard */}
        <div className="space-y-8">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
            <div className="flex justify-between items-center border-b border-gray-100 pb-3">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Shield className="size-5 text-blue-600" />
                CRCE Reliability
              </h3>
              <button
                onClick={handleRecalculate}
                disabled={recalculating}
                className="p-1.5 hover:bg-gray-100 rounded-lg text-blue-600 transition-colors disabled:opacity-50"
                title="Recalculate Reliability Score"
              >
                {recalculating ? <Loader2 className="size-4 animate-spin" /> : <RefreshCw className="size-4" />}
              </button>
            </div>

            {credibility ? (
              <div className="space-y-6">
                {/* Score Circle Gauge */}
                <div className="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-2xl border border-gray-200/80">
                  <div className="relative size-24 flex items-center justify-center">
                    <svg className="absolute inset-0 size-full -rotate-90">
                      <circle cx="48" cy="48" r="40" className="stroke-gray-200 fill-none" strokeWidth="8"></circle>
                      <circle
                        cx="48"
                        cy="48"
                        r="40"
                        className="stroke-blue-600 fill-none transition-all duration-500"
                        strokeWidth="8"
                        strokeDasharray={251}
                        strokeDashoffset={251 - (251 * credibility.score) / 100}
                        strokeLinecap="round"
                      ></circle>
                    </svg>
                    <span className="text-2xl font-black text-gray-950">{credibility.score}%</span>
                  </div>
                  <p className="text-sm font-bold text-gray-900 mt-4 tracking-wide uppercase">
                    Level: {credibility.credibility_level}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">Consumer credibility assessment</p>
                </div>

                {/* Factors checklist */}
                <div className="space-y-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                    Credibility Rule Checklist
                  </span>
                  {[
                    { key: "barcode_verified", label: "Product Barcode Matches Register" },
                    { key: "batch_verified", label: "Valid Batch Identification Code" },
                    { key: "verified_user", label: "Trusted User Credibility Rating" },
                    { key: "images_uploaded", label: "ComplComplimentary Visual Evidence File" },
                    { key: "receipt_uploaded", label: "Purchase Invoice Receipt Scanned" },
                    { key: "location_available", label: "Incident Location Logs Verified" },
                  ].map((factor) => {
                    const isPassed = credibility.factors[factor.key as keyof CredibilityFactors];
                    return (
                      <div key={factor.key} className="flex items-center justify-between text-xs text-gray-700 bg-gray-55/40 px-3 py-2 rounded-xl border border-gray-100">
                        <span>{factor.label}</span>
                        {isPassed ? (
                          <CheckCircle2 className="size-4 text-green-600 shrink-0" />
                        ) : (
                          <XCircle className="size-4 text-red-500 shrink-0" />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-gray-400 text-sm">
                No credibility score compiled yet. Click refresh to evaluate.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
