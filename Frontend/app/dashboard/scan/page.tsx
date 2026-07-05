"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Camera, XCircle, ScanLine, Loader2, AlertTriangle, CheckCircle2, History, Info, Play, Pause
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Custom Hooks
import { useCamera } from "@/hooks/useCamera";
import { useBarcodeScanner } from "@/hooks/useBarcodeScanner";

// Components
import { CameraView } from "@/components/scan/CameraView";
import { BarcodeScannerOverlay } from "@/components/scan/BarcodeScannerOverlay";
import { ScanProgress, ScanStep } from "@/components/scan/ScanProgress";
import { OCRImageHighlight } from "@/components/scan/OCRImageHighlight";

// Services
import { scanFlowApi, OCRHistoryItem, OCRData } from "@/services/scanService";
import { Product } from "@/services/apiService";

/* ─────────────────────────── Types ─────────────────────────── */
type SessionState = { id: string } | null;

type FlowStep =
  | "idle"        // page just loaded
  | "starting"    // waiting for backend session
  | "scanning"    // camera active, detecting barcode
  | "barcode_ok"  // barcode detected
  | "capturing"   // clear frame auto-detected and capturing
  | "cancelled";

function flowToScanStep(flow: FlowStep): ScanStep {
  const map: Record<FlowStep, ScanStep> = {
    idle: "idle",
    starting: "idle",
    scanning: "camera_ready",
    barcode_ok: "barcode_detected",
    capturing: "image_captured",
    cancelled: "idle",
  };
  return map[flow];
}

function playScanBeep() {
  try {
    const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.type = "sine";
    oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // A5 note
    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);

    oscillator.start();
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
    oscillator.stop(audioCtx.currentTime + 0.15);
  } catch (err) {
    console.error("Audio beep failed:", err);
  }
}

/* ─────────────────────────── Page ─────────────────────────── */
export default function ScanPage() {
  const { toast } = useToast();

  const getFullImageUrl = useCallback((url: string | null) => {
    if (!url) return "";
    if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("blob:") || url.startsWith("data:")) {
      return url;
    }
    return `http://localhost:8001${url}`;
  }, []);

  const getPipelineLogs = useCallback((item: OCRHistoryItem) => {
    const createdTime = item.created_at ? new Date(item.created_at) : new Date();
    const formatTime = (offsetSec: number) => {
      const t = new Date(createdTime.getTime() + offsetSec * 1000);
      return t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    };

    const logs = [
      `[${formatTime(0)}] [Queue] Task registered in background worker queue.`,
      `[${formatTime(0.5)}] [Queue] Worker thread locked task. Status set to 'processing'.`,
      `[${formatTime(1.2)}] [Pipeline] Initialized ScanPipelineService.`,
    ];

    if (item.status === "pending") {
      logs.push(`[${formatTime(2.0)}] [Queue] Waiting for free CPU worker thread...`);
      return logs;
    }

    logs.push(`[${formatTime(1.5)}] [Quality] Running frame clarity variance and glare checks...`);
    
    if (item.status === "processing") {
      logs.push(`[${formatTime(2.2)}] [Quality] Clarity check passed (lenient webcam threshold).`);
      logs.push(`[${formatTime(3.0)}] [OCR] Running local CPU PaddleOCR reader...`);
      return logs;
    }

    if (item.status === "failed") {
      if (item.failure_reason && item.failure_reason.includes("variance")) {
        logs.push(`[${formatTime(2.0)}] [Quality] QUALITY CHECK FAILED: Image is blurry.`);
        logs.push(`[${formatTime(2.1)}] [Pipeline] EARLY EXIT: Task aborted.`);
      } else if (item.failure_reason && item.failure_reason.includes("glare")) {
        logs.push(`[${formatTime(2.0)}] [Quality] QUALITY CHECK FAILED: Severe light reflection/glare.`);
        logs.push(`[${formatTime(2.1)}] [Pipeline] EARLY EXIT: Task aborted.`);
      } else {
        logs.push(`[${formatTime(2.2)}] [Quality] Clarity check passed.`);
        logs.push(`[${formatTime(3.0)}] [OCR] Running local CPU PaddleOCR reader...`);
        logs.push(`[${formatTime(4.1)}] [Pipeline] ERROR: ${item.failure_reason || 'Unknown pipeline crash'}`);
      }
      return logs;
    }

    // completed
    logs.push(`[${formatTime(2.2)}] [Quality] Clarity check passed.`);
    logs.push(`[${formatTime(3.0)}] [OCR] Running local CPU PaddleOCR reader...`);
    if (item.ocr_blocks && item.ocr_blocks.blocks) {
      logs.push(`[${formatTime(4.0)}] [OCR] Detected ${item.ocr_blocks.blocks.length} text coordinates.`);
    } else {
      logs.push(`[${formatTime(4.0)}] [OCR] Detected text blocks successfully.`);
    }
    logs.push(`[${formatTime(4.2)}] [Validation] Running date extraction regex parser...`);
    if (item.extracted_data.manufacturing_date || item.extracted_data.expiry_date) {
      logs.push(`[${formatTime(4.4)}] [Validation] Extracted MFG: ${item.extracted_data.manufacturing_date || 'N/A'}, EXP: ${item.extracted_data.expiry_date || 'N/A'}.`);
    }
    logs.push(`[${formatTime(4.6)}] [Pipeline] COMPLETE: Status set to 'completed'.`);
    return logs;
  }, []);

  // Camera
  const { videoRef, status: camStatus, error: camError, devices, selectedDeviceId, startCamera, stopStream, switchCamera, captureBlob } = useCamera();

  // Session & Flow
  const [session, setSession] = useState<SessionState>(null);
  const [flowStep, setFlowStep] = useState<FlowStep>("idle");

  // Barcode
  const [detectedBarcode, setDetectedBarcode] = useState<string>("");
  const [product, setProduct] = useState<Product | null>(null);
  const [productLoading, setProductLoading] = useState(false);
  const barcodeHandled = useRef(false);

  // Auto-Scan & Queue Settings
  const [autoScanEnabled, setAutoScanEnabled] = useState(true);
  const [detectionPaused, setDetectionPaused] = useState(false);
  const [isAnalyzingFrame, setIsAnalyzingFrame] = useState(false);
  const lastScanTime = useRef(0);

  // Scan Queue History
  const [history, setHistory] = useState<OCRHistoryItem[]>([]);
  const [activeItem, setActiveItem] = useState<OCRHistoryItem | null>(null);
  const [activeItemData, setActiveItemData] = useState<OCRData>({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmittingActive, setIsSubmittingActive] = useState(false);

  /* ── Fetch Scan History ── */
  const fetchHistory = useCallback(async () => {
    try {
      const list = await scanFlowApi.getHistory();
      setHistory(list);
    } catch (err: any) {
      console.error("Failed fetching scan history:", err);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  /* ── Poll individual enqueued scan status ── */
  const pollScanStatus = useCallback(async (resultId: string) => {
    const maxAttempts = 120; // max 180s (120 * 1.5s)
    let attempts = 0;
    
    const interval = setInterval(async () => {
      attempts++;
      try {
        const item = await scanFlowApi.getResultStatus(resultId);
        if (item.status === "completed" || item.status === "failed") {
          clearInterval(interval);
          setHistory(prev => prev.map(x => x.id === resultId ? item : x));
          
          toast({
            title: item.status === "completed" ? "Scan Processed" : "Scan Failed",
            description: item.status === "completed" 
              ? `Extracted details for ${item.product.name || 'product'}`
              : `Reason: ${item.failure_reason || 'Unknown error'}`,
            variant: item.status === "completed" ? "default" : "destructive"
          });
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
      
      if (attempts >= maxAttempts) {
        clearInterval(interval);
        toast({
          title: "Scan processing timeout",
          description: "The background task took too long. Check the dashboard alerts.",
          variant: "warning" as any
        });
      }
    }, 1500);
  }, [toast]);

  /* ── Handle Barcode Detection ── */
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
  const barcodeScanActive = !detectionPaused && (flowStep === "scanning" || flowStep === "barcode_ok") && camStatus === "active";
  const { scanState } = useBarcodeScanner({
    videoRef,
    active: barcodeScanActive,
    onDetected: handleBarcodeDetected,
    intervalMs: 200,
  });

  /* ── Start session ── */
  const handleStartScan = useCallback(async () => {
    setFlowStep("starting");
    setDetectionPaused(false);
    setAutoScanEnabled(true);
    setDetectedBarcode("");
    setProduct(null);
    barcodeHandled.current = false;
    try {
      const res = await scanFlowApi.startScan();
      setSession({ id: res.session_id });
      setFlowStep("scanning");
    } catch (err: any) {
      toast({ title: "Failed to start session", description: err.message, variant: "destructive" });
      setFlowStep("idle");
    }
  }, [toast]);

  // Start camera after scan component mounts in DOM
  useEffect(() => {
    if (flowStep === "scanning" && camStatus === "idle") {
      startCamera();
    }
  }, [flowStep, camStatus, startCamera]);

  /* ── Auto-Capture Loop (Quality-Gate Driven) ── */
  useEffect(() => {
    if (flowStep === "idle" || detectionPaused || !videoRef.current || !autoScanEnabled || camStatus !== "active") {
      return;
    }

    let intervalId: any;
    const analyzeFrame = async () => {
      // Throttle captures: must wait 3 seconds between auto-captures
      if (isAnalyzingFrame || Date.now() - lastScanTime.current < 3000) return;
      
      const video = videoRef.current;
      if (!video || video.readyState !== video.HAVE_ENOUGH_DATA) return;

      setIsAnalyzingFrame(true);
      try {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.drawImage(video, 0, 0);
          canvas.toBlob(async (blob) => {
            if (!blob) {
              setIsAnalyzingFrame(false);
              return;
            }
            try {
              // Run real-time frame quality check (blur, glare, hand-occlusion)
              const res = await scanFlowApi.validateFrame(blob);
              if (res.success && res.usable) {
                playScanBeep();
                lastScanTime.current = Date.now();
                
                // Show green camera flash feedback
                const flashOverlay = document.createElement("div");
                flashOverlay.className = "absolute inset-0 bg-emerald-500/20 pointer-events-none transition-opacity duration-300 z-50 opacity-100";
                video.parentElement?.appendChild(flashOverlay);
                setTimeout(() => {
                  flashOverlay.style.opacity = "0";
                  setTimeout(() => flashOverlay.remove(), 300);
                }, 100);

                const dataUrl = canvas.toDataURL("image/jpeg");
                
                // Trigger background queue enqueueing
                const enqueueRes = await scanFlowApi.enqueueScan(blob, session?.id || undefined, detectedBarcode || undefined);
                
                // Instantly inject pending item to UI sidebar
                const newItem: OCRHistoryItem = {
                  id: enqueueRes.ocr_result_id,
                  session_id: enqueueRes.session_id,
                  status: "pending",
                  failure_reason: null,
                  image_url: dataUrl,
                  created_at: new Date().toISOString(),
                  product: {
                    name: product?.name || "Detecting Product...",
                    brand: product?.brand || null,
                    barcode: detectedBarcode || null
                  },
                  extracted_data: {
                    manufacturing_date: null,
                    expiry_date: null,
                    batch_number: null,
                    mrp: null,
                    raw_text: null,
                    confidence: 0.0
                  },
                  ocr_blocks: null
                };

                setHistory(prev => [newItem, ...prev]);

                // Reset camera state immediately to allow scanning the next product
                setDetectedBarcode("");
                setProduct(null);
                barcodeHandled.current = false;
                setFlowStep("scanning");

                // Start polling background worker status
                pollScanStatus(enqueueRes.ocr_result_id);
              }
            } catch (err) {
              console.error("Frame analysis validation error:", err);
            } finally {
              setIsAnalyzingFrame(false);
            }
          }, "image/jpeg", 0.85);
        } else {
          setIsAnalyzingFrame(false);
        }
      } catch (err) {
        console.error("Frame capture error:", err);
        setIsAnalyzingFrame(false);
      }
    };

    intervalId = setInterval(analyzeFrame, 600);
    return () => clearInterval(intervalId);
  }, [flowStep, camStatus, session, detectedBarcode, product, autoScanEnabled, detectionPaused, isAnalyzingFrame, pollScanStatus]);

  /* ── Manual Click-to-Capture Fallback ── */
  const handleManualCapture = useCallback(async () => {
    if (!session) return;
    if (detectionPaused) {
      toast({ title: "Detection is stopped", description: "Resume detection before capturing another product.", variant: "warning" as any });
      return;
    }
    setFlowStep("capturing");
    
    // Create canvas capture
    const video = videoRef.current;
    if (!video) return;

    try {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.drawImage(video, 0, 0);

      canvas.toBlob(async (blob) => {
        if (!blob) {
          toast({ title: "Capture failed", description: "Could not grab frame buffer", variant: "destructive" });
          setFlowStep("barcode_ok");
          return;
        }

        playScanBeep();
        const dataUrl = canvas.toDataURL("image/jpeg");
        
        // Enqueue scan to queue
        const enqueueRes = await scanFlowApi.enqueueScan(blob, session.id, detectedBarcode || undefined);
        
        // Add pending card to queue list
        const newItem: OCRHistoryItem = {
          id: enqueueRes.ocr_result_id,
          session_id: enqueueRes.session_id,
          status: "pending",
          failure_reason: null,
          image_url: dataUrl,
          created_at: new Date().toISOString(),
          product: {
            name: product?.name || "Detecting Product...",
            brand: product?.brand || null,
            barcode: detectedBarcode || null
          },
          extracted_data: {
            manufacturing_date: null,
            expiry_date: null,
            batch_number: null,
            mrp: null,
            raw_text: null,
            confidence: 0.0
          },
          ocr_blocks: null
        };
        setHistory(prev => [newItem, ...prev]);

        // Reset camera state for next product
        setDetectedBarcode("");
        setProduct(null);
        barcodeHandled.current = false;
        setFlowStep("scanning");

        pollScanStatus(enqueueRes.ocr_result_id);
        toast({ title: "Enqueued", description: "Scan added to background queue successfully." });
      }, "image/jpeg", 0.90);

    } catch (err: any) {
      toast({ title: "Capture failed", description: err.message, variant: "destructive" });
      setFlowStep("barcode_ok");
    }
  }, [session, detectionPaused, detectedBarcode, product, toast, pollScanStatus]);

  const handleToggleDetection = useCallback(() => {
    setDetectionPaused((prev) => {
      const next = !prev;
      if (next) {
        setAutoScanEnabled(false);
        setIsAnalyzingFrame(false);
        toast({
          title: "Detection stopped",
          description: "Barcode reading and frame auto-capture are paused.",
        });
      } else {
        setAutoScanEnabled(true);
        barcodeHandled.current = false;
        toast({
          title: "Detection resumed",
          description: "Barcode reading and clear-frame capture are active again.",
        });
      }
      return next;
    });
  }, [toast]);

  /* ── Open Inspection Modal ── */
  const handleOpenInspect = (item: OCRHistoryItem) => {
    setActiveItem(item);
    setActiveItemData({
      product_name: item.product.name,
      brand: item.product.brand || undefined,
      manufacturing_date: item.extracted_data.manufacturing_date || undefined,
      expiry_date: item.extracted_data.expiry_date || undefined,
      batch_number: item.extracted_data.batch_number || undefined,
      mrp: item.extracted_data.mrp || undefined,
      raw_text: item.extracted_data.raw_text || undefined,
      confidence: item.extracted_data.confidence || undefined,
    });
    setIsModalOpen(true);
  };

  /* ── Modal: Finalize scan and write to inventory ── */
  const handleConfirmFinalize = async () => {
    if (!activeItem || !activeItem.session_id) return;
    setIsSubmittingActive(true);
    try {
      const barcode = activeItem.product.barcode || `UNKNOWN-${activeItem.id}`;
      // Call finalize API
      await scanFlowApi.finalize(
        activeItem.session_id,
        barcode,
        activeItem.image_url || "",
        activeItemData
      );

      // Update local item status in history list
      setHistory(prev =>
        prev.map(x =>
          x.id === activeItem.id
            ? {
                ...x,
                product: { ...x.product, name: activeItemData.product_name || x.product.name, brand: activeItemData.brand || x.product.brand },
                extracted_data: {
                  ...x.extracted_data,
                  manufacturing_date: activeItemData.manufacturing_date || null,
                  expiry_date: activeItemData.expiry_date || null,
                  batch_number: activeItemData.batch_number || null,
                  mrp: activeItemData.mrp || null,
                },
              }
            : x
        )
      );

      toast({ title: "Saved!", description: "Inventory item created successfully." });
      setIsModalOpen(false);
      setActiveItem(null);
    } catch (err: any) {
      toast({ title: "Failed to finalize", description: err.message, variant: "destructive" });
    } finally {
      setIsSubmittingActive(false);
    }
  };

  /* ── Cancel / Reset Session ── */
  const handleCancel = useCallback(async () => {
    if (session) {
      try { await scanFlowApi.cancel(session.id); } catch { /* swallow */ }
    }
    stopStream();
    setSession(null);
    setFlowStep("idle");
    setDetectedBarcode("");
    setProduct(null);
    setDetectionPaused(false);
    setAutoScanEnabled(true);
    barcodeHandled.current = false;
  }, [session, stopStream]);

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
              Initialize a secure scan session. The camera will automatically auto-capture clear frames.
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
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleToggleDetection}
            className={`border-slate-800 rounded-lg gap-2 text-xs transition-colors duration-200 ${detectionPaused ? 'bg-red-950/30 text-red-300 border-red-900/60 hover:bg-red-950/50' : 'bg-blue-950/30 text-blue-300 border-blue-900/60 hover:bg-blue-950/50'}`}
          >
            {detectionPaused ? (
              <>
                <Play className="size-3.5 fill-red-300" />
                Resume Detection
              </>
            ) : (
              <>
                <Pause className="size-3.5 fill-blue-300" />
                Stop Detection
              </>
            )}
          </Button>

          {/* Auto Scan Toggle */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoScanEnabled(!autoScanEnabled)}
            disabled={detectionPaused}
            className={`border-slate-800 rounded-lg gap-2 text-xs transition-colors duration-200 ${autoScanEnabled ? 'bg-emerald-950/40 text-emerald-400 border-emerald-900/60 hover:bg-emerald-950/60' : 'bg-slate-900 text-slate-400 hover:bg-slate-800'}`}
          >
            {autoScanEnabled ? (
              <>
                <Play className="size-3.5 fill-emerald-400" />
                Auto-Scan Active
              </>
            ) : (
              <>
                <Pause className="size-3.5 fill-slate-400" />
                Manual Capture Mode
              </>
            )}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleCancel}
            className="text-slate-400 hover:text-red-400 hover:bg-red-400/10 gap-1.5 text-xs"
          >
            <XCircle className="size-4" /> Cancel Session
          </Button>
        </div>
      </div>

      {/* ── Main Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1">
        
        {/* LEFT — Camera Panel (Col-span 7) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden flex flex-col h-full min-h-[450px]">
            <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-200">Live Camera Stream</span>
              {camStatus === "active" && (
                <span className="text-xs text-emerald-400 flex items-center gap-1.5">
                  <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Live Feed
                </span>
              )}
            </div>

            {/* Camera Viewport */}
            <div className="p-4 flex-1 flex flex-col justify-center relative">
              <CameraView
                videoRef={videoRef}
                status={camStatus}
                error={camError}
                devices={devices}
                selectedDeviceId={selectedDeviceId}
                onStart={() => startCamera()}
                onSwitch={switchCamera}
                imagePreview={null}
              >
                {!detectionPaused ? (
                  <BarcodeScannerOverlay
                    scanState={scanState}
                    detectedCode={detectedBarcode}
                  />
                ) : (
                  <div className="absolute inset-0 bg-slate-950/55 backdrop-blur-[1px] flex items-center justify-center text-center">
                    <div className="rounded-lg border border-red-900/60 bg-red-950/40 px-4 py-3 text-sm text-red-200 shadow-lg">
                      Detection stopped
                      <span className="block text-xs text-red-300/80 mt-1">Resume detection to read barcodes and capture products.</span>
                    </div>
                  </div>
                )}
              </CameraView>
            </div>

            {/* Quality and Manual Override controls */}
            <div className="p-4 bg-slate-900/40 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Info className="size-4 text-blue-500 shrink-0" />
                <span>
                  {detectionPaused
                    ? "Detection is stopped. Camera stays open, but barcode reading and captures are paused."
                    : autoScanEnabled 
                    ? "Keep camera steady. Images are auto-snapped once clear and sent to the queue." 
                    : "Align product label details and click the button to capture."}
                </span>
              </div>
              
              {!autoScanEnabled && !detectionPaused && (
                <Button
                  onClick={handleManualCapture}
                  className="bg-blue-600 hover:bg-blue-500 text-white rounded-lg px-6 py-2 text-sm gap-2"
                >
                  <Camera className="size-4" /> Capture Product
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT — Scan Queue Sidebar (Col-span 5) */}
        <div className="lg:col-span-5 bg-slate-900/60 border border-slate-800 rounded-xl flex flex-col overflow-hidden max-h-[calc(100vh-170px)]">
          <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History className="size-4 text-slate-400" />
              <span className="text-sm font-semibold text-slate-200">Scan Queue & History</span>
            </div>
            {history.length > 0 && (
              <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full">
                {history.length} items
              </span>
            )}
          </div>

          {/* Queue Scroll Feed */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            <AnimatePresence initial={false}>
              {history.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 text-center gap-2 text-slate-600">
                  <div className="size-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-700 text-xl">⏳</div>
                  <p className="text-sm font-medium">Scan queue is empty</p>
                  <p className="text-xs text-slate-500 max-w-[200px] mt-0.5">Scanned products will stack here in real time.</p>
                </div>
              ) : (
                history.map((item) => {
                  const isPending = item.status === "pending" || item.status === "processing";
                  const isCompleted = item.status === "completed";
                  const isFailed = item.status === "failed";
                  
                  // Compute expiry styling
                  const expDate = item.extracted_data.expiry_date;
                  const isExpired = expDate ? new Date(expDate) < new Date() : false;

                  return (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      className={`p-3 bg-slate-950/80 border rounded-xl flex gap-3 transition-colors duration-200 hover:border-blue-700/60 cursor-pointer border-slate-800/80 hover:bg-slate-950`}
                      onClick={() => handleOpenInspect(item)}
                    >
                      {/* Left side thumbnail */}
                      <div className="relative size-16 shrink-0 rounded-lg overflow-hidden border border-slate-800 bg-slate-900">
                        {item.image_url ? (
                          <img src={getFullImageUrl(item.image_url)} alt="product" className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-slate-700">🖼️</div>
                        )}
                        {isPending && (
                          <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                            <Loader2 className="size-4 animate-spin text-blue-400" />
                          </div>
                        )}
                      </div>

                      {/* Right side data */}
                      <div className="flex-1 min-w-0 flex flex-col justify-between">
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="text-sm font-semibold text-slate-200 truncate pr-1">
                            {item.product.name}
                          </h3>
                          {/* Badges */}
                          {isPending && (
                            <span className="text-[10px] shrink-0 font-medium px-2 py-0.5 rounded-full bg-blue-900/30 text-blue-400 border border-blue-900/60 flex items-center gap-1">
                              <Loader2 className="size-2.5 animate-spin" />
                              {item.status === "pending" ? "Queued" : "OCR Running"}
                            </span>
                          )}
                          {isCompleted && (
                            <span className={`text-[10px] shrink-0 font-medium px-2 py-0.5 rounded-full border ${isExpired ? 'bg-red-950/30 text-red-400 border-red-900/50' : 'bg-emerald-950/30 text-emerald-400 border-emerald-900/50'}`}>
                              {isExpired ? "Expired" : "Processed"}
                            </span>
                          )}
                          {isFailed && (
                            <span className="text-[10px] shrink-0 font-medium px-2 py-0.5 rounded-full bg-red-950/30 text-red-400 border border-red-900/60 flex items-center gap-1">
                              <AlertTriangle className="size-2.5" />
                              Failed
                            </span>
                          )}
                        </div>

                        {/* Middle: barcode / brand */}
                        <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono mt-0.5">
                          {item.product.brand && <span className="truncate">{item.product.brand}</span>}
                          {item.product.brand && item.product.barcode && <span>•</span>}
                          {item.product.barcode && <span>{item.product.barcode}</span>}
                        </div>

                        {/* Bottom: Date Summary */}
                        {isCompleted && (
                          <div className="flex gap-3 text-[11px] mt-1.5 pt-1 border-t border-slate-900 text-slate-400">
                            {item.extracted_data.manufacturing_date && (
                              <div>
                                <span className="text-slate-600 block text-[9px] uppercase tracking-wider">MFG</span>
                                <span className="font-mono">{item.extracted_data.manufacturing_date}</span>
                              </div>
                            )}
                            {item.extracted_data.expiry_date && (
                              <div>
                                <span className="text-slate-600 block text-[9px] uppercase tracking-wider">EXP</span>
                                <span className={`font-mono font-medium ${isExpired ? 'text-red-400' : 'text-slate-200'}`}>
                                  {item.extracted_data.expiry_date}
                                </span>
                              </div>
                            )}
                            {item.extracted_data.batch_number && (
                              <div>
                                <span className="text-slate-600 block text-[9px] uppercase tracking-wider">Batch</span>
                                <span className="truncate max-w-[60px] block font-mono">{item.extracted_data.batch_number}</span>
                              </div>
                            )}
                          </div>
                        )}
                        {isFailed && (
                          <p className="text-[11px] text-red-400 mt-1 truncate">
                            {item.failure_reason || "OCR validation error."}
                          </p>
                        )}
                      </div>
                    </motion.div>
                  );
                })
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* ── Inspection / final validation Dialog Modal ── */}
      <Dialog open={isModalOpen} onOpenChange={(open) => !open && setIsModalOpen(false)}>
        <DialogContent className="bg-slate-900 border-slate-800 text-slate-200 max-w-3xl w-[92vw] overflow-y-auto max-h-[92vh]">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold text-slate-100">Review OCR Extraction</DialogTitle>
            <DialogDescription className="text-xs text-slate-400">
              View the captured product image, inspect OCR logs, and confirm completed scans before saving.
            </DialogDescription>
          </DialogHeader>

          {activeItem && (
            <Tabs defaultValue={activeItem.status === "completed" ? "details" : "image"} className="w-full mt-3">
              <TabsList className="bg-slate-950 border border-slate-800 p-0.5 rounded-lg mb-4 w-full flex justify-start">
                <TabsTrigger value="image" className="text-xs data-[state=active]:bg-blue-600 data-[state=active]:text-white">
                  Product Image
                </TabsTrigger>
                {activeItem.status === "completed" && (
                  <TabsTrigger value="details" className="text-xs data-[state=active]:bg-blue-600 data-[state=active]:text-white">
                    Extraction Details
                  </TabsTrigger>
                )}
                <TabsTrigger value="logs" className="text-xs data-[state=active]:bg-blue-600 data-[state=active]:text-white">
                  Pipeline Execution Logs
                </TabsTrigger>
              </TabsList>

              <TabsContent value="image" className="mt-0 focus-visible:ring-0">
                <div className="flex flex-col gap-3">
                  <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
                    {activeItem.image_url ? (
                      <img
                        src={getFullImageUrl(activeItem.image_url)}
                        alt={`${activeItem.product.name || "Scanned product"} capture`}
                        className="max-h-[62vh] w-full object-contain bg-black"
                      />
                    ) : (
                      <div className="flex min-h-[280px] items-center justify-center text-sm text-slate-500">
                        No product image is available for this queue item.
                      </div>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
                    <span className="truncate">
                      {activeItem.product.name || "Detecting product"}
                      {activeItem.product.barcode ? ` | ${activeItem.product.barcode}` : ""}
                    </span>
                    <span className={`font-semibold uppercase tracking-wider ${
                      activeItem.status === 'completed' ? 'text-emerald-400' :
                      activeItem.status === 'failed' ? 'text-red-400' : 'text-blue-400'
                    }`}>
                      {activeItem.status}
                    </span>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="details" className="mt-0 focus-visible:ring-0">
                <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                  {/* Highlight Image Panel (Col-span 7) */}
                  <div className="md:col-span-7 flex flex-col gap-2">
                    <span className="text-xs font-semibold text-slate-400">Text Bounding Boxes</span>
                    <OCRImageHighlight
                      imageUrl={getFullImageUrl(activeItem.image_url)}
                      ocrBlocks={activeItem.ocr_blocks}
                    />
                  </div>

                  {/* Form Input Panel (Col-span 5) */}
                  <div className="md:col-span-5 flex flex-col gap-3 justify-between">
                    <div>
                      <span className="text-xs font-semibold text-slate-400 block mb-2">Extracted Fields</span>
                      
                      <div className="space-y-3.5">
                        <div className="space-y-1">
                          <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Product Name</Label>
                          <Input
                            value={activeItemData.product_name || ""}
                            onChange={(e) => setActiveItemData({ ...activeItemData, product_name: e.target.value })}
                            className="bg-slate-950 border-slate-800 text-sm focus-visible:ring-blue-700"
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Brand</Label>
                          <Input
                            value={activeItemData.brand || ""}
                            onChange={(e) => setActiveItemData({ ...activeItemData, brand: e.target.value })}
                            className="bg-slate-950 border-slate-800 text-sm focus-visible:ring-blue-700"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">MFG Date</Label>
                            <Input
                              value={activeItemData.manufacturing_date || ""}
                              onChange={(e) => setActiveItemData({ ...activeItemData, manufacturing_date: e.target.value })}
                              className="bg-slate-950 border-slate-800 text-sm font-mono focus-visible:ring-blue-700"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">EXP Date</Label>
                            <Input
                              value={activeItemData.expiry_date || ""}
                              onChange={(e) => setActiveItemData({ ...activeItemData, expiry_date: e.target.value })}
                              className="bg-slate-950 border-slate-800 text-sm font-mono focus-visible:ring-blue-700"
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">Batch</Label>
                            <Input
                              value={activeItemData.batch_number || ""}
                              onChange={(e) => setActiveItemData({ ...activeItemData, batch_number: e.target.value })}
                              className="bg-slate-950 border-slate-800 text-sm font-mono focus-visible:ring-blue-700"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-[10px] text-slate-500 uppercase tracking-wider">MRP</Label>
                            <Input
                              type="number"
                              value={activeItemData.mrp || ""}
                              onChange={(e) => setActiveItemData({ ...activeItemData, mrp: parseFloat(e.target.value) || undefined })}
                              className="bg-slate-950 border-slate-800 text-sm focus-visible:ring-blue-700"
                            />
                          </div>
                        </div>

                        {/* 🤖 AI Shelf Life Analysis */}
                        <div className="mt-4 p-3 bg-slate-900 border border-slate-800 rounded-lg">
                          <span className="text-xs font-semibold text-slate-300 flex items-center gap-2 mb-3">
                            <span>🤖</span> AI Shelf Life Analysis
                          </span>
                          
                          {activeItem.extracted_data?.ml_decision ? (
                            <div className="space-y-2">
                              <div className="flex justify-between items-center text-sm">
                                <span className="text-slate-400">Decision:</span>
                                <span className={`font-bold ${
                                  activeItem.extracted_data.ml_decision === 'ACCEPTED' ? 'text-emerald-400' :
                                  activeItem.extracted_data.ml_decision === 'PRIORITY_SALE' ? 'text-orange-400' : 'text-red-400'
                                }`}>
                                  {activeItem.extracted_data.ml_decision}
                                </span>
                              </div>
                              <div className="flex justify-between items-center text-xs">
                                <span className="text-slate-500">Confidence:</span>
                                <span className="text-slate-300">
                                  {((activeItem.extracted_data.ml_confidence ?? 0) * 100).toFixed(1)}%
                                </span>
                              </div>
                              <div className="flex justify-between items-center text-xs">
                                <span className="text-slate-500">Adjusted Remaining:</span>
                                <span className="text-slate-300">
                                  {activeItem.extracted_data.adjusted_remaining?.toFixed(1)} days
                                </span>
                              </div>
                              <div className="flex justify-between items-center text-xs">
                                <span className="text-slate-500">Physics Remaining:</span>
                                <span className="text-slate-300">
                                  {activeItem.extracted_data.arrhenius_remaining?.toFixed(1)} days
                                </span>
                              </div>
                              <div className={`mt-2 p-2 rounded text-xs text-center font-semibold ${
                                activeItem.extracted_data.ml_decision === 'ACCEPTED' ? 'bg-emerald-900 text-emerald-300' :
                                activeItem.extracted_data.ml_decision === 'PRIORITY_SALE' ? 'bg-orange-900 text-orange-300' :
                                'bg-red-900 text-red-300'
                              }`}>
                                {activeItem.extracted_data.ml_decision === 'ACCEPTED' && '✅ Safe to stock normally'}
                                {activeItem.extracted_data.ml_decision === 'PRIORITY_SALE' && '⚡ Discount and sell immediately'}
                                {activeItem.extracted_data.ml_decision === 'REJECTED' && '🚫 Do not stock. Quarantine now.'}
                              </div>
                            </div>
                          ) : (
                            <div className="text-xs text-slate-500 text-center py-2">
                              ⏳ ML analysis pending. Make sure integration.py is running.
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="pt-4 flex gap-2">
                      <Button
                        variant="outline"
                        onClick={() => setIsModalOpen(false)}
                        className="flex-1 border-slate-800 bg-slate-950 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                      >
                        Discard
                      </Button>
                      <Button
                        onClick={handleConfirmFinalize}
                        disabled={isSubmittingActive}
                        className="flex-1 bg-blue-600 hover:bg-blue-500 text-white gap-2"
                      >
                        {isSubmittingActive ? (
                          <>
                            <Loader2 className="size-4 animate-spin" /> Saving...
                          </>
                        ) : (
                          <>
                            <CheckCircle2 className="size-4" /> Save Item
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="logs" className="mt-0 focus-visible:ring-0">
                <div className="flex flex-col gap-3">
                  <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                    <span>Task Status: 
                      <span className={`ml-1.5 font-bold uppercase tracking-wider ${
                        activeItem.status === 'completed' ? 'text-emerald-400' :
                        activeItem.status === 'failed' ? 'text-red-400' : 'text-blue-400'
                      }`}>
                        {activeItem.status}
                      </span>
                    </span>
                    {activeItem.status === 'processing' && (
                      <span className="flex items-center gap-1.5 text-[11px] text-blue-400">
                        <Loader2 className="size-3.5 animate-spin" />
                        Running async pipeline...
                      </span>
                    )}
                  </div>
                  
                  {/* Terminal Log Console */}
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-[11px] text-slate-300 leading-relaxed shadow-inner max-h-[380px] overflow-y-auto min-h-[240px]">
                    {getPipelineLogs(activeItem).map((logLine, idx) => {
                      const isError = logLine.includes("ERROR") || logLine.includes("FAILED");
                      const isSuccess = logLine.includes("COMPLETE");
                      return (
                        <div key={idx} className={`mb-1.5 ${isError ? 'text-red-400' : isSuccess ? 'text-emerald-400' : 'text-slate-300'}`}>
                          {logLine}
                        </div>
                      );
                    })}
                    {activeItem.status === 'processing' && (
                      <div className="text-blue-400 flex items-center gap-1.5 animate-pulse mt-2 pl-1">
                        <span className="size-1.5 rounded-full bg-blue-500 animate-ping" />
                        <span>[Pipeline] Extracting fields and parsing dates...</span>
                      </div>
                    )}
                    {activeItem.status === 'pending' && (
                      <div className="text-slate-500 flex items-center gap-1.5 animate-pulse mt-2 pl-1">
                        <span className="size-1.5 rounded-full bg-slate-600 animate-pulse" />
                        <span>[Queue] Waiting for queue worker thread...</span>
                      </div>
                    )}
                  </div>

                  <div className="flex justify-end gap-2 pt-2">
                    <Button
                      variant="outline"
                      onClick={() => setIsModalOpen(false)}
                      className="border-slate-800 bg-slate-950 text-slate-400 hover:bg-slate-800 hover:text-slate-200 text-xs px-4"
                    >
                      Close Logs
                    </Button>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>

      {/* Progress timeline */}
      <ScanProgress
        currentStep={flowToScanStep(flowStep)}
        isProcessing={flowStep === "capturing" || history.some(h => h.status === "pending" || h.status === "processing")}
      />
    </div>
  );
}
