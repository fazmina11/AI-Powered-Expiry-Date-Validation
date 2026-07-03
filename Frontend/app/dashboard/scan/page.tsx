"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Camera, XCircle, ScanLine, Loader2, AlertTriangle, RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";

// Custom Hooks
import { useCamera } from "@/hooks/useCamera";
import { useBarcodeScanner } from "@/hooks/useBarcodeScanner";
import { useOCR } from "@/hooks/useOCR";

// Components
import { CameraView } from "@/components/scan/CameraView";
import { BarcodeScannerOverlay } from "@/components/scan/BarcodeScannerOverlay";
import { OCRPreview } from "@/components/scan/OCRPreview";
import { ScanProgress, ScanStep } from "@/components/scan/ScanProgress";

// Services
import { scanFlowApi } from "@/services/scanService";
import { Product } from "@/services/apiService";

/* ─────────────────────────── Types ─────────────────────────── */
type SessionState = { id: string } | null;

type FlowStep =
  | "idle"        // page just loaded
  | "starting"    // waiting for backend session
  | "scanning"    // camera active, detecting barcode
  | "barcode_ok"  // barcode detected, show Capture button
  | "capturing"   // user clicked Capture
  | "ocr_running" // upload + OCR in progress
  | "ocr_done"    // OCR completed, show form
  | "finalizing"  // committing to DB
  | "saved"       // success
  | "cancelled";

function flowToScanStep(flow: FlowStep): ScanStep {
  const map: Record<FlowStep, ScanStep> = {
    idle: "idle",
    starting: "idle",
    scanning: "camera_ready",
    barcode_ok: "barcode_detected",
    capturing: "image_captured",
    ocr_running: "image_captured",
    ocr_done: "ocr_completed",
    finalizing: "ocr_completed",
    saved: "saved",
    cancelled: "idle",
  };
  return map[flow];
}

/* ─────────────────────────── Page ─────────────────────────── */
export default function ScanPage() {
  const { toast } = useToast();

  // Camera
  const { videoRef, status: camStatus, error: camError, devices, selectedDeviceId, startCamera, stopStream, switchCamera, captureDataUrl, captureBlob } = useCamera();

  // Session
  const [session, setSession] = useState<SessionState>(null);
  const [flowStep, setFlowStep] = useState<FlowStep>("idle");

  // Barcode
  const [detectedBarcode, setDetectedBarcode] = useState<string>("");
  const [product, setProduct] = useState<Product | null>(null);
  const [productLoading, setProductLoading] = useState(false);

  // Image
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const [imagePath, setImagePath] = useState<string | null>(null);

  // OCR
  const { ocrState, ocrData, setOcrData, imagePath: ocrImagePath, ocrError, runOCR, resetOCR } = useOCR(session?.id ?? null);

  // Misc
  const [isSaved, setIsSaved] = useState(false);
  const barcodeHandled = useRef(false);

  /* ── Handle barcode detection ── */
  const handleBarcodeDetected = useCallback(async (code: string) => {
    if (barcodeHandled.current || !session) return;
    barcodeHandled.current = true;
    setDetectedBarcode(code);
    setProductLoading(true);
    setFlowStep("barcode_ok");

    try {
      const res = await scanFlowApi.submitBarcode(session.id, code);
      setProduct(res.product);
      if (res.product) {
        toast({ title: `Product found`, description: res.product.name });
      } else {
        toast({ title: "Unknown product", description: "Barcode not in database. You can still proceed.", variant: "destructive" });
      }
    } catch (err: any) {
      toast({ title: "Barcode lookup failed", description: err.message, variant: "destructive" });
    } finally {
      setProductLoading(false);
    }
  }, [session, toast]);

  /* ── Barcode scanner hook ── */
  const barcodeScanActive = flowStep === "scanning" && camStatus === "active";
  const { scanState, resetScanner } = useBarcodeScanner({
    videoRef,
    active: barcodeScanActive,
    onDetected: handleBarcodeDetected,
    intervalMs: 200,
  });

  /* ── Start session ── */
  const handleStartScan = useCallback(async () => {
    setFlowStep("starting");
    try {
      const res = await scanFlowApi.startScan();
      setSession({ id: res.session_id });
      // Start camera immediately
      await startCamera();
      setFlowStep("scanning");
    } catch (err: any) {
      toast({ title: "Failed to start session", description: err.message, variant: "destructive" });
      setFlowStep("idle");
    }
  }, [startCamera, toast]);

  /* ── Camera status tracker ── */
  useEffect(() => {
    // Once camera is active and we're in scanning state, update progress
  }, [camStatus]);

  /* ── Capture label ── */
  const handleCapture = useCallback(async () => {
    setFlowStep("capturing");
    const dataUrl = captureDataUrl();
    const file = await captureBlob();
    if (!dataUrl || !file) {
      toast({ title: "Capture failed", description: "Could not grab frame from camera.", variant: "destructive" });
      setFlowStep("barcode_ok");
      return;
    }
    setImagePreview(dataUrl);
    setCapturedFile(file);
    setFlowStep("ocr_running");
    await runOCR(file, dataUrl);
    // imagePath is now available in ocrImagePath from the hook
    setFlowStep("ocr_done");
  }, [captureDataUrl, captureBlob, runOCR, toast]);

  /* ── Retake ── */
  const handleRetake = useCallback(() => {
    setImagePreview(null);
    setCapturedFile(null);
    setImagePath(null);
    resetOCR();
    barcodeHandled.current = true; // keep barcode, but allow re-capture
    setFlowStep("barcode_ok");
  }, [resetOCR]);

  /* ── Finalize / Save ── */
  const handleFinalize = useCallback(async () => {
    if (!session || !detectedBarcode) {
      toast({ title: "Missing data", description: "Session or barcode not ready.", variant: "destructive" });
      return;
    }
    const ip = ocrImagePath || imagePath;
    if (!ip) {
      toast({ title: "Image not uploaded", description: "Please capture the product label first.", variant: "destructive" });
      return;
    }
    setFlowStep("finalizing");
    try {
      await scanFlowApi.finalize(session.id, detectedBarcode, ip, ocrData);
      setIsSaved(true);
      setFlowStep("saved");
      toast({ title: "Saved!", description: "Inventory item created successfully." });
    } catch (err: any) {
      toast({ title: "Save failed", description: err.message, variant: "destructive" });
      setFlowStep("ocr_done");
    }
  }, [session, detectedBarcode, imagePath, ocrImagePath, ocrData, toast]);

  // imagePath is fully managed by the useOCR hook above (exposed as ocrImagePath)
  // No need for a duplicate call here

  /* ── Cancel / Reset ── */
  const handleCancel = useCallback(async () => {
    if (session) {
      try { await scanFlowApi.cancel(session.id); } catch { /* swallow */ }
    }
    stopStream();
    setSession(null);
    setFlowStep("idle");
    setDetectedBarcode("");
    setProduct(null);
    setImagePreview(null);
    setCapturedFile(null);
    setImagePath(null);
    setIsSaved(false);
    barcodeHandled.current = false;
    resetOCR();
  }, [session, stopStream, resetOCR]);

  const handleNextProduct = useCallback(async () => {
    await handleCancel();
    // Auto-start for convenience
  }, [handleCancel]);

  /* ─────────── Idle / Entry Screen ─────────── */
  if (flowStep === "idle" || flowStep === "starting") {
    return (
      <div className="flex h-[calc(100vh-80px)] items-center justify-center bg-slate-950 p-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-6 max-w-sm"
        >
          <div className="mx-auto size-24 rounded-full bg-blue-600/10 border border-blue-600/30 flex items-center justify-center">
            <ScanLine className="size-12 text-blue-500" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Ready to Scan</h1>
            <p className="text-slate-400 mt-2 text-sm">
              Initialize a secure scan session. The camera will open automatically.
            </p>
          </div>
          <Button
            size="lg"
            onClick={handleStartScan}
            disabled={flowStep === "starting"}
            className="bg-blue-600 hover:bg-blue-500 text-white rounded-full px-10 py-6 text-base font-semibold gap-3"
          >
            {flowStep === "starting"
              ? <><Loader2 className="size-5 animate-spin" /> Starting session...</>
              : <><Camera className="size-5" /> Start New Scan</>
            }
          </Button>
        </motion.div>
      </div>
    );
  }

  /* ─────────── Main Scan UI ─────────── */
  const isFinalizing = flowStep === "finalizing";
  const isOcrRunning = flowStep === "ocr_running" || ocrState === "uploading" || ocrState === "processing";

  return (
    <div className="min-h-[calc(100vh-80px)] bg-slate-950 p-4 lg:p-6 flex flex-col gap-4 text-slate-200">

      {/* ── Header ── */}
      <div className="flex items-center justify-between bg-slate-900/60 backdrop-blur px-5 py-3 rounded-xl border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="size-2 rounded-full bg-emerald-400 animate-pulse" />
          <h1 className="text-base font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            AI Powered Expiry Validation
          </h1>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCancel}
          className="text-slate-400 hover:text-red-400 hover:bg-red-400/10 gap-1.5 text-xs"
        >
          <XCircle className="size-4" /> Cancel Session
        </Button>
      </div>

      {/* ── Main Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1">

        {/* LEFT — Camera */}
        <div className="lg:col-span-4 flex flex-col gap-3">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
            <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-200">Live Camera</span>
              {camStatus === "active" && (
                <span className="text-xs text-emerald-400 flex items-center gap-1.5">
                  <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Live
                </span>
              )}
            </div>
            <div className="p-3">
              <CameraView
                videoRef={videoRef}
                status={camStatus}
                error={camError}
                devices={devices}
                selectedDeviceId={selectedDeviceId}
                onStart={() => startCamera()}
                onSwitch={switchCamera}
                imagePreview={imagePreview}
              >
                {/* Barcode overlay — only show during scanning */}
                {flowStep === "scanning" && (
                  <BarcodeScannerOverlay
                    scanState={scanState}
                    detectedCode={detectedBarcode}
                  />
                )}
              </CameraView>
            </div>

            {/* Camera controls */}
            <div className="px-3 pb-3 flex gap-2">
              {flowStep === "barcode_ok" && !imagePreview && (
                <Button
                  onClick={handleCapture}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white gap-2"
                >
                  <Camera className="size-4" /> Capture Product Label
                </Button>
              )}

              {imagePreview && !isSaved && (
                <>
                  <Button
                    variant="outline"
                    onClick={handleRetake}
                    disabled={isOcrRunning || isFinalizing}
                    className="flex-1 border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 gap-1.5"
                  >
                    <RefreshCw className="size-4" /> Retake
                  </Button>

                  {isOcrRunning && (
                    <Button disabled className="flex-1 bg-amber-600/40 text-amber-200 cursor-not-allowed gap-1.5">
                      <Loader2 className="size-4 animate-spin" />
                      {ocrState === "uploading" ? "Uploading..." : "Extracting..."}
                    </Button>
                  )}
                </>
              )}

              {flowStep === "scanning" && (
                <div className="w-full text-center text-xs text-slate-500 py-2">
                  Aim camera at the barcode...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* MIDDLE — Product Info */}
        <div className="lg:col-span-3 bg-slate-900/60 border border-slate-800 rounded-xl flex flex-col">
          <div className="px-4 py-3 bg-slate-900 border-b border-slate-800">
            <span className="text-sm font-semibold text-slate-200">Product Information</span>
          </div>

          <div className="p-4 flex-1 space-y-4">
            {/* Barcode */}
            <div>
              <Label className="text-slate-500 text-xs uppercase tracking-wider">Barcode</Label>
              <div className={`mt-1.5 font-mono text-sm bg-slate-950 px-3 py-2 rounded-lg border transition-colors duration-300 ${detectedBarcode ? "border-blue-700 text-blue-300" : "border-slate-800 text-slate-600"}`}>
                {detectedBarcode || "—"}
              </div>
            </div>

            <AnimatePresence>
              {productLoading && (
                <motion.div key="pload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="flex items-center gap-2 text-slate-400 text-sm">
                  <Loader2 className="size-4 animate-spin" /> Looking up product...
                </motion.div>
              )}

              {!productLoading && product && (
                <motion.div key="product" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
                  className="space-y-3">
                  {[
                    { label: "Product Name", value: product.name },
                    { label: "Brand", value: (product as any).brand || "—" },
                    { label: "Category", value: (product as any).category || "—" },
                    { label: "Description", value: (product as any).description || "—" },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <Label className="text-slate-500 text-xs uppercase tracking-wider">{label}</Label>
                      <div className="text-slate-200 text-sm mt-1 line-clamp-3">{value}</div>
                    </div>
                  ))}
                </motion.div>
              )}

              {!productLoading && detectedBarcode && !product && (
                <motion.div key="notfound" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className="flex gap-2 p-3 bg-orange-950/30 border border-orange-900/50 rounded-lg text-orange-400 text-sm">
                  <AlertTriangle className="size-5 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">Unknown Product</p>
                    <p className="text-xs mt-1 text-orange-400/80">Barcode not in database. Proceed and map later.</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* RIGHT — OCR Preview */}
        <div className="lg:col-span-5 bg-slate-900/60 border border-slate-800 rounded-xl flex flex-col overflow-hidden">
          <OCRPreview
            ocrState={ocrState}
            ocrError={ocrError}
            ocrData={ocrData}
            onOcrDataChange={setOcrData}
            onConfirm={handleFinalize}
            onNextProduct={handleNextProduct}
            isFinalizing={isFinalizing}
            isSaved={isSaved}
          />
        </div>
      </div>

      {/* BOTTOM — Progress */}
      <ScanProgress
        currentStep={flowToScanStep(flowStep)}
        isProcessing={isOcrRunning || isFinalizing}
      />
    </div>
  );
}
