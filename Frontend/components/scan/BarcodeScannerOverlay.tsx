"use client";

import { motion, AnimatePresence } from "framer-motion";
import { BarcodeScanState } from "@/hooks/useBarcodeScanner";

interface BarcodeScannerOverlayProps {
  scanState: BarcodeScanState;
  detectedCode?: string;
}

export function BarcodeScannerOverlay({ scanState, detectedCode }: BarcodeScannerOverlayProps) {
  return (
    <div className="absolute inset-0 pointer-events-none flex flex-col items-center justify-center">
      {/* Scanning viewfinder */}
      <AnimatePresence>
        {scanState === "scanning" && (
          <motion.div
            key="viewfinder"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="relative w-3/4 max-w-xs h-28 border-2 border-blue-400/60 rounded-xl"
          >
            {/* Corner decorations */}
            <span className="absolute -top-0.5 -left-0.5 w-5 h-5 border-t-2 border-l-2 border-blue-400 rounded-tl-lg" />
            <span className="absolute -top-0.5 -right-0.5 w-5 h-5 border-t-2 border-r-2 border-blue-400 rounded-tr-lg" />
            <span className="absolute -bottom-0.5 -left-0.5 w-5 h-5 border-b-2 border-l-2 border-blue-400 rounded-bl-lg" />
            <span className="absolute -bottom-0.5 -right-0.5 w-5 h-5 border-b-2 border-r-2 border-blue-400 rounded-br-lg" />

            {/* Scan line */}
            <motion.div
              className="absolute left-2 right-2 h-0.5 bg-blue-400/80 shadow-[0_0_8px_2px_rgba(59,130,246,0.7)]"
              animate={{ top: ["10%", "85%", "10%"] }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Detection pulse */}
      <AnimatePresence>
        {scanState === "found" && (
          <motion.div
            key="found"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center gap-2"
          >
            <motion.div
              className="size-16 rounded-full bg-emerald-500/20 border-2 border-emerald-400 flex items-center justify-center"
              animate={{ scale: [1, 1.15, 1] }}
              transition={{ duration: 0.4 }}
            >
              <span className="text-emerald-400 text-2xl">✓</span>
            </motion.div>
            {detectedCode && (
              <span className="bg-black/70 text-white text-xs font-mono px-3 py-1 rounded-full">
                {detectedCode}
              </span>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status label */}
      <div className="absolute bottom-3 left-0 right-0 flex justify-center">
        <AnimatePresence mode="wait">
          {scanState === "scanning" && (
            <motion.span
              key="s"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              className="bg-black/60 text-blue-300 text-xs font-medium px-3 py-1 rounded-full backdrop-blur-sm"
            >
              Detecting barcode...
            </motion.span>
          )}
          {scanState === "found" && (
            <motion.span
              key="f"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              className="bg-emerald-900/80 text-emerald-300 text-xs font-medium px-3 py-1 rounded-full"
            >
              Barcode detected!
            </motion.span>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
