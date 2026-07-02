"use client";

<<<<<<< HEAD
import { User, Mail, Package, AlertTriangle, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// Mock data
const mockUser = {
  name: "John Doe",
  email: "john.doe@example.com",
  avatar: null,
};

const mockStats = {
  totalProducts: 142,
  earlyExpiring: 23,
  totalInventory: 856,
  recentValidations: 12,
};

const earlyExpiringItems = [
  {
    id: 1,
    name: "Organic Milk 1L",
    pid: "PRD-001",
    expiryDate: "2024-06-30",
    daysLeft: 6,
  },
  {
    id: 2,
    name: "Greek Yogurt 500g",
    pid: "PRD-045",
    expiryDate: "2024-07-02",
    daysLeft: 8,
  },
  {
    id: 3,
    name: "Whole Wheat Bread",
    pid: "PRD-089",
    expiryDate: "2024-07-03",
    daysLeft: 9,
  },
  {
    id: 4,
    name: "Fresh Orange Juice 1L",
    pid: "PRD-123",
    expiryDate: "2024-07-05",
    daysLeft: 11,
  },
  {
    id: 5,
    name: "Cheddar Cheese Block",
    pid: "PRD-056",
    expiryDate: "2024-07-08",
    daysLeft: 14,
  },
];

export default function DashboardHome() {
  return (
    <div className="p-8 space-y-8">
      {/* User Info */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="size-16 rounded-full bg-gray-100 flex items-center justify-center">
            <User className="size-8 text-gray-500" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{mockUser.name}</h1>
            <div className="flex items-center gap-2 text-gray-500">
              <Mail className="size-4" />
              <span>{mockUser.email}</span>
            </div>
          </div>
        </div>
        <div className="text-right text-sm text-gray-500">
          <div>Last Login: Today, 09:45 AM</div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Products
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {mockStats.totalProducts}
            </div>
          </CardContent>
        </Card>
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-orange-700">
              Early Expiring Items
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">
              {mockStats.earlyExpiring}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Inventory
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {mockStats.totalInventory}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Recent Validations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {mockStats.recentValidations}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Early Expiring Items */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-xl font-bold text-gray-900">
            Early Expiring Items
          </CardTitle>
          <Button variant="secondary" className="gap-2">
            View All
            <ArrowRight className="size-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    Product Name
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    PID
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    Expiry Date
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    Days Left
                  </th>
                </tr>
              </thead>
              <tbody>
                {earlyExpiringItems.map((item) => (
                  <tr
                    key={item.id}
                    className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                  >
                    <td className="py-4 px-4 font-medium text-gray-900">
                      {item.name}
                    </td>
                    <td className="py-4 px-4 text-gray-600">{item.pid}</td>
                    <td className="py-4 px-4 text-gray-600">
                      {item.expiryDate}
                    </td>
                    <td className="py-4 px-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          item.daysLeft <= 7
                            ? "bg-red-100 text-red-800"
                            : "bg-orange-100 text-orange-800"
                        }`}
                      >
                        <AlertTriangle className="size-3 mr-1" />
                        {item.daysLeft} days
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
=======
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
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { productApi, inventoryApi, Product, ProductCreate, ProductUpdate, InventoryItem } from "@/lib/api";

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
  const { user, logout } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"inventory" | "intelligence">("inventory");

  // Data states
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  const [inventoryStats, setInventoryStats] = useState({
    totalProducts: 0,
    lowStock: 0,
    expiringSoon: 0,
    validatedToday: 0,
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
    if (!user) {
      router.push("/login");
      return;
    }
    fetchProducts();
  }, [user, router]);

  const fetchProducts = async () => {
    try {
      setIsLoadingProducts(true);
      const data = await productApi.getAll();
      setProducts(data);
      // Mock stats based on products
      setInventoryStats({
        totalProducts: data.length,
        lowStock: Math.floor(Math.random() * 20) + 5,
        expiringSoon: Math.floor(Math.random() * 15) + 3,
        validatedToday: Math.floor(Math.random() * 100) + 20,
      });
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

  if (!user) {
    return null;
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Left Sidebar - Black Theme */}
      <aside className="w-72 bg-[oklch(0.05_0_0)] border-r border-white/10 flex flex-col">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
              <Package className="text-primary-foreground size-5" />
            </div>
            <div>
              <h2 className="text-white font-bold text-lg">Cliste</h2>
              <p className="text-white/50 text-xs">Expiry Validation</p>
            </div>
          </div>
        </div>

        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center border border-white/20">
              <span className="text-white font-semibold text-lg">
                {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">
                {user.name || user.email.split("@")[0]}
              </p>
              <p className="text-white/50 text-sm truncate">{user.email}</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <p className="text-white/40 text-xs font-semibold uppercase tracking-wider px-4 mb-3">
            Main Menu
          </p>

          <button
            onClick={() => setActiveTab("inventory")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
              activeTab === "inventory"
                ? "bg-primary text-primary-foreground font-medium"
                : "text-white/70 hover:bg-white/10 hover:text-white"
            }`}
          >
            <LayoutDashboard className="size-5" />
            <span>Inventory Management</span>
            {activeTab === "inventory" && <ChevronRight className="size-4 ml-auto" />}
          </button>

          <button
            onClick={() => setActiveTab("intelligence")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
              activeTab === "intelligence"
                ? "bg-primary text-primary-foreground font-medium"
                : "text-white/70 hover:bg-white/10 hover:text-white"
            }`}
          >
            <BarChart3 className="size-5" />
            <span>Inventory Intelligence</span>
            {activeTab === "intelligence" && <ChevronRight className="size-4 ml-auto" />}
          </button>

          <div className="h-px bg-white/10 my-4" />

          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white/70 hover:bg-white/10 hover:text-white transition-all">
            <Calendar className="size-5" />
            <span>Scheduled Checks</span>
          </button>

          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white/70 hover:bg-white/10 hover:text-white transition-all">
            <Bell className="size-5" />
            <span>Alerts</span>
          </button>
        </nav>

        <div className="p-4 border-t border-white/10">
          <button
            onClick={() => {
              logout();
              router.push("/");
            }}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white/70 hover:bg-red-500/10 hover:text-red-400 transition-all"
          >
            <svg
              className="size-5"
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Right Content Area - Light White Theme */}
      <main className="flex-1 bg-white overflow-y-auto">
        <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-8 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {activeTab === "inventory" ? "Inventory Management" : "Inventory Intelligence"}
              </h1>
              <p className="text-gray-500 mt-1">
                {activeTab === "inventory"
                  ? "Manage and track your inventory items"
                  : "Gain insights and analytics from your inventory data"}
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

        <div className="p-8">
          {activeTab === "inventory" ? (
            <div className="space-y-8">
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  {
                    title: "Total Products",
                    value: inventoryStats.totalProducts,
                    change: "+12.5%",
                    isPositive: true,
                    icon: Package,
                    color: "bg-blue-500",
                  },
                  {
                    title: "Low Stock",
                    value: inventoryStats.lowStock,
                    change: "-5.2%",
                    isPositive: true,
                    icon: AlertTriangle,
                    color: "bg-amber-500",
                  },
                  {
                    title: "Expiring Soon",
                    value: inventoryStats.expiringSoon,
                    change: "+2.1%",
                    isPositive: false,
                    icon: Clock,
                    color: "bg-red-500",
                  },
                  {
                    title: "Validated Today",
                    value: inventoryStats.validatedToday,
                    change: "+18.3%",
                    isPositive: true,
                    icon: CheckCircle2,
                    color: "bg-green-500",
                  },
                ].map((stat, index) => (
                  <div
                    key={index}
                    className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className={`${stat.color} p-3 rounded-xl text-white`}>
                        <stat.icon className="size-5" />
                      </div>
                      <div
                        className={`flex items-center gap-1 text-sm font-medium ${
                          stat.isPositive ? "text-green-600" : "text-red-600"
                        }`}
                      >
                        {stat.isPositive ? (
                          <ArrowUpRight className="size-4" />
                        ) : (
                          <ArrowDownRight className="size-4" />
                        )}
                        {stat.change}
                      </div>
                    </div>
                    <div className="mt-4">
                      <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                      <p className="text-gray-500 text-sm mt-1">{stat.title}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Inventory Table */}
              <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
                <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Products</h2>
                    <p className="text-gray-500 text-sm mt-1">Manage and track your product inventory</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors">
                      <Filter className="size-4" />
                      Filter
                    </button>
                    <button
                      onClick={() => setIsAddModalOpen(true)}
                      className="flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:bg-primary/90 transition-colors"
                    >
                      <Plus className="size-4" />
                      Add Product
                    </button>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  {isLoadingProducts ? (
                    <div className="flex items-center justify-center py-16">
                      <Loader2 className="size-8 animate-spin text-gray-400" />
                    </div>
                  ) : (
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Product
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            SKU
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Category
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Barcode
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Created
                          </th>
                          <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {products.map((product) => (
                          <tr key={product.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                                  <Package className="size-5 text-gray-500" />
                                </div>
                                <span className="font-medium text-gray-900">{product.name}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600 font-mono">
                              {product.sku}
                            </td>
                            <td className="px-6 py-4">
                              <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                                {product.category || "Uncategorized"}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600 font-mono">
                              {product.barcode}
                            </td>
                            <td className="px-6 py-4">{getStatusBadge(product)}</td>
                            <td className="px-6 py-4 text-sm text-gray-600">
                              {new Date(product.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 text-right">
                              <div className="flex items-center justify-end gap-2">
                                <button
                                  onClick={() => handleViewProduct(product)}
                                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                  title="View Details"
                                >
                                  <Eye className="size-4 text-gray-500" />
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedProduct(product);
                                    setIsEditModalOpen(true);
                                  }}
                                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                  title="Edit Product"
                                >
                                  <Edit2 className="size-4 text-gray-500" />
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedProduct(product);
                                    setIsDeleteConfirmOpen(true);
                                  }}
                                  className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                                  title="Delete Product"
                                >
                                  <Trash2 className="size-4 text-red-500" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>

                <div className="p-6 border-t border-gray-200 flex items-center justify-between">
                  <p className="text-sm text-gray-500">
                    Showing <span className="font-semibold text-gray-900">1</span> to{" "}
                    <span className="font-semibold text-gray-900">{products.length}</span> of{" "}
                    <span className="font-semibold text-gray-900">{products.length}</span> results
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-900 mb-6">Expiry Trend Analysis</h3>
                  <div className="h-64 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl flex items-center justify-center">
                    <div className="text-center">
                      <BarChart3 className="size-12 text-gray-300 mx-auto mb-3" />
                      <p className="text-gray-500">Chart visualization coming soon</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-900 mb-6">Category Distribution</h3>
                  <div className="space-y-4">
                    {[
                      { name: "Beverages", percentage: 28 },
                      { name: "Dairy", percentage: 23 },
                      { name: "Produce", percentage: 20 },
                      { name: "Bakery", percentage: 16 },
                      { name: "Other", percentage: 13 },
                    ].map((category, index) => (
                      <div key={index}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-700 font-medium">
                            {category.name}
                          </span>
                          <span className="text-sm text-gray-500">{category.percentage}%</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-primary to-primary/60 rounded-full transition-all duration-1000"
                            style={{ width: `${category.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-2xl p-6">
                  <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center text-white mb-4">
                    <TrendingUp className="size-6" />
                  </div>
                  <h4 className="text-lg font-semibold text-green-900 mb-2">Waste Reduction</h4>
                  <p className="text-green-700 text-sm">
                    24% reduction in expired products this month. Great job on optimizing inventory levels!
                  </p>
                </div>

                <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-2xl p-6">
                  <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center text-white mb-4">
                    <Clock className="size-6" />
                  </div>
                  <h4 className="text-lg font-semibold text-blue-900 mb-2">Peak Expiry Hours</h4>
                  <p className="text-blue-700 text-sm">
                    Most products expire between 2-4 PM. Schedule your checks accordingly.
                  </p>
                </div>

                <div className="bg-gradient-to-br from-amber-50 to-amber-100 border border-amber-200 rounded-2xl p-6">
                  <div className="w-12 h-12 bg-amber-500 rounded-xl flex items-center justify-center text-white mb-4">
                    <AlertTriangle className="size-6" />
                  </div>
                  <h4 className="text-lg font-semibold text-amber-900 mb-2">Attention Needed</h4>
                  <p className="text-amber-700 text-sm">
                    5 products in Dairy category need immediate restocking to avoid stockouts.
                  </p>
                </div>
              </div>
            </div>
          )}
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
>>>>>>> 0f02161 (Update project for Harish branch)
    </div>
  );
}
