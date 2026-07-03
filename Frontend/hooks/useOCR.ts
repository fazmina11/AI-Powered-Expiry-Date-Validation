import { useState, useCallback, useRef } from "react";
import { scanFlowApi, OCRData } from "@/services/scanService";

export type OCRState = "idle" | "uploading" | "processing" | "completed" | "error";

export function useOCR(sessionId: string | null) {
  const [ocrState, setOcrState] = useState<OCRState>("idle");
  const [ocrData, setOcrData] = useState<OCRData>({});
  const [imagePath, setImagePath] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [ocrError, setOcrError] = useState<string | null>(null);
  const calledRef = useRef(false);

  const runOCR = useCallback(async (file: File, previewDataUrl: string) => {
    if (!sessionId || calledRef.current) return;
    calledRef.current = true;
    setImagePreview(previewDataUrl);
    setOcrState("uploading");
    setOcrError(null);

    try {
      const uploadRes = await scanFlowApi.uploadImage(sessionId, file);
      setImagePath(uploadRes.image_path);
      setOcrState("processing");

      const ocrRes = await scanFlowApi.runOCR(sessionId, uploadRes.image_path);
      const extracted = ocrRes.extracted_data ?? {};

      setOcrData({
        product_name: extracted.product?.name ?? "",
        brand: extracted.product?.brand ?? "",
        description: extracted.product?.description ?? "",
        manufacturing_date: extracted.manufacturing?.manufacturing_date ?? "",
        expiry_date: extracted.expiry?.expiry_date ?? "",
        packed_date: extracted.packed?.packed_date ?? "",
        batch_number: extracted.batch?.batch_number ?? "",
        mrp: extracted.mrp?.value ?? undefined,
        raw_text: extracted.ocr?.raw_text ?? "",
        confidence: extracted.ocr?.confidence ?? undefined,
      });
      setOcrState("completed");
    } catch (err: any) {
      setOcrError(err.message || "OCR processing failed");
      setOcrState("error");
    }
  }, [sessionId]);

  const resetOCR = useCallback(() => {
    setOcrState("idle");
    setOcrData({});
    setImagePath(null);
    setImagePreview(null);
    setOcrError(null);
    calledRef.current = false;
  }, []);

  return {
    ocrState,
    ocrData,
    setOcrData,
    imagePath,
    imagePreview,
    ocrError,
    runOCR,
    resetOCR,
  };
}
