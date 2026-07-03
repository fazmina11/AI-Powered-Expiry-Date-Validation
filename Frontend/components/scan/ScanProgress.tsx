"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

export type ScanStep =
  | "idle"
  | "camera_ready"
  | "barcode_detected"
  | "product_found"
  | "image_captured"
  | "ocr_completed"
  | "saved";

const STEPS: { id: ScanStep; label: string }[] = [
  { id: "camera_ready", label: "Camera Ready" },
  { id: "barcode_detected", label: "Barcode Detected" },
  { id: "product_found", label: "Product Found" },
  { id: "image_captured", label: "Image Captured" },
  { id: "ocr_completed", label: "OCR Completed" },
  { id: "saved", label: "Saved" },
];

const ORDER: ScanStep[] = ["idle", "camera_ready", "barcode_detected", "product_found", "image_captured", "ocr_completed", "saved"];

function getStepIndex(step: ScanStep) {
  return ORDER.indexOf(step);
}

interface ScanProgressProps {
  currentStep: ScanStep;
  isProcessing?: boolean;
}

export function ScanProgress({ currentStep, isProcessing }: ScanProgressProps) {
  const currentIndex = getStepIndex(currentStep);

  return (
    <div className="w-full bg-slate-900/50 backdrop-blur-md rounded-xl p-4 border border-slate-700/50">
      <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-3 px-1">Scan Progress</p>
      <div className="flex items-center justify-between gap-1">
        {STEPS.map((step, idx) => {
          const stepActualIndex = idx + 1; // steps start at index 1 in ORDER
          const isCompleted = stepActualIndex < currentIndex;
          const isCurrent = stepActualIndex === currentIndex;
          const isActive = isCompleted || isCurrent;

          return (
            <div key={step.id} className="flex flex-col items-center flex-1 gap-1.5">
              {/* Connector line before */}
              <div className="flex items-center w-full">
                {idx > 0 && (
                  <div className={`flex-1 h-px transition-colors duration-500 ${isActive ? "bg-blue-500" : "bg-slate-700"}`} />
                )}
                <motion.div
                  initial={{ scale: 0.8 }}
                  animate={{ scale: 1 }}
                  className={`relative flex items-center justify-center size-7 rounded-full shrink-0 transition-colors duration-500 ${
                    isCompleted
                      ? "bg-blue-600 text-white"
                      : isCurrent
                      ? "bg-blue-500/20 border-2 border-blue-500 text-blue-400"
                      : "bg-slate-800 border border-slate-700 text-slate-600"
                  }`}
                >
                  {isCurrent && isProcessing ? (
                    <Loader2 className="size-3.5 animate-spin" />
                  ) : isCompleted ? (
                    <CheckCircle2 className="size-3.5" />
                  ) : (
                    <Circle className="size-3.5" />
                  )}
                </motion.div>
                {idx < STEPS.length - 1 && (
                  <div className={`flex-1 h-px transition-colors duration-500 ${isCompleted ? "bg-blue-500" : "bg-slate-700"}`} />
                )}
              </div>
              <span
                className={`text-center leading-tight transition-colors duration-300 ${
                  isActive ? "text-blue-400" : "text-slate-600"
                } text-[10px] font-medium`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
