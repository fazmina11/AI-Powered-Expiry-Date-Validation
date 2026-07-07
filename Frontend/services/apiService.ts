// API Service for interacting with the backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const AUTH_BASE_URL = process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:8000";

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

function unwrapApiData<T>(body: unknown): T {
  if (
    body &&
    typeof body === "object" &&
    "success" in body &&
    "data" in body &&
    (body as ApiResponse<T>).data !== undefined
  ) {
    return (body as ApiResponse<T>).data;
  }

  return body as T;
}

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
    const body = await res.json();
    return unwrapApiData<{ access_token: string; token_type: string }>(body);
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
    const body = await res.json();
    return unwrapApiData<{ access_token: string; token_type: string }>(body);
  },

  async me(token: string) {
    const res = await fetch(`${AUTH_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Could not fetch user profile");
    const body = await res.json();
    return unwrapApiData<{ email: string; name: string }>(body);
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
  inventory_item_id: string | null;
  product_name: string;
  alert_type: string;
  severity: string;
  message: string;
  is_resolved: boolean;
  created_at: string | null;
  resolved_at: string | null;
}

export interface ManualReview {
  id: string;
  inventory_item_id: string | null;
  product_name: string;
  review_type: string;
  review_status: string;
  human_decision: string | null;
  review_notes: string | null;
  created_at: string | null;
}

export const alertApi = {
  async getAlerts(): Promise<ScanAlert[]> {
    const response = await apiFetch<ApiResponse<{ alerts: ScanAlert[] }>>("/alerts");
    return response.data.alerts;
  },
  
  async resolveAlert(alertId: string): Promise<{ id: string; is_resolved: boolean }> {
    const response = await apiFetch<ApiResponse<{ id: string; is_resolved: boolean }>>(`/alerts/${alertId}/resolve`, {
      method: "POST",
    });
    return response.data;
  },
};

export const reviewApi = {
  async getReviews(): Promise<ManualReview[]> {
    const response = await apiFetch<ApiResponse<{ reviews: ManualReview[] }>>("/reviews");
    return response.data.reviews;
  },
  
  async resolveReview(reviewId: string, decision: string, notes?: string): Promise<{ id: string; status: string }> {
    const response = await apiFetch<ApiResponse<{ id: string; status: string }>>(`/reviews/${reviewId}/resolve`, {
      method: "POST",
      body: JSON.stringify({ decision, notes }),
    });
    return response.data;
  },
};
