"use client";

import { useState, useEffect } from "react";
import { 
  AlertCircle, AlertTriangle, CheckCircle, Clock, Eye, Edit, 
  FileText, Search, Filter, X, ShieldAlert, FileWarning, 
  RefreshCw, Loader2, Info
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  alertApi, reviewApi, AlertSummary, ScanAlert, AlertDetails, ManualReview 
} from "@/services/apiService";

function SeverityBadge({ severity }: { severity: string }) {
  if (severity === "CRITICAL") return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
      <ShieldAlert className="size-3" /> Critical
    </span>
  );
  if (severity === "WARNING") return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
      <AlertTriangle className="size-3" /> Warning
    </span>
  );
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
      <Info className="size-3" /> {severity}
    </span>
  );
}

function StatusBadge({ isResolved }: { isResolved: boolean }) {
  if (isResolved) return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
      <CheckCircle className="size-3" /> Resolved
    </span>
  );
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
      <Clock className="size-3" /> Unresolved
    </span>
  );
}

function ReviewStatusBadge({ status }: { status: string }) {
  if (status === "RESOLVED") return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
      <CheckCircle className="size-3" /> Resolved
    </span>
  );
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
      <Clock className="size-3" /> Pending Review
    </span>
  );
}

export default function AlertsAndReviewsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [summary, setSummary] = useState<AlertSummary | null>(null);
  const [alerts, setAlerts] = useState<ScanAlert[]>([]);
  const [reviews, setReviews] = useState<ManualReview[]>([]);
  const [activeTab, setActiveTab] = useState("alerts");
  
  // Filters
  const [filters, setFilters] = useState({
    search: "",
    status: "unresolved", // For alerts
    reviewStatus: "PENDING", // For reviews
    severity: "",
    alert_type: "",
  });

  const [selectedAlert, setSelectedAlert] = useState<AlertDetails | null>(null);
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
  
  const [selectedReview, setSelectedReview] = useState<ManualReview | null>(null);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Correction Form State
  const [correctionForm, setCorrectionForm] = useState({
    decision: "APPROVE",
    corrected_product_name: "",
    corrected_mfg_date: "",
    corrected_expiry_date: "",
    corrected_batch_number: "",
    corrected_description: "",
    reviewer_note: "",
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [sumData, alertsData, reviewsData] = await Promise.all([
        alertApi.getSummary(),
        alertApi.getAlerts({ 
          status: filters.status, 
          search: filters.search,
          severity: filters.severity,
          alert_type: filters.alert_type
        }),
        reviewApi.getReviews({
          status: filters.reviewStatus,
          search: filters.search
        })
      ]);
      setSummary(sumData);
      setAlerts(alertsData);
      setReviews(reviewsData);
    } catch (err) {
      console.error("Failed to load alerts/reviews", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const handleViewAlert = async (alertId: string) => {
    try {
      const details = await alertApi.getAlertDetails(alertId);
      setSelectedAlert(details);
      setIsAlertModalOpen(true);
    } catch (err) {
      console.error("Failed to load alert details", err);
      alert("Failed to load alert details");
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    try {
      await alertApi.resolveAlert(alertId, "Manually resolved");
      setIsAlertModalOpen(false);
      fetchData();
    } catch (err) {
      alert("Failed to resolve alert");
    }
  };

  const handleOpenReview = (review: ManualReview) => {
    setSelectedReview(review);
    setCorrectionForm({
      decision: "APPROVE",
      corrected_product_name: review.product_name || "",
      corrected_mfg_date: review.original_mfg_date || "",
      corrected_expiry_date: review.original_expiry_date || "",
      corrected_batch_number: review.batch_number || "",
      corrected_description: "",
      reviewer_note: "",
    });
    setIsReviewModalOpen(true);
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReview) return;
    setIsSubmitting(true);
    try {
      await reviewApi.correctReview(selectedReview.id, correctionForm);
      setIsReviewModalOpen(false);
      fetchData();
    } catch (err) {
      alert("Failed to submit review correction");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts & Reviews</h1>
          <p className="text-sm text-gray-500 mt-1">Manage system alerts and manual data correction queues.</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchData} disabled={isLoading}>
          <RefreshCw className={`size-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <Card className="bg-white border-gray-200">
          <CardContent className="p-4 flex flex-col items-center justify-center text-center h-full">
            <div className="text-2xl font-bold text-gray-900">{summary?.total_alerts || 0}</div>
            <div className="text-xs text-gray-500 font-medium mt-1">Total Alerts</div>
          </CardContent>
        </Card>
        <Card className="bg-red-50 border-red-100">
          <CardContent className="p-4 flex flex-col items-center justify-center text-center h-full">
            <ShieldAlert className="size-5 text-red-600 mb-1" />
            <div className="text-2xl font-bold text-red-700">{summary?.critical_alerts || 0}</div>
            <div className="text-xs text-red-600 font-medium mt-1">Critical</div>
          </CardContent>
        </Card>
        <Card className="bg-amber-50 border-amber-100">
          <CardContent className="p-4 flex flex-col items-center justify-center text-center h-full">
            <Clock className="size-5 text-amber-600 mb-1" />
            <div className="text-2xl font-bold text-amber-700">{summary?.pending_reviews || 0}</div>
            <div className="text-xs text-amber-600 font-medium mt-1">Pending Reviews</div>
          </CardContent>
        </Card>
        <Card className="bg-orange-50 border-orange-100">
          <CardContent className="p-4 flex flex-col items-center justify-center text-center h-full">
            <FileWarning className="size-5 text-orange-600 mb-1" />
            <div className="text-2xl font-bold text-orange-700">{summary?.ocr_failed || 0}</div>
            <div className="text-xs text-orange-600 font-medium mt-1">OCR Failed</div>
          </CardContent>
        </Card>
        <Card className="bg-yellow-50 border-yellow-100">
          <CardContent className="p-4 flex flex-col items-center justify-center text-center h-full">
            <AlertCircle className="size-5 text-yellow-600 mb-1" />
            <div className="text-2xl font-bold text-yellow-700">{summary?.missing_exp || 0}</div>
            <div className="text-xs text-yellow-600 font-medium mt-1">Missing EXP</div>
          </CardContent>
        </Card>
        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="p-4 flex flex-col items-center justify-center text-center h-full">
            <AlertTriangle className="size-5 text-gray-600 mb-1" />
            <div className="text-2xl font-bold text-gray-700">{summary?.unknown_barcode || 0}</div>
            <div className="text-xs text-gray-600 font-medium mt-1">Unknown Barcode</div>
          </CardContent>
        </Card>
        <Card className="bg-green-50 border-green-100">
          <CardContent className="p-4 flex flex-col items-center justify-center text-center h-full">
            <CheckCircle className="size-5 text-green-600 mb-1" />
            <div className="text-2xl font-bold text-green-700">{summary?.resolved_today || 0}</div>
            <div className="text-xs text-green-600 font-medium mt-1">Resolved Today</div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-[400px] grid-cols-2 bg-gray-100 p-1 rounded-lg">
          <TabsTrigger value="alerts" className="data-[state=active]:bg-white rounded-md text-sm">System Alerts</TabsTrigger>
          <TabsTrigger value="reviews" className="data-[state=active]:bg-white rounded-md text-sm">Manual Reviews Queue</TabsTrigger>
        </TabsList>

        <div className="mt-4 bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-wrap gap-4 items-center">
          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
            <Input 
              placeholder="Search by product, barcode..." 
              className="pl-9 bg-gray-50 border-gray-200 text-sm"
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            />
          </div>
          
          {activeTab === "alerts" && (
            <>
              <select 
                className="h-10 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:ring-1 focus:ring-primary"
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              >
                <option value="">All Statuses</option>
                <option value="unresolved">Unresolved</option>
                <option value="resolved">Resolved</option>
              </select>
              <select 
                className="h-10 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:ring-1 focus:ring-primary"
                value={filters.severity}
                onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
              >
                <option value="">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="WARNING">Warning</option>
              </select>
              <select 
                className="h-10 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:ring-1 focus:ring-primary"
                value={filters.alert_type}
                onChange={(e) => setFilters(prev => ({ ...prev, alert_type: e.target.value }))}
              >
                <option value="">All Alert Types</option>
                <option value="OCR_FAILED">OCR Failed</option>
                <option value="MISSING_EXPIRY">Missing Expiry</option>
                <option value="MISSING_MFG">Missing MFG</option>
                <option value="UNKNOWN_BARCODE">Unknown Barcode</option>
              </select>
            </>
          )}

          {activeTab === "reviews" && (
            <select 
              className="h-10 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:ring-1 focus:ring-primary"
              value={filters.reviewStatus}
              onChange={(e) => setFilters(prev => ({ ...prev, reviewStatus: e.target.value }))}
            >
              <option value="">All Reviews</option>
              <option value="PENDING">Pending</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          )}

          {(filters.search || filters.severity || filters.alert_type) && (
            <Button variant="ghost" className="text-gray-500 h-10 px-3" onClick={() => setFilters({ search: "", status: "unresolved", reviewStatus: "PENDING", severity: "", alert_type: "" })}>
              <X className="size-4 mr-2" /> Clear
            </Button>
          )}
        </div>

        <TabsContent value="alerts" className="mt-4">
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex justify-center p-12 text-gray-400"><Loader2 className="size-6 animate-spin" /></div>
              ) : alerts.length === 0 ? (
                <div className="text-center p-12 text-gray-500">No alerts found matching filters.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 border-b border-gray-200 text-gray-600">
                      <tr>
                        <th className="px-4 py-3 font-medium">Alert Type</th>
                        <th className="px-4 py-3 font-medium">Product / Barcode</th>
                        <th className="px-4 py-3 font-medium">Severity</th>
                        <th className="px-4 py-3 font-medium">Issue</th>
                        <th className="px-4 py-3 font-medium">Time</th>
                        <th className="px-4 py-3 font-medium">Status</th>
                        <th className="px-4 py-3 font-medium text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {alerts.map(alert => (
                        <tr key={alert.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 font-medium text-gray-900">{alert.alert_type}</td>
                          <td className="px-4 py-3">
                            <div className="font-medium text-gray-900">{alert.product_name}</div>
                            <div className="text-xs text-gray-500 font-mono">{alert.barcode}</div>
                          </td>
                          <td className="px-4 py-3"><SeverityBadge severity={alert.severity} /></td>
                          <td className="px-4 py-3 text-gray-600 max-w-xs truncate" title={alert.issue}>{alert.issue}</td>
                          <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                            {alert.created_at ? new Date(alert.created_at).toLocaleString() : '—'}
                          </td>
                          <td className="px-4 py-3"><StatusBadge isResolved={alert.is_resolved} /></td>
                          <td className="px-4 py-3 text-right">
                            <Button variant="outline" size="sm" onClick={() => handleViewAlert(alert.id)}>
                              <Eye className="size-3 mr-1" /> View
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reviews" className="mt-4">
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex justify-center p-12 text-gray-400"><Loader2 className="size-6 animate-spin" /></div>
              ) : reviews.length === 0 ? (
                <div className="text-center p-12 text-gray-500">No manual reviews found matching filters.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 border-b border-gray-200 text-gray-600">
                      <tr>
                        <th className="px-4 py-3 font-medium">Type</th>
                        <th className="px-4 py-3 font-medium">Product / Barcode</th>
                        <th className="px-4 py-3 font-medium">Batch</th>
                        <th className="px-4 py-3 font-medium">Detected Dates</th>
                        <th className="px-4 py-3 font-medium">Time</th>
                        <th className="px-4 py-3 font-medium">Status</th>
                        <th className="px-4 py-3 font-medium text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {reviews.map(review => (
                        <tr key={review.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-3 font-medium text-gray-900">{review.review_type}</td>
                          <td className="px-4 py-3">
                            <div className="font-medium text-gray-900">{review.product_name}</div>
                            <div className="text-xs text-gray-500 font-mono">{review.barcode}</div>
                          </td>
                          <td className="px-4 py-3 text-gray-600 font-mono">{review.batch_number || '—'}</td>
                          <td className="px-4 py-3 text-gray-600 text-xs">
                            <div>MFG: {review.original_mfg_date || '—'}</div>
                            <div>EXP: {review.original_expiry_date || '—'}</div>
                          </td>
                          <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                            {review.created_at ? new Date(review.created_at).toLocaleString() : '—'}
                          </td>
                          <td className="px-4 py-3"><ReviewStatusBadge status={review.review_status} /></td>
                          <td className="px-4 py-3 text-right">
                            {review.review_status === "PENDING" ? (
                              <Button size="sm" className="bg-primary hover:bg-primary/90" onClick={() => handleOpenReview(review)}>
                                <Edit className="size-3 mr-1" /> Correct Data
                              </Button>
                            ) : (
                              <Button variant="outline" size="sm" onClick={() => handleOpenReview(review)}>
                                <Eye className="size-3 mr-1" /> View Decision
                              </Button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Alert Details Dialog */}
      <Dialog open={isAlertModalOpen} onOpenChange={setIsAlertModalOpen}>
        <DialogContent className="sm:max-w-2xl bg-white max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl text-gray-900">
              Alert Details 
              {selectedAlert && <SeverityBadge severity={selectedAlert.severity} />}
            </DialogTitle>
          </DialogHeader>
          
          {selectedAlert && (
            <div className="space-y-6 mt-4">
              <div className="grid grid-cols-2 gap-4 text-sm bg-gray-50 p-4 rounded-xl border border-gray-200">
                <div>
                  <div className="text-gray-500 text-xs uppercase font-semibold">Product Name</div>
                  <div className="font-medium text-gray-900 mt-1">{selectedAlert.product_name}</div>
                </div>
                <div>
                  <div className="text-gray-500 text-xs uppercase font-semibold">Barcode</div>
                  <div className="font-mono text-gray-900 mt-1">{selectedAlert.barcode}</div>
                </div>
                <div>
                  <div className="text-gray-500 text-xs uppercase font-semibold">Alert Type</div>
                  <div className="font-medium text-gray-900 mt-1">{selectedAlert.alert_type}</div>
                </div>
                <div>
                  <div className="text-gray-500 text-xs uppercase font-semibold">Status</div>
                  <div className="mt-1"><StatusBadge isResolved={selectedAlert.is_resolved} /></div>
                </div>
                <div className="col-span-2">
                  <div className="text-gray-500 text-xs uppercase font-semibold">Error / Issue</div>
                  <div className="text-red-600 bg-red-50 p-2 rounded-md mt-1 border border-red-100">{selectedAlert.error_reason || selectedAlert.message}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h3 className="font-semibold text-gray-900 border-b pb-2">OCR Extraction Results</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between border-b border-gray-100 pb-1">
                      <span className="text-gray-500">Detected MFG Date</span>
                      <span className="font-medium">{selectedAlert.detected_mfg || "—"}</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-100 pb-1">
                      <span className="text-gray-500">Detected EXP Date</span>
                      <span className="font-medium">{selectedAlert.detected_exp || "—"}</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-100 pb-1">
                      <span className="text-gray-500">Detected Batch</span>
                      <span className="font-mono">{selectedAlert.detected_batch || "—"}</span>
                    </div>
                  </div>
                  
                  {selectedAlert.ocr_raw_text && (
                    <div className="mt-4">
                      <span className="text-xs text-gray-500 uppercase font-semibold block mb-1">Raw OCR Text</span>
                      <div className="bg-gray-900 text-gray-200 p-3 rounded-md text-xs font-mono max-h-32 overflow-y-auto whitespace-pre-wrap">
                        {selectedAlert.ocr_raw_text}
                      </div>
                    </div>
                  )}
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-900 border-b pb-2 mb-3">Scan Image</h3>
                  <div className="bg-gray-100 rounded-lg border border-gray-200 aspect-square flex items-center justify-center overflow-hidden">
                    {selectedAlert.image_url ? (
                      <img src={selectedAlert.image_url} alt="Scan" className="w-full h-full object-contain" />
                    ) : (
                      <div className="text-gray-400 flex flex-col items-center">
                        <Eye className="size-8 mb-2 opacity-50" />
                        <span>No image available</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <DialogFooter className="mt-6 border-t pt-4">
            <Button variant="outline" onClick={() => setIsAlertModalOpen(false)}>Close</Button>
            {selectedAlert && !selectedAlert.is_resolved && (
              <Button onClick={() => handleResolveAlert(selectedAlert.id)}>Mark as Resolved</Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Manual Review / OCR Correction Dialog */}
      <Dialog open={isReviewModalOpen} onOpenChange={setIsReviewModalOpen}>
        <DialogContent className="sm:max-w-2xl bg-white max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl text-gray-900">
              Manual Data Correction
            </DialogTitle>
          </DialogHeader>

          {selectedReview && (
            <form onSubmit={handleSubmitReview} className="space-y-6 mt-4">
              <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl flex items-start gap-3">
                <AlertCircle className="size-5 text-amber-600 shrink-0 mt-0.5" />
                <div className="text-sm text-amber-800">
                  <p className="font-semibold mb-1">Human verification required for: {selectedReview.product_name}</p>
                  <p>Please verify the extracted dates and information. Make corrections in the form below before approving.</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="product_name">Product Name</Label>
                  <Input 
                    id="product_name"
                    value={correctionForm.corrected_product_name}
                    onChange={e => setCorrectionForm({...correctionForm, corrected_product_name: e.target.value})}
                    disabled={selectedReview.review_status !== "PENDING"}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="mfg_date">Manufacturing Date</Label>
                  <div className="text-xs text-gray-500 mb-1">OCR detected: {selectedReview.original_mfg_date || 'None'}</div>
                  <Input 
                    id="mfg_date" type="date"
                    value={correctionForm.corrected_mfg_date}
                    onChange={e => setCorrectionForm({...correctionForm, corrected_mfg_date: e.target.value})}
                    disabled={selectedReview.review_status !== "PENDING"}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="exp_date">Expiry Date</Label>
                  <div className="text-xs text-gray-500 mb-1">OCR detected: {selectedReview.original_expiry_date || 'None'}</div>
                  <Input 
                    id="exp_date" type="date"
                    value={correctionForm.corrected_expiry_date}
                    onChange={e => setCorrectionForm({...correctionForm, corrected_expiry_date: e.target.value})}
                    disabled={selectedReview.review_status !== "PENDING"}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="batch">Batch Number</Label>
                  <Input 
                    id="batch"
                    value={correctionForm.corrected_batch_number}
                    onChange={e => setCorrectionForm({...correctionForm, corrected_batch_number: e.target.value})}
                    disabled={selectedReview.review_status !== "PENDING"}
                  />
                </div>

                <div className="space-y-2 col-span-2">
                  <Label htmlFor="decision">Decision</Label>
                  <select 
                    id="decision"
                    className="flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:opacity-50"
                    value={correctionForm.decision}
                    onChange={e => setCorrectionForm({...correctionForm, decision: e.target.value})}
                    disabled={selectedReview.review_status !== "PENDING"}
                  >
                    <option value="APPROVE">Approve & Send to Inventory</option>
                    <option value="CORRECT_DATA">Correct Data & Approve</option>
                    <option value="REJECT">Reject Item</option>
                    <option value="RE_SCAN">Send for Re-Scan</option>
                  </select>
                </div>
                
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="notes">Reviewer Notes (Optional)</Label>
                  <Input 
                    id="notes"
                    value={correctionForm.reviewer_note}
                    onChange={e => setCorrectionForm({...correctionForm, reviewer_note: e.target.value})}
                    disabled={selectedReview.review_status !== "PENDING"}
                    placeholder="Why was this changed?"
                  />
                </div>
              </div>

              <DialogFooter className="border-t pt-4">
                <Button type="button" variant="outline" onClick={() => setIsReviewModalOpen(false)}>Close</Button>
                {selectedReview.review_status === "PENDING" && (
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? <Loader2 className="size-4 animate-spin mr-2" /> : <CheckCircle className="size-4 mr-2" />}
                    Save Correction
                  </Button>
                )}
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
