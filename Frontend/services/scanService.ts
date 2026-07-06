/**
 * scanService.ts
 *
 * All scan-session endpoints live under /api/scan (NOT /api/v1/).
 * apiFetch points to /api/v1, so we maintain a separate fetch helper here.
 */

import { Product } from "./apiService";

export interface OCRData {
  product_name?: string;
  brand?: string;
  description?: string;
  manufacturing_date?: string;
  expiry_date?: string;
  packed_date?: string;
  batch_number?: string;
  mrp?: number;
  raw_text?: string;
  confidence?: number;
}

// Scan routes are mounted at /api/scan — separate from /api/v1
const SCAN_BASE = "http://localhost:8000/api/scan";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

async function scanFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`${SCAN_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers ?? {}),
    },
  });

  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = json?.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : detail?.message ?? json?.message ?? `API error ${res.status}`;
    throw new Error(msg);
  }
  return json as T;
}

interface ScanApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export const scanFlowApi = {
  async startScan(): Promise<{ session_id: string }> {
    const res = await scanFetch<ScanApiResponse<{ session_id: string }>>("/start", {
      method: "POST",
    });
    return res.data;
  },

  async submitBarcode(
    session_id: string,
    barcode: string
  ): Promise<{ product_found: boolean; product: Product | null }> {
    const res = await scanFetch<ScanApiResponse<{ product_found: boolean; product: Product | null }>>(
      "/barcode",
      { method: "POST", body: JSON.stringify({ session_id, barcode }) }
    );
    return res.data;
  },

  async uploadImage(session_id: string, file: File): Promise<{ image_path: string }> {
    const formData = new FormData();
    formData.append("session_id", session_id);
    formData.append("file", file);

    const token = getToken();
    const res = await fetch(`${SCAN_BASE}/upload`, {
      method: "POST",
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    const json = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(json?.detail || "Image upload failed");
    return (json as ScanApiResponse<{ image_path: string }>).data;
  },

  async runOCR(
    session_id: string,
    image_path: string
  ): Promise<{ extracted_data: Record<string, any> }> {
    const res = await scanFetch<ScanApiResponse<{ extracted_data: Record<string, any> }>>(
      "/run-ocr",
      { method: "POST", body: JSON.stringify({ session_id, image_path }) }
    );
    return res.data;
  },

  async finalize(
    session_id: string,
    barcode: string,
    image_path: string,
    data: OCRData
  ): Promise<void> {
    await scanFetch<ScanApiResponse<unknown>>("/finalize", {
      method: "POST",
      body: JSON.stringify({ session_id, barcode, image_path, ...data }),
    });
  },

  async cancel(session_id: string): Promise<void> {
    await scanFetch<ScanApiResponse<unknown>>(`/cancel/${session_id}`, {
      method: "POST",
    });
  },

  async validateFrame(file: Blob): Promise<{ success: boolean; usable: boolean; reason?: string }> {
    const formData = new FormData();
    formData.append("file", file, "frame.jpg");

    const token = getToken();
    const res = await fetch(`${SCAN_BASE}/validate-frame`, {
      method: "POST",
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    const json = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(json?.detail || "Frame validation failed");
    return json;
  },

  async enqueueScan(
    file: Blob,
    session_id?: string,
    barcode?: string
  ): Promise<{ ocr_result_id: string; session_id: string; status: string; image_path: string }> {
    const formData = new FormData();
    formData.append("file", file, "capture.jpg");
    if (session_id) formData.append("session_id", session_id);
    if (barcode) formData.append("barcode", barcode);

    const token = getToken();
    const res = await fetch(`${SCAN_BASE}/enqueue`, {
      method: "POST",
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });

    const json = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(json?.detail || "Enqueue scan failed");
    return (json as ScanApiResponse<{ ocr_result_id: string; session_id: string; status: string; image_path: string }>).data;
  },

  async getHistory(): Promise<OCRHistoryItem[]> {
    const res = await scanFetch<ScanApiResponse<OCRHistoryItem[]>>("/history", {
      method: "GET",
    });
    return res.data;
  },

  async getResultStatus(resultId: string): Promise<OCRHistoryItem> {
    const res = await scanFetch<ScanApiResponse<OCRHistoryItem>>(`/result/${resultId}`, {
      method: "GET",
    });
    return res.data;
  },
};

export interface OCRHistoryItem {
  id: string;
  session_id: string | null;
  status: "pending" | "processing" | "completed" | "failed";
  failure_reason: string | null;
  image_url: string | null;
  created_at: string | null;
  product: {
    name: string;
    brand: string | null;
    barcode: string | null;
  };
  extracted_data: {
    manufacturing_date: string | null;
    expiry_date: string | null;
    batch_number: string | null;
    mrp: number | null;
    raw_text: string | null;
    confidence: number;
    ml_decision?: string | null;
    ml_confidence?: number | null;
    adjusted_remaining?: number | null;
    arrhenius_remaining?: number | null;
  };
  ocr_blocks: {
    width: number;
    height: number;
    blocks: Array<{
      text: string;
      confidence: number;
      x_min: number;
      y_min: number;
      x_max: number;
      y_max: number;
    }>;
  } | null;
}
