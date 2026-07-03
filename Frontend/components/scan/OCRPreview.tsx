"use client";

import { OCRData } from "@/services/scanService";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Save, Loader2, CheckCircle2, RefreshCcw } from "lucide-react";
import { OCRState } from "@/hooks/useOCR";
import { motion, AnimatePresence } from "framer-motion";

interface OCRPreviewProps {
  ocrState: OCRState;
  ocrError: string | null;
  ocrData: OCRData;
  onOcrDataChange: (data: OCRData) => void;
  onConfirm: () => void;
  onNextProduct: () => void;
  isFinalizing: boolean;
  isSaved: boolean;
}

function FieldRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <Label className="text-slate-400 text-xs uppercase tracking-wider">{label}</Label>
      {children}
    </div>
  );
}

export function OCRPreview({
  ocrState,
  ocrError,
  ocrData,
  onOcrDataChange,
  onConfirm,
  onNextProduct,
  isFinalizing,
  isSaved,
}: OCRPreviewProps) {
  const update = (key: keyof OCRData) => (e: React.ChangeEvent<HTMLInputElement>) =>
    onOcrDataChange({ ...ocrData, [key]: e.target.value });

  const isEditable = ocrState === "completed" && !isSaved;
  const isLoading = ocrState === "uploading" || ocrState === "processing";

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-slate-900 border-b border-slate-800">
        <span className="font-semibold text-slate-200">OCR Result</span>
        <AnimatePresence mode="wait">
          {ocrState === "uploading" && (
            <motion.span key="u" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded-full flex items-center gap-1.5">
              <Loader2 className="size-3 animate-spin" /> Uploading...
            </motion.span>
          )}
          {ocrState === "processing" && (
            <motion.span key="p" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="text-xs bg-amber-900/50 text-amber-300 px-2 py-1 rounded-full flex items-center gap-1.5">
              <Loader2 className="size-3 animate-spin" /> Extracting OCR...
            </motion.span>
          )}
          {ocrState === "completed" && ocrData.confidence != null && (
            <motion.span key="c" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
              className="text-xs bg-emerald-900/50 text-emerald-400 px-2 py-1 rounded-full">
              {(ocrData.confidence * 100).toFixed(0)}% confidence
            </motion.span>
          )}
          {ocrState === "error" && (
            <motion.span key="e" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="text-xs bg-red-900/50 text-red-400 px-2 py-1 rounded-full">
              OCR Failed
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4">
        <AnimatePresence mode="wait">
          {/* Idle placeholder */}
          {ocrState === "idle" && (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-48 text-center gap-2 text-slate-600">
              <div className="size-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-700 text-xl">🔍</div>
              <p className="text-sm">OCR data will appear after label capture</p>
            </motion.div>
          )}

          {/* Loading skeleton */}
          {isLoading && (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="space-y-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="space-y-1.5">
                  <div className="h-3 w-20 bg-slate-800 rounded animate-pulse" />
                  <div className="h-9 w-full bg-slate-800/60 rounded-md animate-pulse" />
                </div>
              ))}
            </motion.div>
          )}

          {/* Error state */}
          {ocrState === "error" && (
            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="p-4 bg-red-950/30 border border-red-900/50 rounded-lg text-red-400 text-sm">
              {ocrError || "An unknown OCR error occurred. Please retake the image."}
            </motion.div>
          )}

          {/* OCR Form */}
          {(ocrState === "completed") && (
            <motion.div key="form" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <FieldRow label="MFG Date">
                  <Input disabled={!isEditable} value={ocrData.manufacturing_date || ""} onChange={update("manufacturing_date")}
                    className="bg-slate-950 border-slate-700 text-slate-200 disabled:opacity-70" />
                </FieldRow>
                <FieldRow label="EXP Date">
                  <Input disabled={!isEditable} value={ocrData.expiry_date || ""} onChange={update("expiry_date")}
                    className="bg-slate-950 border-slate-700 text-slate-200 disabled:opacity-70" />
                </FieldRow>
                <FieldRow label="Batch Number">
                  <Input disabled={!isEditable} value={ocrData.batch_number || ""} onChange={update("batch_number")}
                    className="bg-slate-950 border-slate-700 text-slate-200 disabled:opacity-70" />
                </FieldRow>
                <FieldRow label="Packed Date">
                  <Input disabled={!isEditable} value={ocrData.packed_date || ""} onChange={update("packed_date")}
                    className="bg-slate-950 border-slate-700 text-slate-200 disabled:opacity-70" />
                </FieldRow>
                <FieldRow label="MRP">
                  <Input disabled={!isEditable} type="number" value={ocrData.mrp || ""} onChange={e => onOcrDataChange({ ...ocrData, mrp: parseFloat(e.target.value) || undefined })}
                    className="bg-slate-950 border-slate-700 text-slate-200 disabled:opacity-70" />
                </FieldRow>
                <FieldRow label="Product Name">
                  <Input disabled={!isEditable} value={ocrData.product_name || ""} onChange={update("product_name")}
                    className="bg-slate-950 border-slate-700 text-slate-200 disabled:opacity-70" />
                </FieldRow>
              </div>

              {ocrData.raw_text && (
                <FieldRow label="Raw OCR Text">
                  <div className="mt-1 p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-500 max-h-28 overflow-y-auto whitespace-pre-wrap">
                    {ocrData.raw_text}
                  </div>
                </FieldRow>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer CTA */}
      <div className="p-4 bg-slate-900 border-t border-slate-800">
        <AnimatePresence mode="wait">
          {isSaved ? (
            <motion.div key="saved" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col gap-2">
              <div className="flex items-center justify-center gap-2 text-emerald-400 text-sm font-medium py-2">
                <CheckCircle2 className="size-5" /> Inventory Saved Successfully!
              </div>
              <Button variant="outline" onClick={onNextProduct}
                className="w-full border-slate-700 text-slate-300 hover:bg-slate-800 gap-2">
                <RefreshCcw className="size-4" /> Scan Next Product
              </Button>
            </motion.div>
          ) : (
            <motion.div key="confirm" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Button
                onClick={onConfirm}
                disabled={ocrState !== "completed" || isFinalizing}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 gap-2"
              >
                {isFinalizing
                  ? <><Loader2 className="size-4 animate-spin" /> Saving...</>
                  : <><Save className="size-4" /> Confirm & Save</>
                }
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
