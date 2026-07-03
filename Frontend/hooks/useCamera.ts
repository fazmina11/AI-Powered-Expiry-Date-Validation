import { useState, useEffect, useRef, useCallback } from "react";

export type CameraStatus =
  | "idle"
  | "requesting"
  | "active"
  | "denied"
  | "unavailable"
  | "error";

export interface CameraDevice {
  deviceId: string;
  label: string;
}

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [status, setStatus] = useState<CameraStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [devices, setDevices] = useState<CameraDevice[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | undefined>(undefined);

  const stopStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  const startCamera = useCallback(async (deviceId?: string) => {
    // Stop any existing stream first
    stopStream();
    setStatus("requesting");
    setError(null);

    // Check browser support
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus("unavailable");
      setError("Your browser does not support camera access.");
      return;
    }

    const constraints: MediaStreamConstraints = {
      video: deviceId
        ? { deviceId: { exact: deviceId }, width: { ideal: 1280 }, height: { ideal: 720 } }
        : {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: { ideal: "environment" },
          },
      audio: false,
    };

    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setStatus("active");

      // Enumerate devices for camera switching
      const allDevices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = allDevices
        .filter((d) => d.kind === "videoinput")
        .map((d) => ({ deviceId: d.deviceId, label: d.label || `Camera ${d.deviceId.slice(0, 6)}` }));
      setDevices(videoDevices);
    } catch (err: any) {
      stopStream();
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setStatus("denied");
        setError("Camera permission was denied. Please allow camera access in your browser settings.");
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        setStatus("unavailable");
        setError("No camera found on this device.");
      } else {
        setStatus("error");
        setError(err.message || "Failed to start camera.");
      }
    }
  }, [stopStream]);

  const switchCamera = useCallback(async (deviceId: string) => {
    setSelectedDeviceId(deviceId);
    await startCamera(deviceId);
  }, [startCamera]);

  const captureFrame = useCallback((): ImageData | null => {
    const video = videoRef.current;
    if (!video || video.readyState < video.HAVE_ENOUGH_DATA) return null;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return ctx.getImageData(0, 0, canvas.width, canvas.height);
  }, []);

  const captureBlob = useCallback((): Promise<File | null> => {
    return new Promise((resolve) => {
      const video = videoRef.current;
      if (!video || video.readyState < video.HAVE_ENOUGH_DATA) return resolve(null);

      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      if (!ctx) return resolve(null);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob(
        (blob) => {
          if (!blob) return resolve(null);
          resolve(new File([blob], `scan-${Date.now()}.jpg`, { type: "image/jpeg" }));
        },
        "image/jpeg",
        0.92
      );
    });
  }, []);

  const captureDataUrl = useCallback((): string | null => {
    const video = videoRef.current;
    if (!video || video.readyState < video.HAVE_ENOUGH_DATA) return null;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.92);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStream();
    };
  }, [stopStream]);

  return {
    videoRef,
    status,
    error,
    devices,
    selectedDeviceId,
    startCamera,
    stopStream,
    switchCamera,
    captureFrame,
    captureBlob,
    captureDataUrl,
  };
}
