import { useState, useEffect, useRef, useCallback, RefObject } from "react";
import { BrowserMultiFormatReader, NotFoundException } from "@zxing/library";

export type BarcodeScanState = "scanning" | "found" | "stopped";

interface UseBarcodeOptions {
  videoRef: RefObject<HTMLVideoElement>;
  active: boolean;
  onDetected: (barcode: string) => void;
  intervalMs?: number;
}

export function useBarcodeScanner({ videoRef, active, onDetected, intervalMs = 250 }: UseBarcodeOptions) {
  const [scanState, setScanState] = useState<BarcodeScanState>("stopped");
  const readerRef = useRef<BrowserMultiFormatReader | null>(null);
  const rafRef = useRef<number | null>(null);
  const detectedRef = useRef(false);
  const mountedRef = useRef(true);

  const stopScanning = useCallback(() => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    setScanState("stopped");
  }, []);

  const resetScanner = useCallback(() => {
    detectedRef.current = false;
    setScanState(active ? "scanning" : "stopped");
  }, [active]);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      stopScanning();
    };
  }, [stopScanning]);

  useEffect(() => {
    if (!active) {
      stopScanning();
      return;
    }

    readerRef.current = new BrowserMultiFormatReader();
    detectedRef.current = false;
    setScanState("scanning");

    let lastScanTime = 0;

    const scan = async (timestamp: number) => {
      if (!mountedRef.current || detectedRef.current) return;

      const elapsed = timestamp - lastScanTime;
      if (elapsed >= intervalMs) {
        lastScanTime = timestamp;
        const video = videoRef.current;

        if (video && video.readyState >= video.HAVE_ENOUGH_DATA && video.videoWidth > 0) {
          try {
            const canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext("2d");
            if (ctx) {
              ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
              // Decode the single frame captured in the canvas.
              // This is a one-shot execution and does not spawn background loops in ZXing.
              const result = readerRef.current!.decode(canvas as any);
              if (result && result.getText() && !detectedRef.current) {
                detectedRef.current = true;
                setScanState("found");
                onDetected(result.getText());
                return; // Stop loop after detection
              }
            }
          } catch (err) {
            // NotFoundException is expected when no barcode in frame — ignore it silently
          }
        }
      }

      if (mountedRef.current && !detectedRef.current) {
        rafRef.current = requestAnimationFrame(scan);
      }
    };

    rafRef.current = requestAnimationFrame(scan);

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    };
  }, [active, videoRef, onDetected, intervalMs, stopScanning]);

  return { scanState, stopScanning, resetScanner };
}
