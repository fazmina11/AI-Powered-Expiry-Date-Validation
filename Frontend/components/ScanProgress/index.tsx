import { CheckCircle2, Circle } from "lucide-react";
import { motion } from "framer-motion";

export type ScanStep = "STARTED" | "BARCODE_DETECTED" | "IMAGE_CAPTURED" | "OCR_COMPLETED" | "DB_STORED";

const STEPS = [
  { id: "STARTED", label: "Start" },
  { id: "BARCODE_DETECTED", label: "Barcode" },
  { id: "IMAGE_CAPTURED", label: "Image" },
  { id: "OCR_COMPLETED", label: "OCR" },
  { id: "DB_STORED", label: "Saved" },
];

export function ScanProgress({ currentStep }: { currentStep: ScanStep }) {
  const currentIndex = STEPS.findIndex((s) => s.id === currentStep);

  return (
    <div className="w-full bg-slate-900/50 backdrop-blur-md rounded-xl p-4 border border-slate-700/50">
      <div className="flex items-center justify-between">
        {STEPS.map((step, idx) => {
          const isCompleted = idx <= currentIndex;
          return (
            <div key={step.id} className="flex flex-col items-center flex-1">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className={`relative z-10 flex items-center justify-center size-8 rounded-full mb-2 ${
                  isCompleted ? "bg-blue-500 text-white" : "bg-slate-800 text-slate-500"
                }`}
              >
                {isCompleted ? <CheckCircle2 className="size-5" /> : <Circle className="size-5" />}
              </motion.div>
              <span className={`text-xs font-medium ${isCompleted ? "text-blue-400" : "text-slate-500"}`}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
