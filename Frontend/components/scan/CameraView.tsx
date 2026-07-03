"use client";

import { useEffect, forwardRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CameraOff, RefreshCw, Settings, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CameraStatus, CameraDevice } from "@/hooks/useCamera";

interface CameraViewProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  status: CameraStatus;
  error: string | null;
  devices: CameraDevice[];
  selectedDeviceId?: string;
  onStart: () => void;
  onSwitch: (deviceId: string) => void;
  /** When a still image preview should replace the live feed */
  imagePreview?: string | null;
  /** Overlay content (barcode scanner UI) */
  children?: React.ReactNode;
}

export function CameraView({
  videoRef,
  status,
  error,
  devices,
  selectedDeviceId,
  onStart,
  onSwitch,
  imagePreview,
  children,
}: CameraViewProps) {
  return (
    <div className="relative w-full aspect-video bg-black rounded-xl overflow-hidden">
      {/* Live video */}
      <video
        ref={videoRef}
        playsInline
        muted
        className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-500 ${
          status === "active" && !imagePreview ? "opacity-100" : "opacity-0"
        }`}
      />

      {/* Image preview overlay */}
      <AnimatePresence>
        {imagePreview && (
          <motion.img
            key="preview"
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            src={imagePreview}
            alt="Captured label"
            className="absolute inset-0 w-full h-full object-contain bg-black"
          />
        )}
      </AnimatePresence>

      {/* Loading state */}
      <AnimatePresence>
        {status === "requesting" && !imagePreview && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 gap-3"
          >
            <Loader2 className="size-10 text-blue-500 animate-spin" />
            <p className="text-slate-400 text-sm">Requesting camera access...</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Permission denied */}
      <AnimatePresence>
        {(status === "denied" || status === "unavailable" || status === "error") && !imagePreview && (
          <motion.div
            key="error"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 gap-4 p-6 text-center"
          >
            <CameraOff className="size-12 text-red-500" />
            <div>
              <p className="text-white font-semibold text-sm">
                {status === "denied" ? "Camera Permission Required" : "Camera Unavailable"}
              </p>
              <p className="text-slate-400 text-xs mt-1 max-w-[220px]">{error}</p>
            </div>
            {status === "denied" && (
              <p className="text-slate-500 text-xs">
                Open browser settings → Site permissions → Camera → Allow
              </p>
            )}
            <Button size="sm" onClick={onStart} className="bg-blue-600 hover:bg-blue-500 text-white gap-2">
              <RefreshCw className="size-3" /> Retry
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Idle state */}
      <AnimatePresence>
        {status === "idle" && !imagePreview && (
          <motion.div
            key="idle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 gap-4"
          >
            <div className="size-16 rounded-full bg-slate-800 flex items-center justify-center">
              <div className="size-8 border-2 border-slate-600 rounded-full" />
            </div>
            <p className="text-slate-500 text-sm">Camera not started</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Camera scanner overlay children */}
      {status === "active" && !imagePreview && children}

      {/* Camera switcher */}
      {status === "active" && devices.length > 1 && !imagePreview && (
        <div className="absolute top-2 right-2">
          <select
            value={selectedDeviceId}
            onChange={(e) => onSwitch(e.target.value)}
            className="text-xs bg-black/60 text-white border border-white/20 rounded-md px-2 py-1 cursor-pointer"
          >
            {devices.map((d) => (
              <option key={d.deviceId} value={d.deviceId}>
                {d.label}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
