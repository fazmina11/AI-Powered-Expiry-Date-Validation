// API Service for interacting with the backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Types based on backend schemas
export interface Product {
  id: number;
  name: string;
  sku: string;
  barcode: string;
  category: string | null;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  sku: string;
  barcode: string;
  category?: string;
  image_url?: string;
}

export interface ProductUpdate {
  name?: string;
  sku?: string;
  barcode?: string;
  category?: string;
  image_url?: string;
}

export interface InventoryItem {
  id: number;
  product_id: number;
  batch_number: string | null;
  manufacturing_date: string | null;
  expiry_date: string | null;
  remaining_days: number | null;
  status: string;
  decision_reason: string | null;
  created_at: string;
}

export interface InventoryIntakeRequest {
  barcode: string;
  batch_number: string;
  manufacturing_date?: string;
  expiry_date?: string;
}

interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

// Helper for fetch requests
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail?.message || `API error: ${response.status}`
    );
  }

  return response.json();
}

// Product API functions
export const productApi = {
  // Get all products
  async getAll(skip = 0, limit = 50): Promise<Product[]> {
    const response = await apiFetch<ApiResponse<Product[]>>(
      `/products?skip=${skip}&limit=${limit}`
    );
    return response.data;
  },

  // Get product by ID
  async getById(id: number): Promise<Product> {
    const response = await apiFetch<ApiResponse<Product>>(`/products/${id}`);
    return response.data;
  },

  // Get product by barcode
  async getByBarcode(barcode: string): Promise<Product> {
    const response = await apiFetch<ApiResponse<Product>>(
      `/products/barcode/${barcode}`
    );
    return response.data;
  },

  // Create product
  async create(product: ProductCreate): Promise<Product> {
    const response = await apiFetch<ApiResponse<Product>>("/products", {
      method: "POST",
      body: JSON.stringify(product),
    });
    return response.data;
  },

  // Update product
  async update(id: number, product: ProductUpdate): Promise<Product> {
    const response = await apiFetch<ApiResponse<Product>>(`/products/${id}`, {
      method: "PUT",
      body: JSON.stringify(product),
    });
    return response.data;
  },

  // Delete product
  async delete(id: number): Promise<void> {
    await apiFetch<ApiResponse<null>>(`/products/${id}`, {
      method: "DELETE",
    });
  },
};

// Inventory API functions
export const inventoryApi = {
  // Get all inventory items
  async getAll(skip = 0, limit = 50): Promise<{ total: number; items: InventoryItem[] }> {
    const response = await apiFetch<
      ApiResponse<{ total: number; items: InventoryItem[] }>
    >(`/inventory?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Get inventory by ID
  async getById(id: number): Promise<InventoryItem> {
    const response = await apiFetch<ApiResponse<InventoryItem>>(
      `/inventory/${id}`
    );
    return response.data;
  },

  // Create inventory intake
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
