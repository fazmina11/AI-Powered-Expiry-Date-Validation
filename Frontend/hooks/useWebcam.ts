import { useRef, useState, useCallback } from "react";
import Webcam from "react-webcam";

export function useWebcam() {
  const webcamRef = useRef<Webcam>(null);
  const [isCameraActive, setIsCameraActive] = useState(true);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const captureLabelImage = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setPreview(imageSrc);
      
      fetch(imageSrc)
        .then((res) => res.blob())
        .then((blob) => {
          const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
          setSelectedFile(file);
        });
    }
  }, []);

  const resetCamera = useCallback(() => {
    setPreview(null);
    setSelectedFile(null);
  }, []);

  return {
    webcamRef,
    isCameraActive,
    setIsCameraActive,
    preview,
    setPreview,
    selectedFile,
    setSelectedFile,
    captureLabelImage,
    resetCamera,
  };
}
