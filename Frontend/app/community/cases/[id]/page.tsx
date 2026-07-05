"use client";

import { useState, useEffect, use } from "react";
import {
  ArrowLeft,
  FolderKanban,
  Loader2,
  Calendar,
  XCircle,
  FileText,
  User,
  ShieldAlert,
  Send,
  Clock,
  ExternalLink,
  BookOpen,
  Paperclip,
  CheckCircle2,
} from "lucide-react";
import Link from "next/link";
import { apiFetch } from "@/services/apiService";

interface CaseNote {
  id: string;
  case_id: string;
  note: string;
  created_by: string;
  created_at: string;
}

interface CaseEvidence {
  id: string;
  case_id: string;
  evidence_type: string;
  file_url: string;
  description: string | null;
  uploaded_by: string;
  uploaded_at: string;
}

interface CaseTimeline {
  id: string;
  case_id: string;
  event_type: string;
  event_description: string;
  performed_by: string;
  created_at: string;
}

interface InvestigationCase {
  id: string;
  case_number: string;
  alert_id: string;
  cluster_id: string;
  assigned_officer: string | null;
  priority: string;
  status: string;
  title: string;
  description: string;
  opened_at: string;
  due_date: string | null;
  closed_at: string | null;
  resolution: string | null;
  final_decision: string | null;
  created_at: string;
  updated_at: string;
  notes: CaseNote[];
  evidence: CaseEvidence[];
  timeline: CaseTimeline[];
}

export default function CaseDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [caseObj, setCaseObj] = useState<InvestigationCase | null>(null);
  const [activeTab, setActiveTab] = useState<"info" | "notes" | "evidence" | "timeline">("info");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Info/action form states
  const [assignee, setAssignee] = useState("");
  const [newStatus, setNewStatus] = useState("ACTIVE");
  const [statusRemarks, setStatusRemarks] = useState("");
  const [resolutionText, setResolutionText] = useState("");
  const [finalDecision, setFinalDecision] = useState("RECOMMEND_RECALL");

  // Notes
  const [newNote, setNewNote] = useState("");

  // Evidence
  const [evidenceType, setEvidenceType] = useState("LAB_REPORT");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [evidenceDesc, setEvidenceDesc] = useState("");

  const showSuccess = (msg: string) => {
    setActionSuccess(msg);
    setTimeout(() => setActionSuccess(null), 4000);
  };

  const fetchCase = async () => {
    setLoading(true);
    setError(null);
    try {
      const raw = await apiFetch<{ data: InvestigationCase } | InvestigationCase>(`/community/cases/${id}`);
      const res: InvestigationCase = (raw as any).data || raw as InvestigationCase;
      setCaseObj(res);
      setAssignee(res.assigned_officer || "");
      setResolutionText(res.resolution || "");
      setFinalDecision(res.final_decision || "RECOMMEND_RECALL");
    } catch (err: any) {
      setError(err.message || "Failed to load case folder.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [id]);

  const handleAssign = async () => {
    if (!assignee) return;
    setActionLoading(true);
    try {
      const raw = await apiFetch<any>(
        `/community/cases/${id}/assign?officer=${encodeURIComponent(assignee)}`,
        { method: "PATCH" }
      );
      const updated: InvestigationCase = raw?.data || raw;
      setCaseObj(updated);
      showSuccess(`Case assigned to ${assignee} successfully.`);
    } catch (err: any) {
      alert("Officer assignment failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateStatus = async () => {
    setActionLoading(true);
    try {
      const raw = await apiFetch<any>(
        `/community/cases/${id}/status?status=${newStatus}&remarks=${encodeURIComponent(statusRemarks)}`,
        { method: "PATCH" }
      );
      const updated: InvestigationCase = raw?.data || raw;
      setCaseObj(updated);
      setStatusRemarks("");
      showSuccess(`Status transitioned to ${newStatus}.`);
    } catch (err: any) {
      alert("Status update failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!resolutionText) {
      alert("Provide a resolution summary.");
      return;
    }
    setActionLoading(true);
    try {
      const raw = await apiFetch<any>(
        `/community/cases/${id}/resolve?resolution=${encodeURIComponent(resolutionText)}&final_decision=${finalDecision}`,
        { method: "PATCH" }
      );
      const updated: InvestigationCase = raw?.data || raw;
      setCaseObj(updated);
      showSuccess("Investigation successfully resolved.");
    } catch (err: any) {
      alert("Resolution failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleClose = async () => {
    setActionLoading(true);
    try {
      const raw = await apiFetch<any>(
        `/community/cases/${id}/close`,
        { method: "PATCH" }
      );
      const updated: InvestigationCase = raw?.data || raw;
      setCaseObj(updated);
      showSuccess("Case folder archived and closed.");
    } catch (err: any) {
      alert("Closure failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!newNote) return;
    setActionLoading(true);
    try {
      const raw = await apiFetch<any>(`/community/cases/${id}/notes`, {
        method: "POST",
        body: JSON.stringify({ note: newNote, created_by: "QA_ENGINEER" }),
      });
      const updated: InvestigationCase = raw?.data || raw;
      setCaseObj(updated);
      setNewNote("");
      showSuccess("Note added to case log.");
    } catch (err: any) {
      alert("Add note failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAttachEvidence = async () => {
    if (!evidenceUrl) return;
    setActionLoading(true);
    try {
      const raw = await apiFetch<any>(`/community/cases/${id}/evidence`, {
        method: "POST",
        body: JSON.stringify({
          evidence_type: evidenceType,
          file_url: evidenceUrl,
          description: evidenceDesc,
          uploaded_by: "QA_ENGINEER",
        }),
      });
      const updated: InvestigationCase = raw?.data || raw;
      setCaseObj(updated);
      setEvidenceUrl("");
      setEvidenceDesc("");
      showSuccess("Evidence successfully uploaded to case folder.");
    } catch (err: any) {
      alert("Attachment failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-500 space-y-4">
        <Loader2 className="size-10 animate-spin text-blue-600" />
        <p className="text-sm font-semibold">Opening active investigation folder...</p>
      </div>
    );
  }

  if (error || !caseObj) {
    return (
      <div className="p-8 max-w-3xl mx-auto space-y-6">
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 flex items-center gap-2">
          <XCircle className="size-5 shrink-0" />
          <span>{error || "Case folder not found."}</span>
        </div>
        <Link href="/community/cases" className="inline-flex items-center gap-2 text-sm text-blue-600 font-bold hover:underline">
          <ArrowLeft className="size-4" /> Back to cases list
        </Link>
      </div>
    );
  }

  const notes = Array.isArray(caseObj.notes) ? caseObj.notes : [];
  const evidence = Array.isArray(caseObj.evidence) ? caseObj.evidence : [];
  const timeline = Array.isArray(caseObj.timeline) ? caseObj.timeline : [];

  return (
    <div className="space-y-8 p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="space-y-4">
        <Link
          href="/community/cases"
          className="inline-flex items-center gap-2 text-xs text-gray-500 hover:text-blue-600 transition-colors font-bold uppercase tracking-wider"
        >
          <ArrowLeft className="size-4" /> Back to cases list
        </Link>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-950 flex items-center gap-3">
              <FolderKanban className="size-8 text-blue-600" />
              Case Folder: {caseObj.case_number}
            </h1>
            <p className="text-sm text-gray-500 mt-1 font-semibold">{caseObj.title}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border ${
              caseObj.priority === "CRITICAL" ? "text-red-700 bg-red-50 border-red-200" :
              caseObj.priority === "HIGH" ? "text-amber-700 bg-amber-50 border-amber-200" : "text-blue-700 bg-blue-50 border-blue-200"
            }`}>
              Priority: {caseObj.priority}
            </span>
            <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border ${
              caseObj.status === "RESOLVED" ? "text-green-700 bg-green-50 border-green-200" :
              caseObj.status === "CLOSED" ? "text-slate-700 bg-slate-50 border-slate-200" :
              caseObj.status === "ASSIGNED" ? "text-violet-700 bg-violet-50 border-violet-200" : "text-amber-700 bg-amber-50 border-amber-200"
            }`}>
              {caseObj.status}
            </span>
          </div>
        </div>

        {actionSuccess && (
          <div className="flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 px-4 py-2.5 rounded-xl text-sm font-semibold">
            <CheckCircle2 className="size-4" /> {actionSuccess}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap border-b border-gray-200 bg-gray-50/30 p-1 rounded-xl gap-1">
        {[
          { key: "info", label: "Case Folder Info" },
          { key: "notes", label: `Notes (${notes.length})` },
          { key: "evidence", label: `Evidence (${evidence.length})` },
          { key: "timeline", label: `Timeline (${timeline.length})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-5 py-2.5 font-bold text-xs rounded-lg transition-all ${
              activeTab === tab.key
                ? "bg-white text-blue-600 shadow-sm border border-gray-200"
                : "text-gray-500 hover:text-gray-900"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Tab Area */}
        <div className="lg:col-span-2 space-y-6">

          {/* TAB: INFO */}
          {activeTab === "info" && (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
              <h3 className="text-lg font-bold text-gray-950 border-b border-gray-100 pb-3 flex items-center gap-2">
                <FileText className="size-5 text-gray-500" />
                ICME Case Profile Details
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Case Number</span>
                  <p className="font-mono font-bold text-gray-900 mt-1">{caseObj.case_number}</p>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Assigned Officer</span>
                  <p className="text-gray-900 mt-1 flex items-center gap-1.5 font-semibold">
                    <User className="size-4 text-gray-400" />
                    {caseObj.assigned_officer || "Unassigned"}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Date Opened</span>
                  <p className="text-gray-800 mt-1 flex items-center gap-1.5">
                    <Calendar className="size-4 text-gray-400" />
                    {new Date(caseObj.opened_at).toLocaleString()}
                  </p>
                </div>
                {caseObj.closed_at && (
                  <div>
                    <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Date Closed</span>
                    <p className="text-green-700 mt-1 flex items-center gap-1.5 font-semibold">
                      <CheckCircle2 className="size-4 text-green-600" />
                      {new Date(caseObj.closed_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
              <div className="border-t border-gray-100 pt-4">
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Mission Statement</span>
                <p className="text-sm text-gray-700 mt-2 bg-gray-50 p-4 rounded-xl border border-gray-200 leading-relaxed font-mono">
                  {caseObj.description}
                </p>
              </div>
              {(caseObj.resolution || caseObj.final_decision) && (
                <div className="border-t border-gray-100 pt-4 space-y-2">
                  <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Resolution Summary</span>
                  <div className="bg-green-50 border border-green-200 p-4 rounded-xl space-y-2">
                    <p className="text-xs font-mono text-green-800 font-bold uppercase">Decision: {caseObj.final_decision}</p>
                    <p className="text-sm text-gray-800 font-medium leading-relaxed">{caseObj.resolution}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB: NOTES */}
          {activeTab === "notes" && (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
              <h3 className="text-lg font-bold text-gray-950 border-b border-gray-100 pb-3 flex items-center gap-2">
                <BookOpen className="size-5 text-gray-500" />
                Investigative Notes Log ({notes.length})
              </h3>
              <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2">
                {notes.length > 0 ? notes.map((note) => (
                  <div key={note.id} className="bg-gray-50 border border-gray-100 p-4 rounded-xl space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-gray-900 flex items-center gap-1">
                        <User className="size-3.5 text-gray-400" />{note.created_by}
                      </span>
                      <span className="text-gray-400">{new Date(note.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-xs text-gray-700 leading-relaxed font-mono">{note.note}</p>
                  </div>
                )) : (
                  <div className="text-center py-10 text-gray-400 text-sm">No investigative logs recorded.</div>
                )}
              </div>
              <div className="border-t border-gray-100 pt-4 space-y-2">
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Append Note Log</span>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Add investigation update, lab request, inspection note..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    className="flex-1 px-3 py-2.5 border border-gray-200 rounded-xl text-xs bg-white text-gray-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <button
                    onClick={handleAddNote}
                    disabled={actionLoading || !newNote}
                    className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 shadow-sm transition-all disabled:opacity-50"
                  >
                    <Send className="size-3.5" /> Add Note
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB: EVIDENCE */}
          {activeTab === "evidence" && (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
              <h3 className="text-lg font-bold text-gray-950 border-b border-gray-100 pb-3 flex items-center gap-2">
                <Paperclip className="size-5 text-gray-500" />
                Attached Evidence Folder ({evidence.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {evidence.length > 0 ? evidence.map((ev) => (
                  <div key={ev.id} className="border border-gray-200 rounded-xl p-4 flex flex-col gap-3 hover:shadow-sm bg-gray-50/20">
                    <div className="space-y-1">
                      <span className="px-2 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded text-[9px] font-bold uppercase tracking-wider">
                        {ev.evidence_type}
                      </span>
                      <p className="text-xs text-gray-700 font-mono mt-2">{ev.description || "No description."}</p>
                    </div>
                    <div className="flex justify-between items-center border-t border-gray-100 pt-2 text-[10px] text-gray-400 font-medium">
                      <span>By: {ev.uploaded_by}</span>
                      <a href={ev.file_url} target="_blank" rel="noopener noreferrer"
                        className="text-blue-600 hover:underline flex items-center gap-0.5 font-bold">
                        Open File <ExternalLink className="size-3" />
                      </a>
                    </div>
                  </div>
                )) : (
                  <div className="col-span-2 text-center py-10 text-gray-400 text-sm">No evidence attachments mapped.</div>
                )}
              </div>
              <div className="border-t border-gray-100 pt-4 space-y-3">
                <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Attach Evidence</span>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-gray-400">Evidence Type</label>
                    <select value={evidenceType} onChange={(e) => setEvidenceType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900 focus:outline-none">
                      <option value="LAB_REPORT">LAB REPORT</option>
                      <option value="CUSTOMER_RECEIPT">CUSTOMER RECEIPT</option>
                      <option value="ON_SITE_PHOTOS">ON-SITE PHOTO</option>
                      <option value="SUPPLIER_DOCUMENTATION">SUPPLIER SPECIFICATION</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-gray-400">Evidence URL</label>
                    <input type="text" placeholder="https://evidence-store.com/reports/..."
                      value={evidenceUrl} onChange={(e) => setEvidenceUrl(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900" />
                  </div>
                </div>
                <input type="text" placeholder="Brief description (e.g. Lab analysis confirming contamination)"
                  value={evidenceDesc} onChange={(e) => setEvidenceDesc(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900" />
                <button onClick={handleAttachEvidence} disabled={actionLoading || !evidenceUrl}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all disabled:opacity-50">
                  Attach Evidence File
                </button>
              </div>
            </div>
          )}

          {/* TAB: TIMELINE */}
          {activeTab === "timeline" && (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
              <h3 className="text-lg font-bold text-gray-950 border-b border-gray-100 pb-3 flex items-center gap-2">
                <Clock className="size-5 text-gray-500" />
                Investigation Timeline Audit Log
              </h3>
              <div className="relative pl-6 border-l border-gray-200 space-y-6">
                {timeline.length > 0 ? timeline.map((event) => (
                  <div key={event.id} className="relative space-y-1">
                    <div className="absolute -left-[30px] top-1.5 size-4 rounded-full bg-blue-50 border-2 border-blue-600 flex items-center justify-center">
                      <div className="size-1.5 rounded-full bg-blue-600" />
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-gray-900 uppercase font-mono">{event.event_type}</span>
                      <span className="text-gray-400">{new Date(event.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-xs text-gray-600 font-mono leading-relaxed">{event.event_description}</p>
                    <span className="text-[10px] text-gray-400">By: {event.performed_by}</span>
                  </div>
                )) : (
                  <div className="text-center py-10 text-gray-400 text-sm -ml-6">No timeline events recorded.</div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right: Operations Panel */}
        <div className="space-y-6">
          {caseObj.status !== "CLOSED" ? (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
              <h3 className="text-lg font-bold text-gray-950 border-b border-gray-100 pb-3 flex items-center gap-2">
                <ShieldAlert className="size-5 text-blue-600" />
                Case Operations Panel
              </h3>

              {/* Assign Officer */}
              <div className="space-y-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block">Assign QA Officer</span>
                <div className="flex gap-2">
                  <input type="text" placeholder="QA Officer Name..." value={assignee}
                    onChange={(e) => setAssignee(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900 focus:outline-none" />
                  <button onClick={handleAssign} disabled={actionLoading || !assignee}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm disabled:opacity-50">
                    Assign
                  </button>
                </div>
              </div>

              {/* Update Status */}
              {caseObj.status !== "RESOLVED" && (
                <div className="space-y-2 border-t border-gray-100 pt-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block">Update Status</span>
                  <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900">
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="UNDER_REVIEW">UNDER REVIEW</option>
                    <option value="PENDING_EVIDENCE">PENDING EVIDENCE</option>
                    <option value="ACTION_TAKEN">ACTION TAKEN</option>
                  </select>
                  <input type="text" placeholder="Status remarks..." value={statusRemarks}
                    onChange={(e) => setStatusRemarks(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900" />
                  <button onClick={handleUpdateStatus} disabled={actionLoading}
                    className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all disabled:opacity-50">
                    Update Status
                  </button>
                </div>
              )}

              {/* Resolve Case */}
              {caseObj.status !== "RESOLVED" && (
                <div className="space-y-2 border-t border-gray-100 pt-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block">Resolve Case</span>
                  <select value={finalDecision} onChange={(e) => setFinalDecision(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white text-gray-900">
                    <option value="RECOMMEND_RECALL">RECOMMEND PRODUCT RECALL</option>
                    <option value="CONTINUE_MONITORING">CONTINUE MONITORING</option>
                    <option value="NO_ACTION_REQUIRED">NO ACTION REQUIRED</option>
                    <option value="SEND_SUPPLIER_WARNING">SEND SUPPLIER WARNING</option>
                  </select>
                  <textarea rows={3} placeholder="Detailed resolution summary..."
                    value={resolutionText} onChange={(e) => setResolutionText(e.target.value)}
                    className="w-full p-3 border border-gray-200 rounded-xl text-xs bg-white text-gray-900 resize-none" />
                  <button onClick={handleResolve} disabled={actionLoading || !resolutionText}
                    className="w-full py-2 bg-green-600 hover:bg-green-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all disabled:opacity-50">
                    Mark Resolved
                  </button>
                </div>
              )}

              {/* Close Case */}
              {caseObj.status === "RESOLVED" && (
                <div className="space-y-2 border-t border-gray-100 pt-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block">Archive Investigation</span>
                  <button onClick={handleClose} disabled={actionLoading}
                    className="w-full py-2.5 bg-gray-900 hover:bg-black text-white font-bold text-xs rounded-xl shadow-sm transition-all disabled:opacity-50">
                    Archive and Close Folder
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm text-center space-y-4">
              <CheckCircle2 className="size-10 text-green-600 mx-auto" />
              <h4 className="text-sm font-bold text-gray-900">Case Folder Archived</h4>
              <p className="text-xs text-gray-500 leading-relaxed font-mono">
                This investigation has been resolved and closed. Files are sealed.
              </p>
            </div>
          )}

          {/* Summary Info Card */}
          <div className="bg-gray-50 border border-gray-200 rounded-2xl p-5 space-y-3 text-xs text-gray-600">
            <p className="font-bold text-gray-800 text-sm">Case Metadata</p>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Case #</span>
                <span className="font-mono font-bold text-gray-700">{caseObj.case_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Notes</span>
                <span className="font-bold text-gray-700">{notes.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Evidence Files</span>
                <span className="font-bold text-gray-700">{evidence.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Timeline Events</span>
                <span className="font-bold text-gray-700">{timeline.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
