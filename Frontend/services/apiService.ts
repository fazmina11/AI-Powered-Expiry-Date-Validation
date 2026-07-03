// API Service for interacting with the backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/v1";
const AUTH_BASE_URL = process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:8001";

// ─── Types ─────────────────────────────────────────────────────────────────

export interface Product {
  id: string;
  name: string;
  sku: string;
  barcode: string;
  category: string | null;
  brand: string | null;
  description: string | null;
  mrp: number | null;
  is_perishable: boolean | null;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  sku: string;
  barcode: string;
  barcode_type?: string;
  category?: string;
  brand?: string;
  manufacturer?: string;
  description?: string;
  mrp?: number;
  is_perishable?: boolean;
}

export interface ProductUpdate {
  name?: string;
  sku?: string;
  barcode?: string;
  category?: string;
  brand?: string;
  description?: string;
  mrp?: number;
  is_perishable?: boolean;
}

export interface InventoryItem {
  id: string;
  product_id: string;
  batch_number: string | null;
  manufacturing_date: string | null;
  expiry_date: string | null;
  remaining_days: number | null;
  status: string;
  decision_reason: string | null;
  created_at: string;
}

export interface InventoryIntakeRequest {
  product_id: string;
  barcode_scan_id?: string;
  ocr_result_id?: string;
  batch_number?: string;
  manufacturing_date?: string;
  expiry_date?: string;
  status: string;
}

export interface DashboardStats {
  total_products: number;
  total_inventory: number;
  expiring_soon: number;
  expired: number;
  accepted: number;
  rejected: number;
  manual_review: number;
  validated_today: number;
}

export interface ScanResult {
  status: string;
  reject_reason?: string;
  barcode?: {
    value?: string | null;
    barcode_type?: string | null;
    supplier_grade?: string | null;
  };
  product?: {
    name?: string | null;
    brand?: string | null;
    category?: string | null;
    description?: string | null;
  };
  expiry?: {
    expiry_date?: string | null;
  };
  manufacturing?: {
    manufacturing_date?: string | null;
  };
  batch?: {
    batch_number?: string | null;
  };
  ocr?: {
    confidence?: number | null;
    raw_text?: string | null;
  };
  [key: string]: any;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

// ─── Helpers ───────────────────────────────────────────────────────────────

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const msg =
      typeof errorData.detail === "string"
        ? errorData.detail
        : errorData.detail?.message ||
          errorData.message ||
          `API error: ${response.status}`;
    throw new Error(msg);
  }

  return response.json();
}

// ─── Auth API ─────────────────────────────────────────────────────────────

export const authApi = {
  async login(email: string, password: string) {
    const res = await fetch(`${AUTH_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      const msg =
        typeof body.detail === "string"
          ? body.detail
          : Array.isArray(body.detail)
          ? body.detail.map((e: { loc: string[]; msg: string }) => `${e.loc[e.loc.length - 1]}: ${e.msg}`).join(", ")
          : "Login failed";
      throw new Error(msg);
    }
    return res.json() as Promise<{ access_token: string; token_type: string }>;
  },

  async signup(name: string, email: string, password: string) {
    const res = await fetch(`${AUTH_BASE_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      const msg =
        typeof body.detail === "string"
          ? body.detail
          : Array.isArray(body.detail)
          ? body.detail.map((e: { loc: string[]; msg: string }) => `${e.loc[e.loc.length - 1]}: ${e.msg}`).join(", ")
          : "Signup failed";
      throw new Error(msg);
    }
    return res.json() as Promise<{ access_token: string; token_type: string }>;
  },

  async me(token: string) {
    const res = await fetch(`${AUTH_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Could not fetch user profile");
    return res.json() as Promise<{ email: string; name: string }>;
  },
};

// ─── Stats API ────────────────────────────────────────────────────────────

export const statsApi = {
  async get(): Promise<DashboardStats> {
    const response = await apiFetch<ApiResponse<DashboardStats>>("/stats");
    return response.data;
  },
};

// ─── Product API ──────────────────────────────────────────────────────────

export const productApi = {
  async getAll(skip = 0, limit = 50): Promise<Product[]> {
    const response = await apiFetch<ApiResponse<Product[]>>(
      `/products?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  async getById(id: string): Promise<Product> {
    const response = await apiFetch<ApiResponse<Product>>(`/products/${id}`);
    return response.data;
  },

  async getByBarcode(barcode: string): Promise<Product> {
    const response = await apiFetch<ApiResponse<Product>>(
      `/products/barcode/${barcode}`
    );
    return response.data;
  },

  async create(product: ProductCreate): Promise<Product> {
    const response = await apiFetch<ApiResponse<Product>>("/products", {
      method: "POST",
      body: JSON.stringify(product),
    });
    return response.data;
  },

  async update(id: string, product: ProductUpdate): Promise<Product> {
    const response = await apiFetch<ApiResponse<Product>>(`/products/${id}`, {
      method: "PUT",
      body: JSON.stringify(product),
    });
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiFetch<ApiResponse<null>>(`/products/${id}`, {
      method: "DELETE",
    });
  },
};

// ─── Inventory API ────────────────────────────────────────────────────────

export const inventoryApi = {
  async getAll(
    skip = 0,
    limit = 100
  ): Promise<{ total: number; items: InventoryItem[] }> {
    const response = await apiFetch<
      ApiResponse<{ total: number; items: InventoryItem[] }>
    >(`/inventory?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async getById(id: string): Promise<InventoryItem> {
    const response = await apiFetch<ApiResponse<InventoryItem>>(
      `/inventory/${id}`
    );
    return response.data;
  },

  async update(id: string, data: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await apiFetch<ApiResponse<InventoryItem>>(`/inventory/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiFetch<ApiResponse<null>>(`/inventory/${id}`, {
      method: "DELETE",
    });
  },

  async intake(data: InventoryIntakeRequest): Promise<InventoryItem> {
    const response = await apiFetch<ApiResponse<InventoryItem>>(
      "/inventory/intake",
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
    return response.data;
  },
};

// ─── Scan API ─────────────────────────────────────────────────────────────

export const scanApi = {
  /** Upload an image file and run the full OCR + barcode pipeline */
  async scanImage(file: File): Promise<ScanResult> {
    const formData = new FormData();
    formData.append("file", file);

    const token = getAuthToken();
    const res = await fetch(`${API_BASE_URL}/ocr/upload`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Scan failed: ${res.status}`);
    }

    const json = (await res.json()) as ApiResponse<ScanResult>;
    return json.data;
  },

  /** Look up a barcode string directly */
  async lookupBarcode(barcode: string): Promise<{
    found: boolean;
    product: Product | null;
    inventory: InventoryItem[];
  }> {
    try {
      const product = await productApi.getByBarcode(barcode);
      // Inventory fetch omitted to align with backend changes to GET /products/barcode/{barcode}
      return { found: true, product, inventory: [] };
    } catch (e) {
      return { found: false, product: null, inventory: [] };
    }
  },
};

// ─── Alerts & Reviews API ──────────────────────────────────────────────────

export interface ScanAlert {
  id: string;
  scan_session_id: string | null;
  inventory_item_id: string | null;
  alert_type: string;
  severity: string;
  message: string;
  issue: string;
  is_resolved: boolean;
  created_at: string | null;
  resolved_at: string | null;
  product_name: string;
  barcode: string;
}

export interface AlertDetails extends ScanAlert {
  error_reason: string;
  ocr_raw_text: string | null;
  detected_mfg: string | null;
  detected_exp: string | null;
  detected_batch: string | null;
  image_url: string | null;
}

export interface AlertSummary {
  total_alerts: number;
  critical_alerts: number;
  warnings: number;
  resolved_alerts: number;
  resolved_today: number;
  ocr_failed: number;
  missing_exp: number;
  unknown_barcode: number;
  pending_reviews: number;
}

export interface ManualReview {
  id: string;
  scan_session_id: string | null;
  inventory_item_id: string | null;
  review_type: string;
  review_status: string;
  created_at: string | null;
  product_name: string;
  barcode: string;
  batch_number: string | null;
  original_mfg_date: string | null;
  original_expiry_date: string | null;
  corrected_mfg_date: string | null;
  corrected_expiry_date: string | null;
  human_decision: string | null;
}

export const alertApi = {
  async getSummary(): Promise<AlertSummary> {
    const response = await apiFetch<ApiResponse<AlertSummary>>("/alerts/summary");
    return response.data;
  },

  async getAlerts(params?: { status?: string; search?: string; severity?: string; alert_type?: string }): Promise<ScanAlert[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append("status", params.status);
    if (params?.search) searchParams.append("search", params.search);
    if (params?.severity) searchParams.append("severity", params.severity);
    if (params?.alert_type) searchParams.append("alert_type", params.alert_type);
    
    const query = searchParams.toString() ? `?${searchParams.toString()}` : "";
    const response = await apiFetch<ApiResponse<{ alerts: ScanAlert[] }>>(`/alerts${query}`);
    return response.data.alerts;
  },
  
  async getAlertDetails(alertId: string): Promise<AlertDetails> {
    const response = await apiFetch<ApiResponse<AlertDetails>>(`/alerts/${alertId}`);
    return response.data;
  },

  async resolveAlert(alertId: string, notes?: string): Promise<{ id: string; is_resolved: boolean }> {
    const response = await apiFetch<ApiResponse<{ id: string; is_resolved: boolean }>>(`/alerts/${alertId}/resolve`, {
      method: "POST",
      body: JSON.stringify({ notes }),
    });
    return response.data;
  },
};

export const reviewApi = {
  async getReviews(params?: { status?: string; search?: string }): Promise<ManualReview[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append("status", params.status);
    if (params?.search) searchParams.append("search", params.search);
    
    const query = searchParams.toString() ? `?${searchParams.toString()}` : "";
    const response = await apiFetch<ApiResponse<{ reviews: ManualReview[] }>>(`/reviews${query}`);
    return response.data.reviews;
  },
  
  async correctReview(
    reviewId: string, 
    data: { 
      decision: string;
      corrected_product_name?: string;
      corrected_mfg_date?: string;
      corrected_expiry_date?: string;
      corrected_batch_number?: string;
      corrected_description?: string;
      reviewer_note?: string;
    }
  ): Promise<{ id: string; status: string }> {
    const response = await apiFetch<ApiResponse<{ id: string; status: string }>>(`/reviews/${reviewId}/correct`, {
      method: "POST",
      body: JSON.stringify(data),
    });
    return response.data;
  },
};
