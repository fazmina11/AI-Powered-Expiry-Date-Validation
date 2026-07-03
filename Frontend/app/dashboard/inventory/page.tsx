"use client";

import { useState, useEffect } from "react";
import { Edit, Trash2, Eye, Plus, RefreshCw, AlertTriangle, CheckCircle, Clock, XCircle, Loader2 } from "lucide-react";
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

      <Card>
        <CardHeader className="pb-4">
          <CardTitle>Inventory Items</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-16 text-gray-500">
              <Loader2 className="size-6 animate-spin mr-3" />
              Loading inventory...
            </div>
          ) : inventoryItems.length === 0 ? (
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
                    <th className="text-left py-3 px-4 font-medium text-gray-500 text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {inventoryItems.map((item) => {
                    const product = products[item.product_id];
                    return (
                      <tr
                        key={item.id}
                        className="border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer"
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
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={(e) => { e.stopPropagation(); handleViewItem(item); }}
                          >
                            <Eye className="size-4" />
                          </Button>
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

      {/* New Intake Dialog */}
      <IntakeFormDialog
        open={isIntakeOpen}
        onClose={() => setIsIntakeOpen(false)}
        onSuccess={fetchData}
      />
    </div>
  );
}
