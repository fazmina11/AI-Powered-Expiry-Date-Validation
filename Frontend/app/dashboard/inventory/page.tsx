"use client";

import { useState, useEffect, useMemo } from "react";
import { Edit, Trash2, Eye, Plus, RefreshCw, AlertTriangle, CheckCircle, Clock, XCircle, Loader2, Search, Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { productApi, inventoryApi, Product, InventoryItem, InventoryIntakeRequest } from "@/services/apiService";

// Status badge helper
function StatusBadge({ status }: { status: string }) {
  const s = (status || "").toUpperCase();
  if (s === "ACCEPTED") return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
      <CheckCircle className="size-3" /> Accepted
    </span>
  );
  if (s === "REJECTED") return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
      <XCircle className="size-3" /> Rejected
    </span>
  );
  if (s === "PRIORITY_SALE") return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
      <AlertTriangle className="size-3" /> Priority Sale
    </span>
  );
  if (s === "MANUAL_REVIEW") return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
      <Clock className="size-3" /> Review
    </span>
  );
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
      {status}
    </span>
  );
}

// Intake form dialog
function IntakeFormDialog({
  open,
  onClose,
  onSuccess,
}: {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [formData, setFormData] = useState<InventoryIntakeRequest>({
    barcode: "",
    batch_number: "",
    manufacturing_date: "",
    expiry_date: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<null | { status: string; decision_reason: string | null; remaining_days: number | null }>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setResult(null);
    setIsLoading(true);
    try {
      const payload: InventoryIntakeRequest = {
        barcode: formData.barcode,
        batch_number: formData.batch_number,
      };
      if (formData.manufacturing_date) payload.manufacturing_date = formData.manufacturing_date;
      if (formData.expiry_date) payload.expiry_date = formData.expiry_date;
      const item = await inventoryApi.intake(payload);
      setResult({ status: item.status, decision_reason: item.decision_reason, remaining_days: item.remaining_days });
      onSuccess();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({ barcode: "", batch_number: "", manufacturing_date: "", expiry_date: "" });
    setError("");
    setResult(null);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>New Inventory Intake</DialogTitle>
          <DialogDescription>
            Scan a product barcode and enter batch details. The system will auto-evaluate expiry status.
          </DialogDescription>
        </DialogHeader>

        {result ? (
          <div className="space-y-4">
            <div className={`p-4 rounded-lg border ${
              result.status === "ACCEPTED" ? "bg-green-50 border-green-200" :
              result.status === "REJECTED" ? "bg-red-50 border-red-200" :
              result.status === "PRIORITY_SALE" ? "bg-orange-50 border-orange-200" :
              "bg-yellow-50 border-yellow-200"
            }`}>
              <div className="font-semibold text-sm mb-1">Intake Decision</div>
              <StatusBadge status={result.status} />
              {result.remaining_days !== null && (
                <div className="mt-2 text-sm text-gray-600">{result.remaining_days} days remaining</div>
              )}
              {result.decision_reason && (
                <div className="mt-1 text-sm text-gray-600">{result.decision_reason}</div>
              )}
            </div>
            <DialogFooter>
              <Button onClick={handleClose}>Done</Button>
            </DialogFooter>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="barcode">Barcode *</Label>
              <Input
                id="barcode"
                placeholder="e.g. 8901262010011"
                value={formData.barcode}
                onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="batch_number">Batch Number *</Label>
              <Input
                id="batch_number"
                placeholder="e.g. BATCH-2026-001"
                value={formData.batch_number}
                onChange={(e) => setFormData({ ...formData, batch_number: e.target.value })}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="mfg_date">Manufacturing Date</Label>
                <Input
                  id="mfg_date"
                  type="date"
                  value={formData.manufacturing_date}
                  onChange={(e) => setFormData({ ...formData, manufacturing_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="exp_date">Expiry Date</Label>
                <Input
                  id="exp_date"
                  type="date"
                  value={formData.expiry_date}
                  onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                />
              </div>
            </div>

            {error && (
              <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md border border-red-200">{error}</div>
            )}

            <DialogFooter>
              <Button type="button" variant="secondary" onClick={handleClose}>Cancel</Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? <><Loader2 className="size-4 mr-2 animate-spin" /> Processing…</> : "Submit Intake"}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default function InventoryPage() {
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [products, setProducts] = useState<Record<string, Product>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [total, setTotal] = useState(0);

  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isIntakeOpen, setIsIntakeOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  
  // Filter state
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    search: "",
    category: "",
    brand: "",
    inventoryStatus: "",
    scanStatus: "",
    ocrStatus: "",
    manualReviewStatus: "",
    warehouse: "",
    storageLocation: "",
    dateFrom: "",
    dateTo: "",
  });

  const [isUpdating, setIsUpdating] = useState(false);

  const fetchData = async () => {
    setIsLoading(true);
    setError("");
    try {
      const [invData, prodData] = await Promise.all([
        inventoryApi.getAll(0, 100),
        productApi.getAll(0, 200),
      ]);
      setInventoryItems(invData.items);
      setTotal(invData.total);
      // Build a product lookup map
      const prodMap: Record<string, Product> = {};
      prodData.forEach((p) => { prodMap[p.id] = p; });
      setProducts(prodMap);
    } catch (err) {
      setError("Failed to load inventory. Is the backend running?");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleViewItem = (item: InventoryItem) => {
    setSelectedItem(item);
    setIsDetailOpen(true);
  };

  const getDaysColor = (days: number | null) => {
    if (days === null) return "text-gray-500";
    if (days < 0) return "text-red-600 font-semibold";
    if (days <= 7) return "text-orange-600 font-semibold";
    if (days <= 30) return "text-amber-600";
    return "text-green-600";
  };

  const handleDelete = async () => {
    if (!selectedItem) return;
    setIsUpdating(true);
    try {
      await inventoryApi.delete(selectedItem.id);
      setIsDeleteOpen(false);
      setSelectedItem(null);
      fetchData();
    } catch (err) {
      alert("Failed to delete item: " + (err as Error).message);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem) return;
    setIsUpdating(true);
    try {
      const form = e.target as HTMLFormElement;
      const data = {
        batch_number: (form.elements.namedItem("batch_number") as HTMLInputElement).value,
        manufacturing_date: (form.elements.namedItem("manufacturing_date") as HTMLInputElement).value || null,
        expiry_date: (form.elements.namedItem("expiry_date") as HTMLInputElement).value || null,
        status: (form.elements.namedItem("status") as HTMLSelectElement).value,
      };
      // status maps to operator_decision in backend logic for simple updates in our mockup
      await inventoryApi.update(selectedItem.id, {
        batch_number: data.batch_number,
        manufacturing_date: data.manufacturing_date,
        expiry_date: data.expiry_date,
        operator_decision: data.status !== "KEEP" ? data.status : undefined
      } as any);
      setIsEditOpen(false);
      fetchData();
    } catch (err) {
      alert("Failed to update item: " + (err as Error).message);
    } finally {
      setIsUpdating(false);
    }
  };

  const filteredItems = useMemo(() => {
    return inventoryItems.filter((item) => {
      const p = products[item.product_id];
      const s = filters.search.toLowerCase();
      
      // Text Search
      if (s) {
        const matchesName = p?.name?.toLowerCase().includes(s);
        const matchesBarcode = p?.barcode?.toLowerCase().includes(s);
        const matchesBatch = item.batch_number?.toLowerCase().includes(s);
        if (!matchesName && !matchesBarcode && !matchesBatch) return false;
      }
      
      // Category & Brand
      if (filters.category && p?.category !== filters.category) return false;
      if (filters.brand && p?.brand !== filters.brand) return false;
      
      // Statuses
      const itemStatus = (item.operator_decision || item.intake_status || "PENDING").toUpperCase();
      if (filters.inventoryStatus && itemStatus !== filters.inventoryStatus) return false;
      
      // Dates (simple logic: check if any of the item's dates fall in range)
      if (filters.dateFrom) {
        const fromDate = new Date(filters.dateFrom).getTime();
        const mfg = item.manufacturing_date ? new Date(item.manufacturing_date).getTime() : 0;
        const exp = item.expiry_date ? new Date(item.expiry_date).getTime() : 0;
        if ((mfg && mfg < fromDate) && (exp && exp < fromDate)) return false;
      }
      if (filters.dateTo) {
        const toDate = new Date(filters.dateTo).getTime();
        const mfg = item.manufacturing_date ? new Date(item.manufacturing_date).getTime() : Infinity;
        const exp = item.expiry_date ? new Date(item.expiry_date).getTime() : Infinity;
        if ((mfg && mfg > toDate) && (exp && exp > toDate)) return false;
      }
      
      return true;
    });
  }, [inventoryItems, products, filters]);

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
          <p className="text-sm text-gray-500 mt-1">{total} total items in database</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={fetchData} disabled={isLoading}>
            <RefreshCw className={`size-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button className="gap-2" onClick={() => setIsIntakeOpen(true)}>
            <Plus className="size-4" />
            New Intake
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
      )}
      
      {/* Search and Filters Bar */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
            <Input 
              placeholder="Search by product name, barcode, or batch number..." 
              className="pl-9 bg-gray-50 border-gray-200 text-gray-900"
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            />
          </div>
          <Button 
            variant="outline" 
            className={`gap-2 ${showFilters ? 'bg-primary/5 border-primary/30 text-primary' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="size-4" />
            Filters
            {Object.values(filters).filter(v => v !== "" && v !== filters.search).length > 0 && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-primary text-primary-foreground text-xs font-bold">
                {Object.values(filters).filter(v => v !== "" && v !== filters.search).length}
              </span>
            )}
          </Button>
          {(Object.values(filters).some(v => v !== "")) && (
            <Button 
              variant="ghost" 
              className="text-gray-500 hover:text-red-600"
              onClick={() => setFilters({
                search: "", category: "", brand: "", inventoryStatus: "", 
                scanStatus: "", ocrStatus: "", manualReviewStatus: "", 
                warehouse: "", storageLocation: "", dateFrom: "", dateTo: ""
              })}
            >
              <X className="size-4 mr-1" /> Clear
            </Button>
          )}
        </div>
        
        {showFilters && (
          <div className="pt-4 border-t border-gray-100 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <div className="space-y-1.5">
              <Label className="text-xs text-gray-500">Category</Label>
              <Input 
                placeholder="All Categories" 
                className="h-9 text-sm text-gray-900 bg-white" 
                value={filters.category}
                onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-gray-500">Brand</Label>
              <Input 
                placeholder="All Brands" 
                className="h-9 text-sm text-gray-900 bg-white" 
                value={filters.brand}
                onChange={(e) => setFilters(prev => ({ ...prev, brand: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-gray-500">Inventory Status</Label>
              <select 
                className="flex h-9 w-full items-center justify-between rounded-md border border-input bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
                value={filters.inventoryStatus}
                onChange={(e) => setFilters(prev => ({ ...prev, inventoryStatus: e.target.value }))}
              >
                <option value="">All Statuses</option>
                <option value="ACCEPTED">Accepted</option>
                <option value="REJECTED">Rejected</option>
                <option value="PRIORITY_SALE">Priority Sale</option>
                <option value="MANUAL_REVIEW">Manual Review</option>
                <option value="PENDING">Pending</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-gray-500">Manual Review Status</Label>
              <select 
                className="flex h-9 w-full items-center justify-between rounded-md border border-input bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
                value={filters.manualReviewStatus}
                onChange={(e) => setFilters(prev => ({ ...prev, manualReviewStatus: e.target.value }))}
              >
                <option value="">All</option>
                <option value="PENDING">Pending Review</option>
                <option value="RESOLVED">Resolved</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-gray-500">Warehouse</Label>
              <Input 
                placeholder="Any Warehouse" 
                className="h-9 text-sm text-gray-900 bg-white" 
                value={filters.warehouse}
                onChange={(e) => setFilters(prev => ({ ...prev, warehouse: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-gray-500">Storage Location</Label>
              <Input 
                placeholder="Any Location" 
                className="h-9 text-sm text-gray-900 bg-white" 
                value={filters.storageLocation}
                onChange={(e) => setFilters(prev => ({ ...prev, storageLocation: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-gray-500">Date From</Label>
              <Input 
                type="date" 
                className="h-9 text-sm text-gray-900 bg-white" 
                value={filters.dateFrom}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs text-gray-500">Date To</Label>
              <Input 
                type="date" 
                className="h-9 text-sm text-gray-900 bg-white" 
                value={filters.dateTo}
                onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
              />
            </div>
          </div>
        )}
      </div>

      <Card className="bg-white border-gray-200 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-gray-900">Inventory Items</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-16 text-gray-500">
              <Loader2 className="size-6 animate-spin mr-3 text-primary" />
              Loading inventory...
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <p className="font-medium">No inventory items found</p>
              <p className="text-sm mt-1">Click "New Intake" to add a product to inventory.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Product</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Batch #</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">MFG Date</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">EXP Date</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Days Left</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">ML Decision</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white">
                  {filteredItems.map((item) => {
                    const product = products[item.product_id];
                    return (
                      <tr
                        key={item.id}
                        className="border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer text-gray-900"
                        onClick={() => handleViewItem(item)}
                      >
                        <td className="py-3 px-4">
                          <div className="font-medium text-gray-900 text-sm">{product?.name || "Unknown"}</div>
                          <div className="text-xs text-gray-400 font-mono">{product?.sku}</div>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600 font-mono">{item.batch_number || "—"}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">{item.manufacturing_date || "—"}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">{item.expiry_date || "—"}</td>
                        <td className={`py-3 px-4 text-sm ${getDaysColor(item.remaining_days)}`}>
                          {item.remaining_days !== null ? (
                            item.remaining_days < 0 ? `Expired ${Math.abs(item.remaining_days)}d ago` : `${item.remaining_days}d`
                          ) : "—"}
                        </td>
                        <td className="py-3 px-4"><StatusBadge status={item.status} /></td>
                        <td className="py-3 px-4">
                          {item.ml_decision ? (
                            <span className={`text-xs font-bold ${
                                  item.ml_decision === 'ACCEPTED' ? 'text-emerald-500' :
                                  item.ml_decision === 'PRIORITY_SALE' ? 'text-orange-500' : 'text-red-500'
                                }`}>
                              {item.ml_decision}
                            </span>
                          ) : (
                            <span className="text-xs text-gray-400">PENDING</span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-gray-500 hover:text-gray-900"
                              onClick={(e) => { e.stopPropagation(); handleViewItem(item); }}
                              title="View Details"
                            >
                              <Eye className="size-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-blue-500 hover:text-blue-700"
                              onClick={(e) => { 
                                e.stopPropagation(); 
                                setSelectedItem(item);
                                setIsEditOpen(true);
                              }}
                              title="Edit Item"
                            >
                              <Edit className="size-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-red-500 hover:text-red-700"
                              onClick={(e) => { 
                                e.stopPropagation(); 
                                setSelectedItem(item);
                                setIsDeleteOpen(true);
                              }}
                              title="Delete Item"
                            >
                              <Trash2 className="size-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Item Detail Modal */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Inventory Item Details</DialogTitle>
          </DialogHeader>
          {selectedItem && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-500">Product</div>
                  <div className="font-medium">{products[selectedItem.product_id]?.name || "Unknown"}</div>
                </div>
                <div>
                  <div className="text-gray-500">SKU</div>
                  <div className="font-mono">{products[selectedItem.product_id]?.sku || "—"}</div>
                </div>
                <div>
                  <div className="text-gray-500">Batch Number</div>
                  <div className="font-mono">{selectedItem.batch_number || "—"}</div>
                </div>
                <div>
                  <div className="text-gray-500">Status</div>
                  <div className="mt-0.5"><StatusBadge status={selectedItem.status} /></div>
                </div>
                <div>
                  <div className="text-gray-500">Manufacturing Date</div>
                  <div>{selectedItem.manufacturing_date || "—"}</div>
                </div>
                <div>
                  <div className="text-gray-500">Expiry Date</div>
                  <div>{selectedItem.expiry_date || "—"}</div>
                </div>
                <div>
                  <div className="text-gray-500">Days Remaining</div>
                  <div className={getDaysColor(selectedItem.remaining_days)}>
                    {selectedItem.remaining_days !== null
                      ? selectedItem.remaining_days < 0
                        ? `Expired ${Math.abs(selectedItem.remaining_days)} days ago`
                        : `${selectedItem.remaining_days} days`
                      : "—"}
                  </div>
                </div>
                <div>
                  <div className="text-gray-500">Intake Date</div>
                  <div>{selectedItem.created_at ? new Date(selectedItem.created_at).toLocaleDateString() : "—"}</div>
                </div>
              </div>
              
              {selectedItem.ml_decision && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-100">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <span>🤖</span> AI Shelf Life Analysis
                  </h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 block mb-1">Decision</span>
                      <span className={`font-bold ${
                          selectedItem.ml_decision === 'ACCEPTED' ? 'text-emerald-500' :
                          selectedItem.ml_decision === 'PRIORITY_SALE' ? 'text-orange-500' : 'text-red-500'
                        }`}>
                        {selectedItem.ml_decision}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 block mb-1">Confidence</span>
                      <span className="font-medium">
                        {selectedItem.ml_confidence ? `${(selectedItem.ml_confidence * 100).toFixed(1)}%` : "—"}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 block mb-1">Arrhenius Remaining</span>
                      <span className="font-medium">
                        {selectedItem.arrhenius_remaining ? `${selectedItem.arrhenius_remaining.toFixed(1)} days` : "—"}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 block mb-1">Processed At</span>
                      <span className="font-medium text-gray-600">
                        {selectedItem.ml_processed_at ? new Date(selectedItem.ml_processed_at).toLocaleString() : "—"}
                      </span>
                    </div>
                  </div>
                </div>
              )}
              
              {selectedItem.decision_reason && (
                <div className="p-3 bg-gray-50 rounded-lg text-sm">
                  <span className="text-gray-500 font-medium">Decision Reason: </span>
                  <span className="text-gray-700">{selectedItem.decision_reason}</span>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="secondary" onClick={() => setIsDetailOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      {/* Edit Item Modal */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="sm:max-w-md bg-white">
          <DialogHeader>
            <DialogTitle className="text-gray-900">Edit Inventory Item</DialogTitle>
          </DialogHeader>
          {selectedItem && (
            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label className="text-gray-900">Product</Label>
                <div className="text-sm font-medium text-gray-700 p-2 bg-gray-50 rounded-md border border-gray-200">
                  {products[selectedItem.product_id]?.name || "Unknown Product"}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="batch_number" className="text-gray-900">Batch Number</Label>
                <Input 
                  id="batch_number" 
                  name="batch_number"
                  defaultValue={selectedItem.batch_number || ""} 
                  className="bg-white border-gray-300 text-gray-900"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="manufacturing_date" className="text-gray-900">Manufacturing Date</Label>
                <Input 
                  id="manufacturing_date" 
                  name="manufacturing_date"
                  type="date"
                  defaultValue={selectedItem.manufacturing_date || ""} 
                  className="bg-white border-gray-300 text-gray-900"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="expiry_date" className="text-gray-900">Expiry Date</Label>
                <Input 
                  id="expiry_date" 
                  name="expiry_date"
                  type="date"
                  defaultValue={selectedItem.expiry_date || ""} 
                  className="bg-white border-gray-300 text-gray-900"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="status" className="text-gray-900">Status</Label>
                <select 
                  id="status"
                  name="status"
                  defaultValue="KEEP"
                  className="flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option value="KEEP">Keep Current ({selectedItem.status})</option>
                  <option value="ACCEPTED">Accepted</option>
                  <option value="REJECTED">Rejected</option>
                  <option value="PRIORITY_SALE">Priority Sale</option>
                  <option value="MANUAL_REVIEW">Manual Review</option>
                </select>
              </div>
              
              <DialogFooter className="pt-4">
                <Button type="button" variant="outline" onClick={() => setIsEditOpen(false)} className="text-gray-700">Cancel</Button>
                <Button type="submit" disabled={isUpdating}>
                  {isUpdating ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
                  Save Changes
                </Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <DialogContent className="sm:max-w-md bg-white">
          <DialogHeader>
            <DialogTitle className="text-gray-900">Delete Inventory Item</DialogTitle>
          </DialogHeader>
          <div className="py-4 text-gray-600">
            Are you sure you want to permanently delete this inventory item (Batch: <span className="font-semibold text-gray-900">{selectedItem?.batch_number || "Unknown"}</span>)? This action cannot be undone.
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteOpen(false)} className="text-gray-700">Cancel</Button>
            <Button variant="destructive" onClick={handleDelete} disabled={isUpdating}>
              {isUpdating ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
              Delete Permanently
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* New Intake Dialog */}
      <IntakeFormDialog
        open={isIntakeOpen}
        onClose={() => setIsIntakeOpen(false)}
        onSuccess={fetchData}
      />
    </div>
  );
}
