"use client";

import { useEffect, useState } from "react";
import { alertApi, reviewApi, ScanAlert, ManualReview } from "@/services/apiService";
import { AlertTriangle, CheckCircle, Clock, XCircle, Info, ClipboardList } from "lucide-react";
import { cn } from "@/lib/utils";

export default function AlertsReviewsPage() {
  const [activeTab, setActiveTab] = useState<"alerts" | "reviews">("alerts");
  const [alerts, setAlerts] = useState<ScanAlert[]>([]);
  const [reviews, setReviews] = useState<ManualReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modals for resolving review
  const [resolvingReview, setResolvingReview] = useState<ManualReview | null>(null);
  const [reviewDecision, setReviewDecision] = useState<"ACCEPTED" | "REJECTED" | "">("");
  const [reviewNotes, setReviewNotes] = useState("");

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === "alerts") {
        const data = await alertApi.getAlerts();
        setAlerts(data);
      } else {
        const data = await reviewApi.getReviews();
        setReviews(data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleResolveAlert = async (id: string) => {
    try {
      await alertApi.resolveAlert(id);
      setAlerts((prev) =>
        prev.map((a) => (a.id === id ? { ...a, is_resolved: true, resolved_at: new Date().toISOString() } : a))
      );
    } catch (err: any) {
      alert("Failed to resolve alert: " + err.message);
    }
  };

  const handleSubmitReview = async () => {
    if (!resolvingReview || !reviewDecision) return;
    
    try {
      await reviewApi.resolveReview(resolvingReview.id, reviewDecision, reviewNotes);
      setResolvingReview(null);
      setReviewDecision("");
      setReviewNotes("");
      fetchData(); // Refresh list
    } catch (err: any) {
      alert("Failed to submit review: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Alerts & Reviews</h1>
          <p className="text-white/60 mt-1">Manage scan anomalies and manual verification tasks.</p>
        </div>
        
        <div className="flex bg-white/5 rounded-lg p-1 border border-white/10">
          <button
            onClick={() => setActiveTab("alerts")}
            className={cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2",
              activeTab === "alerts" ? "bg-white/10 text-white" : "text-white/60 hover:text-white"
            )}
          >
            <AlertTriangle className="size-4" />
            Alerts ({alerts.filter((a) => !a.is_resolved).length})
          </button>
          <button
            onClick={() => setActiveTab("reviews")}
            className={cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2",
              activeTab === "reviews" ? "bg-white/10 text-white" : "text-white/60 hover:text-white"
            )}
          >
            <ClipboardList className="size-4" />
            Manual Reviews ({reviews.filter((r) => r.review_status === "pending").length})
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-white/5 rounded-lg"></div>
          ))}
        </div>
      ) : activeTab === "alerts" ? (
        <div className="space-y-4">
          {alerts.length === 0 ? (
            <div className="text-center py-12 text-white/40">No alerts found.</div>
          ) : (
            alerts.map((alert) => (
              <div
                key={alert.id}
                className={cn(
                  "p-5 rounded-lg border flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between",
                  alert.is_resolved
                    ? "bg-white/5 border-white/5 opacity-60"
                    : alert.severity === "CRITICAL"
                    ? "bg-red-500/10 border-red-500/20"
                    : "bg-yellow-500/10 border-yellow-500/20"
                )}
              >
                <div className="flex gap-4 items-start">
                  <div
                    className={cn(
                      "p-2 rounded-full",
                      alert.is_resolved
                        ? "bg-white/10 text-white/50"
                        : alert.severity === "CRITICAL"
                        ? "bg-red-500/20 text-red-400"
                        : "bg-yellow-500/20 text-yellow-400"
                    )}
                  >
                    {alert.is_resolved ? <CheckCircle className="size-6" /> : alert.severity === "CRITICAL" ? <XCircle className="size-6" /> : <AlertTriangle className="size-6" />}
                  </div>
                  <div>
                    <h3 className="text-white font-medium flex items-center gap-2">
                      {alert.product_name}
                      <span
                        className={cn(
                          "text-xs px-2 py-0.5 rounded-full",
                          alert.severity === "CRITICAL" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"
                        )}
                      >
                        {alert.alert_type}
                      </span>
                    </h3>
                    <p className="text-white/60 text-sm mt-1">{alert.message}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-white/40">
                      <span className="flex items-center gap-1">
                        <Clock className="size-3" /> {new Date(alert.created_at || "").toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                {!alert.is_resolved && (
                  <button
                    onClick={() => handleResolveAlert(alert.id)}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm transition-colors whitespace-nowrap"
                  >
                    Mark Resolved
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.length === 0 ? (
            <div className="text-center py-12 text-white/40">No pending reviews.</div>
          ) : (
            reviews.map((review) => (
              <div
                key={review.id}
                className={cn(
                  "p-5 rounded-lg border flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between",
                  review.review_status === "resolved"
                    ? "bg-white/5 border-white/5 opacity-60"
                    : "bg-blue-500/10 border-blue-500/20"
                )}
              >
                <div className="flex gap-4 items-start">
                  <div
                    className={cn(
                      "p-2 rounded-full",
                      review.review_status === "resolved"
                        ? "bg-white/10 text-white/50"
                        : "bg-blue-500/20 text-blue-400"
                    )}
                  >
                    {review.review_status === "resolved" ? <CheckCircle className="size-6" /> : <Info className="size-6" />}
                  </div>
                  <div>
                    <h3 className="text-white font-medium flex items-center gap-2">
                      {review.product_name}
                      <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400">
                        {review.review_type}
                      </span>
                    </h3>
                    <p className="text-white/60 text-sm mt-1">{review.review_notes}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-white/40">
                      <span className="flex items-center gap-1">
                        <Clock className="size-3" /> {new Date(review.created_at || "").toLocaleString()}
                      </span>
                      {review.review_status === "resolved" && (
                        <span>Decision: <strong className="text-white/80">{review.human_decision}</strong></span>
                      )}
                    </div>
                  </div>
                </div>
                
                {review.review_status === "pending" && (
                  <button
                    onClick={() => setResolvingReview(review)}
                    className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 rounded-lg text-sm transition-colors whitespace-nowrap"
                  >
                    Review Now
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Review Modal */}
      {resolvingReview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-[#111] border border-white/10 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-2">Manual Verification</h2>
            <p className="text-white/60 mb-6 text-sm">
              Product: <strong>{resolvingReview.product_name}</strong><br />
              Issue: {resolvingReview.review_notes}
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Decision</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setReviewDecision("ACCEPTED")}
                    className={cn(
                      "py-2 px-4 rounded-lg border transition-colors",
                      reviewDecision === "ACCEPTED" 
                        ? "bg-green-500/20 border-green-500/50 text-green-400" 
                        : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10"
                    )}
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => setReviewDecision("REJECTED")}
                    className={cn(
                      "py-2 px-4 rounded-lg border transition-colors",
                      reviewDecision === "REJECTED" 
                        ? "bg-red-500/20 border-red-500/50 text-red-400" 
                        : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10"
                    )}
                  >
                    Reject
                  </button>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Notes (Optional)</label>
                <textarea
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none h-24"
                  placeholder="E.g., Date verified by calling supplier..."
                />
              </div>
              
              <div className="flex justify-end gap-3 pt-4">
                <button
                  onClick={() => setResolvingReview(null)}
                  className="px-4 py-2 text-white/60 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitReview}
                  disabled={!reviewDecision}
                  className="px-6 py-2 bg-primary text-primary-foreground font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
                >
                  Submit Decision
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
