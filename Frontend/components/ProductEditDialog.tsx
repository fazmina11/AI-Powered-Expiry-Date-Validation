"use client";

import { useState, useEffect } from "react";
import { Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
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
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { productApi, Product, ProductUpdate } from "@/services/apiService";

interface ProductEditDialogProps {
  open: boolean;
  product: Product | null;
  onClose: () => void;
  onSuccess: (updatedProduct: Product) => void;
}

export function ProductEditDialog({
  open,
  product,
  onClose,
  onSuccess,
}: ProductEditDialogProps) {
  const [formData, setFormData] = useState<ProductUpdate>({
    name: "",
    brand: "",
    sku: "",
    barcode: "",
    category: "",
    warehouse_location: "",
    description: "",
    mrp: 0,
    is_perishable: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Populate form data when product changes
  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || "",
        brand: product.brand || "",
        sku: product.sku || "",
        barcode: product.barcode || "",
        category: product.category || "",
        warehouse_location: product.warehouse_location || "",
        description: product.description || "",
        mrp: product.mrp || 0,
        is_perishable: !!product.is_perishable,
      });
      setError("");
    }
  }, [product]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product) return;
    setError("");
    setIsLoading(true);

    try {
      const updated = await productApi.update(product.id, formData);
      onSuccess(updated);
      onClose();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-[550px] border border-slate-200/50 dark:border-slate-800/50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl shadow-2xl rounded-2xl overflow-hidden transition-all duration-300">
        <DialogHeader className="pb-4 border-b border-slate-100 dark:border-slate-800">
          <DialogTitle className="text-xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Edit Product Information
          </DialogTitle>
          <DialogDescription className="text-sm text-slate-500 dark:text-slate-400">
            Modify product master details. Updates will immediately propagate across the system.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-5 pt-4">
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800/30 rounded-lg">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5 col-span-2">
              <Label htmlFor="name" className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                Product Name *
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-slate-50/50 dark:bg-slate-950/30 border-slate-200 dark:border-slate-800 focus:ring-blue-500 rounded-lg transition-all"
                required
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="brand" className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                Brand
              </Label>
              <Input
                id="brand"
                value={formData.brand}
                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                className="bg-slate-50/50 dark:bg-slate-950/30 border-slate-200 dark:border-slate-800 focus:ring-blue-500 rounded-lg"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="category" className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                Category
              </Label>
              <Input
                id="category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="bg-slate-50/50 dark:bg-slate-950/30 border-slate-200 dark:border-slate-800 focus:ring-blue-500 rounded-lg"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="sku" className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                SKU *
              </Label>
              <Input
                id="sku"
                value={formData.sku}
                onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                className="bg-slate-50/50 dark:bg-slate-950/30 border-slate-200 dark:border-slate-800 focus:ring-blue-500 rounded-lg font-mono"
                required
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="barcode" className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                Barcode *
              </Label>
              <Input
                id="barcode"
                value={formData.barcode}
                onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
                className="bg-slate-50/50 dark:bg-slate-950/30 border-slate-200 dark:border-slate-800 focus:ring-blue-500 rounded-lg font-mono"
                required
              />
            </div>

            <div className="space-y-1.5 col-span-2">
              <Label htmlFor="warehouse_location" className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                Warehouse Location
              </Label>
              <Input
                id="warehouse_location"
                placeholder="e.g. AISLE-B4-SHELF2"
                value={formData.warehouse_location}
                onChange={(e) => setFormData({ ...formData, warehouse_location: e.target.value })}
                className="bg-slate-50/50 dark:bg-slate-950/30 border-slate-200 dark:border-slate-800 focus:ring-blue-500 rounded-lg"
              />
            </div>

            <div className="space-y-1.5 col-span-2">
              <Label htmlFor="mrp" className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                MRP (INR)
              </Label>
              <Input
                id="mrp"
                type="number"
                step="0.01"
                value={formData.mrp || ""}
                onChange={(e) => setFormData({ ...formData, mrp: parseFloat(e.target.value) || 0 })}
                className="bg-slate-50/50 dark:bg-slate-950/30 border-slate-200 dark:border-slate-800 focus:ring-blue-500 rounded-lg"
              />
            </div>

            <div className="space-y-1.5 col-span-2">
              <Label htmlFor="description" className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                Description
              </Label>
              <Textarea
                id="description"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="bg-slate-50/50 dark:bg-slate-950/30 border-slate-200 dark:border-slate-800 focus:ring-blue-500 rounded-lg resize-none"
              />
            </div>

            <div className="flex items-center space-x-2 pt-2 col-span-2">
              <Checkbox
                id="is_perishable"
                checked={formData.is_perishable}
                onCheckedChange={(checked) => setFormData({ ...formData, is_perishable: !!checked })}
                className="border-slate-300 rounded focus:ring-blue-500"
              />
              <Label htmlFor="is_perishable" className="text-sm font-medium text-slate-700 dark:text-slate-300 cursor-pointer select-none">
                This is a perishable product (requires active shelf-life tracking)
              </Label>
            </div>
          </div>

          <DialogFooter className="pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              className="border-slate-200 hover:bg-slate-50 rounded-lg transition-colors"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg px-5 shadow-lg shadow-blue-500/20 flex items-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Loader2 className="size-4 hidden" />
                  Save Changes
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
