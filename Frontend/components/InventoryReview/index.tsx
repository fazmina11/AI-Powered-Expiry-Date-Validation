import { CheckCircle, XCircle, AlertTriangle, Clock, Loader2, Save } from "lucide-react";
import { ScanResult, inventoryApi } from "@/services/apiService";
import { useState } from "react";
import { Button } from "@/components/ui/button";

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

interface InventoryReviewProps {
  result: ScanResult;
  onSaveComplete: () => void;
}

export function InventoryReview({ result, onSaveComplete }: InventoryReviewProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState("");

  const handleSave = async () => {
    if (!result.db_records || !result.db_records.product_id) {
      setSaveError("Missing product ID in database records. Cannot save.");
      return;
    }
    
    setIsSaving(true);
    setSaveError("");
    try {
      await inventoryApi.intake({
        product_id: result.db_records.product_id,
        barcode_scan_id: result.db_records.barcode_scan_id,
        ocr_result_id: result.db_records.ocr_result_id,
        batch_number: result.batch?.batch_number || undefined,
        manufacturing_date: result.manufacturing?.manufacturing_date || undefined,
        expiry_date: result.expiry?.expiry_date || undefined,
        status: result.status === "PASS" ? "ACCEPTED" : "MANUAL_REVIEW"
      });
      onSaveComplete();
    } catch (err) {
      setSaveError((err as Error).message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-900">Extracted Data</h3>
        <StatusBadge status={result.status || "UNKNOWN"} />
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        {result.barcode?.value && (
          <div className="col-span-2">
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">Barcode</div>
            <div className="font-mono text-gray-900 bg-gray-50 px-3 py-1.5 rounded-lg border">{result.barcode.value}</div>
          </div>
        )}
        {result.product?.name && (
          <div className="col-span-2">
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">Product Name</div>
            <div className="font-medium text-gray-900">{result.product.name}</div>
          </div>
        )}
        {result.product?.brand && (
          <div>
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">Brand</div>
            <div className="font-medium text-gray-900">{result.product.brand}</div>
          </div>
        )}
        {result.product?.category && (
          <div>
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">Category</div>
            <div className="font-medium text-gray-900">{result.product.category}</div>
          </div>
        )}
        {result.product?.description && (
          <div className="col-span-2">
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">Description</div>
            <div className="font-medium text-gray-900 line-clamp-3">{result.product.description}</div>
          </div>
        )}
        {result.batch?.batch_number && (
          <div className="col-span-2">
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">Batch Number</div>
            <div className="font-mono text-gray-900">{result.batch.batch_number}</div>
          </div>
        )}
        {result.manufacturing?.manufacturing_date && (
          <div>
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">MFG Date</div>
            <div className="font-medium text-gray-900">{result.manufacturing.manufacturing_date}</div>
          </div>
        )}
        {result.expiry?.expiry_date && (
          <div>
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">EXP Date</div>
            <div className="font-medium text-gray-900">{result.expiry.expiry_date}</div>
          </div>
        )}
        {result.ocr?.confidence !== undefined && result.ocr?.confidence !== null && (
          <div className="col-span-2">
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">OCR Confidence</div>
            <div className="font-medium text-gray-900">{(result.ocr.confidence * 100).toFixed(0)}%</div>
          </div>
        )}
        {result.ocr?.raw_text && (
          <div className="col-span-2">
            <div className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-1">Raw OCR Text</div>
            <div className="font-mono text-gray-900 text-xs bg-gray-50 p-2 rounded border max-h-32 overflow-y-auto whitespace-pre-wrap">
              {result.ocr.raw_text}
            </div>
          </div>
        )}
        {result.reject_reason && (
          <div className="col-span-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-xs font-medium text-red-700">Rejection Reason</div>
            <div className="text-sm text-red-800 mt-0.5">{result.reject_reason}</div>
          </div>
        )}
      </div>

      <div className="pt-4 mt-4 border-t border-gray-100 space-y-4">
        {saveError && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
            {saveError}
          </div>
        )}
        
        <Button 
          className="w-full bg-green-600 hover:bg-green-700 text-white font-medium"
          size="lg"
          onClick={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <Loader2 className="size-5 mr-2 animate-spin" />
          ) : (
            <Save className="size-5 mr-2" />
          )}
          Save to Inventory
        </Button>
      </div>
    </div>
  );
}
