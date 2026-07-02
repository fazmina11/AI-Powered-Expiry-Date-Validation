"use client";

import { useState } from "react";
import { Edit, Trash2, Eye, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

// Mock products data
const mockProducts = [
  {
    id: 1,
    pid: "PRD-001",
    name: "Organic Milk 1L",
    description: "Fresh organic milk from local farms",
    category: "Dairy",
    mfgDate: "2024-06-10",
    expDate: "2024-06-30",
    quantity: 45,
    batchNumber: "BCH-2024-0610",
  },
  {
    id: 2,
    pid: "PRD-045",
    name: "Greek Yogurt 500g",
    description: "Thick and creamy Greek yogurt",
    category: "Dairy",
    mfgDate: "2024-06-12",
    expDate: "2024-07-02",
    quantity: 89,
    batchNumber: "BCH-2024-0612",
  },
  {
    id: 3,
    pid: "PRD-089",
    name: "Whole Wheat Bread",
    description: "Freshly baked whole wheat bread",
    category: "Bakery",
    mfgDate: "2024-06-20",
    expDate: "2024-07-03",
    quantity: 23,
    batchNumber: "BCH-2024-0620",
  },
  {
    id: 4,
    pid: "PRD-123",
    name: "Fresh Orange Juice 1L",
    description: "100% pure orange juice, no added sugar",
    category: "Beverages",
    mfgDate: "2024-06-18",
    expDate: "2024-07-05",
    quantity: 67,
    batchNumber: "BCH-2024-0618",
  },
  {
    id: 5,
    pid: "PRD-056",
    name: "Cheddar Cheese Block",
    description: "Premium aged cheddar cheese",
    category: "Dairy",
    mfgDate: "2024-05-20",
    expDate: "2024-07-08",
    quantity: 12,
    batchNumber: "BCH-2024-0520",
  },
  {
    id: 6,
    pid: "PRD-078",
    name: "Organic Eggs (12 pack)",
    description: "Farm-fresh organic eggs",
    category: "Poultry",
    mfgDate: "2024-06-22",
    expDate: "2024-07-12",
    quantity: 34,
    batchNumber: "BCH-2024-0622",
  },
];

export default function InventoryPage() {
  const [products, setProducts] = useState(mockProducts);
  const [selectedProduct, setSelectedProduct] = useState<(typeof mockProducts)[0] | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editFormData, setEditFormData] = useState<Partial<(typeof mockProducts)[0]>>({});

  const handleViewProduct = (product: (typeof mockProducts)[0]) => {
    setSelectedProduct(product);
    setIsEditing(false);
    setIsModalOpen(true);
  };

  const handleEditProduct = (product: (typeof mockProducts)[0]) => {
    setSelectedProduct(product);
    setEditFormData({ ...product });
    setIsEditing(true);
    setIsModalOpen(true);
  };

  const handleDeleteProduct = (productId: number) => {
    if (confirm(`Are you sure you want to delete this product?`)) {
      setProducts(products.filter((p) => p.id !== productId));
    }
  };

  const handleSaveEdit = () => {
    if (selectedProduct && editFormData) {
      setProducts(
        products.map((p) =>
          p.id === selectedProduct.id ? { ...p, ...editFormData } : p
        )
      );
      setIsModalOpen(false);
      setIsEditing(false);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
        <Button className="gap-2">
          <Plus className="size-4" />
          Add Product
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-4">
          <CardTitle>Product List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    PID
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    Product Name
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    Category
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    MFG Date
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    EXP Date
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    Quantity
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr
                    key={product.id}
                    className="border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => handleViewProduct(product)}
                  >
                    <td className="py-4 px-4 font-mono text-gray-600">
                      {product.pid}
                    </td>
                    <td className="py-4 px-4 font-medium text-gray-900">
                      {product.name}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {product.category}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {product.mfgDate}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {product.expDate}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {product.quantity}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewProduct(product);
                          }}
                        >
                          <Eye className="size-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-blue-600"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditProduct(product);
                          }}
                        >
                          <Edit className="size-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-red-600"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteProduct(product.id);
                          }}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Product Detail Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {isEditing ? "Edit Product" : "Product Details"}
            </DialogTitle>
            <DialogDescription>
              {isEditing
                ? "Make changes to the product details"
                : "View complete product information"}
            </DialogDescription>
          </DialogHeader>

          {selectedProduct && (
            <div className="space-y-4">
              {isEditing ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="edit-name">Product Name</Label>
                      <Input
                        id="edit-name"
                        value={editFormData.name || ""}
                        onChange={(e) =>
                          setEditFormData({ ...editFormData, name: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="edit-pid">PID</Label>
                      <Input
                        id="edit-pid"
                        value={editFormData.pid || ""}
                        onChange={(e) =>
                          setEditFormData({ ...editFormData, pid: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="edit-category">Category</Label>
                      <Input
                        id="edit-category"
                        value={editFormData.category || ""}
                        onChange={(e) =>
                          setEditFormData({ ...editFormData, category: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="edit-quantity">Quantity</Label>
                      <Input
                        id="edit-quantity"
                        type="number"
                        value={editFormData.quantity || ""}
                        onChange={(e) =>
                          setEditFormData({
                            ...editFormData,
                            quantity: parseInt(e.target.value),
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="edit-mfg">Manufacturing Date</Label>
                      <Input
                        id="edit-mfg"
                        type="date"
                        value={editFormData.mfgDate || ""}
                        onChange={(e) =>
                          setEditFormData({ ...editFormData, mfgDate: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="edit-exp">Expiry Date</Label>
                      <Input
                        id="edit-exp"
                        type="date"
                        value={editFormData.expDate || ""}
                        onChange={(e) =>
                          setEditFormData({ ...editFormData, expDate: e.target.value })
                        }
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-description">Description</Label>
                    <Textarea
                      id="edit-description"
                      value={editFormData.description || ""}
                      onChange={(e) =>
                        setEditFormData({
                          ...editFormData,
                          description: e.target.value,
                        })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-batch">Batch Number</Label>
                    <Input
                      id="edit-batch"
                      value={editFormData.batchNumber || ""}
                      onChange={(e) =>
                        setEditFormData({
                          ...editFormData,
                          batchNumber: e.target.value,
                        })
                      }
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">PID</div>
                      <div className="font-medium text-gray-900">
                        {selectedProduct.pid}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Category</div>
                      <div className="font-medium text-gray-900">
                        {selectedProduct.category}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">MFG Date</div>
                      <div className="font-medium text-gray-900">
                        {selectedProduct.mfgDate}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">EXP Date</div>
                      <div className="font-medium text-gray-900">
                        {selectedProduct.expDate}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Batch Number</div>
                      <div className="font-medium text-gray-900">
                        {selectedProduct.batchNumber}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Quantity</div>
                      <div className="font-medium text-gray-900">
                        {selectedProduct.quantity} units
                      </div>
                    </div>
                  </div>
                  <div className="pt-4">
                    <div className="text-sm text-gray-500 mb-1">Description</div>
                    <div className="text-gray-700">
                      {selectedProduct.description}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          <DialogFooter className="gap-2">
            {isEditing ? (
              <>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setIsEditing(false);
                    setEditFormData(selectedProduct || {});
                  }}
                >
                  Cancel
                </Button>
                <Button onClick={handleSaveEdit}>Save Changes</Button>
              </>
            ) : (
              <>
                <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                  Close
                </Button>
                <Button onClick={() => handleEditProduct(selectedProduct!)}>
                  Edit Product
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
