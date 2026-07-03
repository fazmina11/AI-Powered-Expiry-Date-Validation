"use client";

import { useState, useEffect } from "react";
import {
  Package,
  BarChart3,
  LayoutDashboard,
  Bell,
  Search,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Calendar,
  Filter,
  MoreVertical,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  ChevronRight,
  X,
  Edit2,
  Trash2,
  Eye,
  Loader2,
  Thermometer,
  Snowflake,
  Wind,
  Sun,
  Scan,
  Boxes,
  FileText,
  AlertCircle,
  CalendarRange,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { productApi, inventoryApi, statsApi, Product, ProductCreate, ProductUpdate, InventoryItem, DashboardStats } from "@/services/apiService";

// --- Components ---

// Modal component
const Modal = ({
  isOpen,
  onClose,
  title,
  children,
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="size-5 text-gray-500" />
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
};

// Product Form Component
const ProductForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
}: {
  initialData?: Product;
  onSubmit: (data: ProductCreate | ProductUpdate) => void;
  onCancel: () => void;
  isLoading: boolean;
}) => {
  const [formData, setFormData] = useState({
    name: initialData?.name || "",
    sku: initialData?.sku || "",
    barcode: initialData?.barcode || "",
    category: initialData?.category || "",
    image_url: initialData?.image_url || "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Product Name *</label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            placeholder="e.g. Organic Almond Milk"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">SKU *</label>
          <input
            type="text"
            required
            value={formData.sku}
            onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono"
            placeholder="e.g. SKU-001"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Barcode *</label>
          <input
            type="text"
            required
            value={formData.barcode}
            onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono"
            placeholder="e.g. 123456789012"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Category</label>
          <input
            type="text"
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            placeholder="e.g. Beverages, Dairy, Produce"
          />
        </div>
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Image URL</label>
        <input
          type="url"
          value={formData.image_url}
          onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
          className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          placeholder="https://example.com/product.jpg"
        />
      </div>
      <div className="flex gap-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 px-6 py-2.5 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors font-medium"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="flex-1 px-6 py-2.5 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors font-medium flex items-center justify-center gap-2"
          disabled={isLoading}
        >
          {isLoading && <Loader2 className="size-4 animate-spin" />}
          {initialData ? "Update Product" : "Add Product"}
        </button>
      </div>
    </form>
  );
};

// Product Detail View
const ProductDetail = ({
  product,
  inventoryItems,
  onClose,
  onEdit,
  onDelete,
  isLoading,
}: {
  product: Product;
  inventoryItems: InventoryItem[];
  onClose: () => void;
  onEdit: () => void;
  onDelete: () => void;
  isLoading: boolean;
}) => {
  return (
    <div className="space-y-6">
      {/* Product Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full aspect-square object-cover rounded-2xl border border-gray-200"
            />
          ) : (
            <div className="w-full aspect-square bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center border border-gray-200">
              <Package className="size-16 text-gray-400" />
            </div>
          )}
        </div>
        <div className="md:col-span-2 space-y-4">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">{product.name}</h3>
            <div className="flex items-center gap-4 mt-2">
              <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm font-medium rounded-full">
                {product.category || "Uncategorized"}
              </span>
              <span className="text-gray-500 text-sm font-mono">SKU: {product.sku}</span>
              <span className="text-gray-500 text-sm font-mono">Barcode: {product.barcode}</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 pt-4">
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-gray-500 text-sm">Created At</p>
              <p className="text-gray-900 font-medium">
                {new Date(product.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-gray-500 text-sm">Last Updated</p>
              <p className="text-gray-900 font-medium">
                {new Date(product.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="flex gap-3 pt-4">
            <button
              onClick={onEdit}
              className="flex items-center gap-2 px-4 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-medium"
            >
              <Edit2 className="size-4" />
              Edit Product
            </button>
            <button
              onClick={onDelete}
              className="flex items-center gap-2 px-4 py-2.5 bg-red-50 text-red-700 rounded-xl hover:bg-red-100 transition-colors font-medium"
            >
              <Trash2 className="size-4" />
              Delete Product
            </button>
          </div>
        </div>
      </div>

      {/* Inventory Items */}
      <div className="border-t border-gray-200 pt-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Inventory Batches</h4>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="size-6 animate-spin text-gray-400" />
          </div>
        ) : inventoryItems.length > 0 ? (
          <div className="space-y-3">
            {inventoryItems.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200"
              >
                <div>
                  <p className="font-medium text-gray-900">
                    Batch: {item.batch_number || "N/A"}
                  </p>
                  <div className="flex items-center gap-4 mt-1">
                    {item.manufacturing_date && (
                      <span className="text-sm text-gray-500">
                        MFD: {new Date(item.manufacturing_date).toLocaleDateString()}
                      </span>
                    )}
                    {item.expiry_date && (
                      <span className="text-sm text-gray-500">
                        Expiry: {new Date(item.expiry_date).toLocaleDateString()}
                      </span>
                    )}
                    {item.remaining_days !== null && (
                      <span
                        className={`text-sm font-medium px-2 py-0.5 rounded-full ${
                          item.remaining_days < 30
                            ? "bg-red-100 text-red-700"
                            : item.remaining_days < 90
                            ? "bg-amber-100 text-amber-700"
                            : "bg-green-100 text-green-700"
                        }`}
                      >
                        {item.remaining_days} days remaining
                      </span>
                    )}
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    item.status === "ACCEPTED"
                      ? "bg-green-100 text-green-700"
                      : item.status === "REJECTED"
                      ? "bg-red-100 text-red-700"
                      : item.status === "PRIORITY_SALE"
                      ? "bg-amber-100 text-amber-700"
                      : "bg-gray-100 text-gray-700"
                  }`}
                >
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 bg-gray-50 rounded-xl border border-gray-200">
            <Package className="size-8 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-500">No inventory batches yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

// --- Main Dashboard Page ---

export default function DashboardPage() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"inventory" | "intelligence">("inventory");

  // Data states
  const [products, setProducts] = useState<Product[]>([]);
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  const [inventoryStats, setInventoryStats] = useState<DashboardStats>({
    total_products: 0,
    total_inventory: 0,
    expiring_soon: 0,
    expired: 0,
    accepted: 0,
    rejected: 0,
    manual_review: 0,
    validated_today: 0,
  });

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [selectedProductInventory, setSelectedProductInventory] = useState<InventoryItem[]>([]);
  const [isLoadingInventory, setIsLoadingInventory] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch products on load
  useEffect(() => {
    if (isLoading) {
      return;
    }

    if (!user) {
      router.push("/login");
      return;
    }
    fetchProducts();
  }, [user, isLoading, router]);

  const fetchProducts = async () => {
    try {
      setIsLoadingProducts(true);
      const [data, stats, invData] = await Promise.all([
        productApi.getAll(),
        statsApi.get().catch(() => null),
        inventoryApi.getAll(),
      ]);
      setProducts(data);
      if (stats) setInventoryStats(stats);
      setInventoryItems(invData.items || []);
    } catch (error) {
      console.error("Failed to fetch products:", error);
    } finally {
      setIsLoadingProducts(false);
    }
  };

  const handleAddProduct = async (data: ProductCreate) => {
    try {
      setIsSubmitting(true);
      await productApi.create(data);
      await fetchProducts();
      setIsAddModalOpen(false);
    } catch (error) {
      alert("Failed to add product: " + (error as Error).message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditProduct = async (data: ProductUpdate) => {
    if (!selectedProduct) return;
    try {
      setIsSubmitting(true);
      await productApi.update(selectedProduct.id, data);
      await fetchProducts();
      setIsEditModalOpen(false);
    } catch (error) {
      alert("Failed to update product: " + (error as Error).message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteProduct = async () => {
    if (!selectedProduct) return;
    try {
      setIsSubmitting(true);
      await productApi.delete(selectedProduct.id);
      await fetchProducts();
      setIsDeleteConfirmOpen(false);
      setIsDetailModalOpen(false);
    } catch (error) {
      alert("Failed to delete product: " + (error as Error).message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleViewProduct = async (product: Product) => {
    setSelectedProduct(product);
    setIsDetailModalOpen(true);
    // Fetch inventory items for this product (mock for now since we don't have a filter endpoint)
    setIsLoadingInventory(true);
    try {
      const data = await inventoryApi.getAll();
      // Filter inventory items for this product (mock logic)
      const filtered = data.items.filter(
        (item) => item.product_id === product.id || Math.random() > 0.7
      );
      setSelectedProductInventory(filtered);
    } catch (error) {
      console.error("Failed to fetch inventory:", error);
    } finally {
      setIsLoadingInventory(false);
    }
  };

  const getStatusBadge = (product: Product) => {
    // Mock status based on random for now
    const statuses = ["in-stock", "low-stock", "out-of-stock"];
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    if (status === "in-stock") {
      return (
        <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full flex items-center gap-1 w-fit">
          <CheckCircle2 className="size-3" />
          In Stock
        </span>
      );
    } else if (status === "low-stock") {
      return (
        <span className="px-3 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded-full flex items-center gap-1 w-fit">
          <AlertTriangle className="size-3" />
          Low Stock
        </span>
      );
    } else {
      return (
        <span className="px-3 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full flex items-center gap-1 w-fit">
          <AlertTriangle className="size-3" />
          Out of Stock
        </span>
      );
    }
  };

  // Derived Data for Dashboard
  const expiredItems = inventoryItems.filter(item => item.remaining_days !== null && item.remaining_days <= 0);
  const nearingExpiryItems = inventoryItems.filter(item => item.remaining_days !== null && item.remaining_days > 0 && item.remaining_days <= 30);

  if (isLoading || !user) {
    return null;
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Right Content Area - Light White Theme */}
      <main className="flex-1 bg-white overflow-y-auto">
        <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-8 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Dashboard Overview
              </h1>
              <p className="text-gray-500 mt-1">
                Monitor your inventory health and warehouse environment
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  className="pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all w-64"
                />
              </div>
              <button className="relative p-2.5 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                <Bell className="size-5 text-gray-600" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
              </button>
            </div>
          </div>
        </header>

        <div className="p-8 space-y-8">
          
          {/* Top Section: Expired & Nearing Expiry */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Expired Products */}
            <div className="bg-white border border-red-200 rounded-2xl shadow-sm overflow-hidden flex flex-col">
              <div className="p-5 border-b border-red-100 bg-red-50/50 flex items-center gap-3">
                <div className="p-2 bg-red-100 text-red-600 rounded-lg">
                  <AlertTriangle className="size-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-red-900">Expired Products</h2>
                  <p className="text-sm text-red-600">Immediate action required</p>
                </div>
                <span className="ml-auto bg-red-600 text-white px-3 py-1 rounded-full text-sm font-bold">
                  {expiredItems.length}
                </span>
              </div>
              <div className="p-5 flex-1 overflow-y-auto max-h-80">
                {expiredItems.length > 0 ? (
                  <div className="space-y-3">
                    {expiredItems.map((item) => {
                      const product = products.find(p => p.id === item.product_id);
                      return (
                        <div key={item.id} className="flex items-center justify-between p-3 bg-red-50/30 border border-red-100 rounded-xl">
                          <div>
                            <p className="font-semibold text-gray-900">{product?.name || "Unknown Product"}</p>
                            <p className="text-xs text-gray-500">Batch: {item.batch_number}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-bold text-red-600">Expired {Math.abs(item.remaining_days!)} days ago</p>
                            <p className="text-xs text-gray-500">Exp: {item.expiry_date && new Date(item.expiry_date).toLocaleDateString()}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-400 space-y-2">
                    <CheckCircle2 className="size-8 text-green-400" />
                    <p>No expired products!</p>
                  </div>
                )}
              </div>
            </div>

            {/* Nearing Expiry */}
            <div className="bg-white border border-amber-200 rounded-2xl shadow-sm overflow-hidden flex flex-col">
              <div className="p-5 border-b border-amber-100 bg-amber-50/50 flex items-center gap-3">
                <div className="p-2 bg-amber-100 text-amber-600 rounded-lg">
                  <Clock className="size-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-amber-900">Nearing Expiry</h2>
                  <p className="text-sm text-amber-600">Expires within 30 days</p>
                </div>
                <span className="ml-auto bg-amber-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                  {nearingExpiryItems.length}
                </span>
              </div>
              <div className="p-5 flex-1 overflow-y-auto max-h-80">
                {nearingExpiryItems.length > 0 ? (
                  <div className="space-y-3">
                    {nearingExpiryItems.map((item) => {
                      const product = products.find(p => p.id === item.product_id);
                      return (
                        <div key={item.id} className="flex items-center justify-between p-3 bg-amber-50/30 border border-amber-100 rounded-xl">
                          <div>
                            <p className="font-semibold text-gray-900">{product?.name || "Unknown Product"}</p>
                            <p className="text-xs text-gray-500">Batch: {item.batch_number}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-bold text-amber-600">In {item.remaining_days} days</p>
                            <p className="text-xs text-gray-500">Exp: {item.expiry_date && new Date(item.expiry_date).toLocaleDateString()}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-gray-400 space-y-2">
                    <Package className="size-8 text-gray-300" />
                    <p>No products nearing expiry.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Middle Section: Warehouse Temperatures */}
          <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
            <div className="flex items-center gap-2 mb-6">
              <Thermometer className="size-5 text-gray-600" />
              <h2 className="text-lg font-bold text-gray-900">Warehouse Climate Monitoring</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Freezer */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
                    <Snowflake className="size-5" />
                  </div>
                  <span className="flex items-center gap-1 text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">
                    <span className="size-1.5 rounded-full bg-green-500 animate-pulse" /> Optimal
                  </span>
                </div>
                <p className="text-sm text-gray-500 font-medium">Freezer Zone</p>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-3xl font-bold text-gray-900">-18.5</span>
                  <span className="text-gray-500 font-medium">°C</span>
                </div>
                <p className="text-xs text-gray-400 mt-2">Target: -18°C to -22°C</p>
              </div>

              {/* Cool Storage */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-cyan-100 text-cyan-600 rounded-lg">
                    <Wind className="size-5" />
                  </div>
                  <span className="flex items-center gap-1 text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">
                    <span className="size-1.5 rounded-full bg-green-500 animate-pulse" /> Optimal
                  </span>
                </div>
                <p className="text-sm text-gray-500 font-medium">Cool Storage</p>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-3xl font-bold text-gray-900">4.2</span>
                  <span className="text-gray-500 font-medium">°C</span>
                </div>
                <p className="text-xs text-gray-400 mt-2">Target: 2°C to 8°C</p>
              </div>

              {/* Normal Storage */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-orange-100 text-orange-600 rounded-lg">
                    <Boxes className="size-5" />
                  </div>
                  <span className="flex items-center gap-1 text-xs font-bold text-amber-600 bg-amber-100 px-2 py-1 rounded-full">
                    <span className="size-1.5 rounded-full bg-amber-500 animate-pulse" /> Warning
                  </span>
                </div>
                <p className="text-sm text-gray-500 font-medium">Normal Storage</p>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-3xl font-bold text-orange-600">26.8</span>
                  <span className="text-gray-500 font-medium">°C</span>
                </div>
                <p className="text-xs text-gray-400 mt-2">Target: 15°C to 25°C</p>
              </div>

              {/* External */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-2 bg-yellow-100 text-yellow-600 rounded-lg">
                    <Sun className="size-5" />
                  </div>
                  <span className="text-xs font-bold text-gray-500 bg-gray-200 px-2 py-1 rounded-full">
                    External
                  </span>
                </div>
                <p className="text-sm text-gray-500 font-medium">Local Weather</p>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-3xl font-bold text-gray-900">31.0</span>
                  <span className="text-gray-500 font-medium">°C</span>
                </div>
                <p className="text-xs text-gray-400 mt-2">Humidity: 65%</p>
              </div>
            </div>
          </div>

          {/* Bottom Section: Quick Services */}
          <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-6">Quick Services</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button 
                onClick={() => router.push('/dashboard/scan')}
                className="group flex flex-col items-center p-6 bg-slate-50 border border-slate-200 rounded-xl hover:bg-primary/5 hover:border-primary/30 transition-all text-center"
              >
                <div className="w-12 h-12 bg-white rounded-full shadow-sm flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Scan className="size-5 text-primary" />
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-primary transition-colors">Scan / Intake</h3>
                <p className="text-xs text-gray-500 mt-1">AI-powered barcode & expiry scanning</p>
              </button>

              <button 
                onClick={() => router.push('/dashboard/inventory')}
                className="group flex flex-col items-center p-6 bg-slate-50 border border-slate-200 rounded-xl hover:bg-blue-50 hover:border-blue-300 transition-all text-center"
              >
                <div className="w-12 h-12 bg-white rounded-full shadow-sm flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Package className="size-5 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">Inventory Master</h3>
                <p className="text-xs text-gray-500 mt-1">Manage all stored products & stock</p>
              </button>

              <button className="group flex flex-col items-center p-6 bg-slate-50 border border-slate-200 rounded-xl hover:bg-purple-50 hover:border-purple-300 transition-all text-center">
                <div className="w-12 h-12 bg-white rounded-full shadow-sm flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <FileText className="size-5 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">Reports</h3>
                <p className="text-xs text-gray-500 mt-1">Generate compliance & stock reports</p>
              </button>

              <button className="group flex flex-col items-center p-6 bg-slate-50 border border-slate-200 rounded-xl hover:bg-orange-50 hover:border-orange-300 transition-all text-center">
                <div className="w-12 h-12 bg-white rounded-full shadow-sm flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <CalendarRange className="size-5 text-orange-600" />
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-orange-600 transition-colors">Scheduled Checks</h3>
                <p className="text-xs text-gray-500 mt-1">Plan manual spot checks & audits</p>
              </button>
            </div>
          </div>

        </div>

        {/* Modals */}
        <Modal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          title="Add New Product"
        >
          <ProductForm
            onSubmit={handleAddProduct}
            onCancel={() => setIsAddModalOpen(false)}
            isLoading={isSubmitting}
          />
        </Modal>

        <Modal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          title="Edit Product"
        >
          {selectedProduct && (
            <ProductForm
              initialData={selectedProduct}
              onSubmit={handleEditProduct}
              onCancel={() => setIsEditModalOpen(false)}
              isLoading={isSubmitting}
            />
          )}
        </Modal>

        <Modal
          isOpen={isDetailModalOpen}
          onClose={() => setIsDetailModalOpen(false)}
          title="Product Details"
        >
          {selectedProduct && (
            <ProductDetail
              product={selectedProduct}
              inventoryItems={selectedProductInventory}
              onClose={() => setIsDetailModalOpen(false)}
              onEdit={() => {
                setIsDetailModalOpen(false);
                setIsEditModalOpen(true);
              }}
              onDelete={() => {
                setIsDetailModalOpen(false);
                setIsDeleteConfirmOpen(true);
              }}
              isLoading={isLoadingInventory}
            />
          )}
        </Modal>

        <Modal
          isOpen={isDeleteConfirmOpen}
          onClose={() => setIsDeleteConfirmOpen(false)}
          title="Delete Product"
        >
          <div className="text-center py-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Trash2 className="size-8 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Are you sure you want to delete this product?
            </h3>
            <p className="text-gray-500 mb-6">
              This action cannot be undone. The product will be permanently removed.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setIsDeleteConfirmOpen(false)}
                className="flex-1 px-6 py-2.5 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors font-medium"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteProduct}
                className="flex-1 px-6 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors font-medium flex items-center justify-center gap-2"
                disabled={isSubmitting}
              >
                {isSubmitting && <Loader2 className="size-4 animate-spin" />}
                Delete
              </button>
            </div>
          </div>
        </Modal>
      </main>

    </div>
  );
}
