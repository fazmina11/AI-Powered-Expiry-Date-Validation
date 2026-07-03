"use client";

import { motion, AnimatePresence } from "framer-motion";
import { BarcodeScanState } from "@/hooks/useBarcodeScanner";

interface BarcodeScannerOverlayProps {
  scanState: BarcodeScanState;
  detectedCode?: string;
}

export function BarcodeScannerOverlay({ scanState, detectedCode }: BarcodeScannerOverlayProps) {
  const isFound = scanState === "found";

  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Full viewport border glow when product is locked */}
      <AnimatePresence>
        {isFound ? (
          <motion.div
            key="viewport-lock"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 border-4 border-emerald-500/80 shadow-[inset_0_0_24px_rgba(16,185,129,0.35)] transition-all duration-300"
          >
            <div className="absolute top-4 left-4 w-8 h-8 border-t-4 border-l-4 border-emerald-400" />
            <div className="absolute top-4 right-4 w-8 h-8 border-t-4 border-r-4 border-emerald-400" />
            <div className="absolute bottom-4 left-4 w-8 h-8 border-b-4 border-l-4 border-emerald-400" />
            <div className="absolute bottom-4 right-4 w-8 h-8 border-b-4 border-r-4 border-emerald-400" />
          </motion.div>
        ) : (
          /* Product guide frame with animated scan line */
          <motion.div
            key="product-guide"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-6 sm:inset-10 rounded-2xl overflow-hidden"
          >
            {/* Dashed guide border */}
            <div className="absolute inset-0 border-2 border-dashed border-blue-500/20 rounded-2xl" />

            {/* Corner brackets */}
            <span className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-blue-500 rounded-tl-xl" />
            <span className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-blue-500 rounded-tr-xl" />
            <span className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-blue-500 rounded-bl-xl" />
            <span className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-blue-500 rounded-br-xl" />

            {/* Animated scan line sweeping top → bottom */}
            <motion.div
              className="absolute left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-blue-400 to-transparent shadow-[0_0_8px_2px_rgba(96,165,250,0.6)]"
              initial={{ top: "0%" }}
              animate={{ top: ["0%", "100%", "0%"] }}
              transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Dynamic status label at bottom */}
      <div className="absolute bottom-4 left-0 right-0 flex justify-center">
        <AnimatePresence mode="wait">
          {scanState === "scanning" && (
            <motion.span
              key="scanning-state"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              className="bg-black/75 text-blue-300 text-[11px] font-semibold tracking-wide uppercase px-4 py-1.5 rounded-full border border-blue-900/30 backdrop-blur flex items-center gap-2"
            >
              <span className="size-1.5 rounded-full bg-blue-400 animate-ping" />
              Align product — hold steady
            </motion.span>
          )}
          {isFound && (
            <motion.span
              key="found-state"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              className="bg-emerald-950/90 text-emerald-300 text-[11px] font-semibold tracking-wide uppercase px-4 py-1.5 rounded-full border border-emerald-900/60 backdrop-blur flex items-center gap-2"
            >
              <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Product Locked — Capturing...
            </motion.span>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
