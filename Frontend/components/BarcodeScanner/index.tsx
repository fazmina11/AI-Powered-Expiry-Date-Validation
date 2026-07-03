import { Search, Loader2, Package, CheckCircle, XCircle, AlertTriangle, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Product, InventoryItem } from "@/services/apiService";

function StatusBadge({ status }: { status: string }) {
  const s = (status || "").toUpperCase();
  if (s === "ACCEPTED" || s === "PASS")
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold bg-green-100 text-green-800 border border-green-200">
        <CheckCircle className="size-4" /> Accepted
      </span>
    );
  if (s === "REJECTED" || s === "FAIL")
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold bg-red-100 text-red-800 border border-red-200">
        <XCircle className="size-4" /> Rejected
      </span>
    );
  if (s === "PRIORITY_SALE")
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold bg-orange-100 text-orange-800 border border-orange-200">
        <AlertTriangle className="size-4" /> Priority Sale
      </span>
    );
  if (s.includes("REVIEW") || s.includes("INCOMPLETE"))
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-800 border border-yellow-200">
        <Clock className="size-4" /> Needs Review
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold bg-gray-100 text-gray-700 border border-gray-200">
      {status}
    </span>
  );
}

function BarcodeResult({
  product,
  inventory,
}: {
  product: Product;
  inventory: InventoryItem[];
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-blue-100 rounded-lg">
          <Package className="size-5 text-blue-600" />
        </div>
        <div>
          <div className="font-semibold text-gray-900">{product.name}</div>
          <div className="text-sm text-gray-500">{product.category} · SKU: {product.sku}</div>
          {product.brand && <div className="text-sm text-gray-500">Brand: {product.brand}</div>}
        </div>
      </div>

      {inventory.length > 0 ? (
        <div>
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            Recent Inventory Batches
          </div>
          <div className="space-y-2">
            {inventory.slice(0, 5).map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between text-sm p-2.5 bg-gray-50 rounded-lg border"
              >
                <div>
                  <div className="font-mono text-xs text-gray-500">{item.batch_number || "—"}</div>
                  <div className="text-gray-700">
                    EXP: {item.expiry_date || "N/A"}
                    {item.remaining_days !== null && (
                      <span className={`ml-2 text-xs ${item.remaining_days < 0 ? "text-red-600" : item.remaining_days <= 30 ? "text-orange-600" : "text-green-600"}`}>
                        ({item.remaining_days < 0 ? "expired" : `${item.remaining_days}d left`})
                      </span>
                    )}
                  </div>
                </div>
                <StatusBadge status={item.status} />
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-sm text-gray-400 italic">No inventory batches recorded yet.</div>
      )}
    </div>
  );
}

interface BarcodeScannerProps {
  barcodeInput: string;
  setBarcodeInput: (val: string) => void;
  handleBarcodeSearch: (val: string) => void;
  isBarcodeLoading: boolean;
  barcodeError: string;
  barcodeNotFound: boolean;
  barcodeProduct: Product | null;
  barcodeInventory: InventoryItem[];
}

export function BarcodeScanner({
  barcodeInput,
  setBarcodeInput,
  handleBarcodeSearch,
  isBarcodeLoading,
  barcodeError,
  barcodeNotFound,
  barcodeProduct,
  barcodeInventory
}: BarcodeScannerProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Product Lookup</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Barcode (Manual Entry)</Label>
          <div className="flex gap-2">
            <Input
              value={barcodeInput}
              onChange={(e) => setBarcodeInput(e.target.value)}
              placeholder="Scan or type barcode"
              onKeyDown={(e) => e.key === "Enter" && handleBarcodeSearch(barcodeInput)}
            />
            <Button
              variant="secondary"
              onClick={() => handleBarcodeSearch(barcodeInput)}
              disabled={isBarcodeLoading || !barcodeInput.trim()}
            >
              {isBarcodeLoading ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
            </Button>
          </div>
        </div>

        {barcodeError && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
            {barcodeError}
          </div>
        )}

        {barcodeNotFound && (
          <div className="text-sm text-yellow-700 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
            Product not found. Scanning the image will attempt to extract new product info.
          </div>
        )}

        {barcodeProduct && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <BarcodeResult product={barcodeProduct} inventory={barcodeInventory} />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
