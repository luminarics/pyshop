"use client";

import React, { useState } from "react";
import { ShoppingBag, Plus, RefreshCw } from "lucide-react";
import { ProductGridLayout } from "@/components/products";
import { Button } from "@/components/ui/button";
import { useProducts } from "@/hooks/useProducts";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { toast } from "sonner";
import type { Product } from "@/types";
import { ResponsiveContainer, ResponsiveText } from "@/components/ui/responsive-grid";

function ProductsPageContent() {
  const { products, isLoading, error, refetch } = useProducts();
  const [cartItems, setCartItems] = useState<Map<number, number>>(new Map());

  const handleAddToCart = (product: Product) => {
    setCartItems((prev) => {
      const newCart = new Map(prev);
      const currentQuantity = newCart.get(product.id) || 0;
      newCart.set(product.id, currentQuantity + 1);
      return newCart;
    });
    toast.success(`${product.name} added to cart`);
  };

  const handleUpdateQuantity = (product: Product, quantity: number) => {
    setCartItems((prev) => {
      const newCart = new Map(prev);
      if (quantity <= 0) {
        newCart.delete(product.id);
        toast.info(`${product.name} removed from cart`);
      } else {
        newCart.set(product.id, quantity);
      }
      return newCart;
    });
  };

  const totalItems = Array.from(cartItems.values()).reduce((sum, qty) => sum + qty, 0);
  const totalPrice = Array.from(cartItems.entries()).reduce((sum, [productId, qty]) => {
    const product = products.find((p) => p.id === productId);
    return sum + (product ? product.price * qty : 0);
  }, 0);

  return (
    <ResponsiveContainer size="2xl" className="py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <ResponsiveText as="h1" variant="h1" className="mb-2">
            Products
          </ResponsiveText>
          <p className="text-muted-foreground">
            Browse our collection of amazing products
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Cart Summary */}
          {totalItems > 0 && (
            <div className="flex items-center gap-2 rounded-lg border bg-card px-4 py-2">
              <ShoppingBag className="h-5 w-5 text-muted-foreground" />
              <div className="text-sm">
                <span className="font-semibold">{totalItems}</span> item
                {totalItems !== 1 ? "s" : ""}
                <span className="mx-1">·</span>
                <span className="font-semibold">
                  ${totalPrice.toFixed(2)}
                </span>
              </div>
            </div>
          )}

          {/* Refresh Button */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => refetch()}
            disabled={isLoading}
            aria-label="Refresh products"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>

          {/* Add Product Button (admin feature - placeholder) */}
          <Button variant="default">
            <Plus className="mr-2 h-4 w-4" />
            Add Product
          </Button>
        </div>
      </div>

      {/* Error State */}
      {error && !isLoading && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
          <div className="flex items-center gap-2">
            <div className="flex-1">
              <p className="font-semibold text-destructive">Error loading products</p>
              <p className="text-sm text-muted-foreground">{error}</p>
            </div>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </div>
      )}

      {/* Products Grid */}
      <ProductGridLayout
        products={products}
        isLoading={isLoading}
        onAddToCart={handleAddToCart}
        cartItems={cartItems}
        onUpdateQuantity={handleUpdateQuantity}
        showSearch={true}
        showSort={true}
        showFilters={true}
        emptyMessage={
          error
            ? "Unable to load products. Please try again."
            : "No products available at the moment."
        }
      />

      {/* Quick Stats (Optional) */}
      {!isLoading && products.length > 0 && (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Total Products</p>
            <p className="text-2xl font-bold">{products.length}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Average Price</p>
            <p className="text-2xl font-bold">
              ${(products.reduce((sum, p) => sum + p.price, 0) / products.length).toFixed(2)}
            </p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">In Cart</p>
            <p className="text-2xl font-bold">{totalItems}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Cart Total</p>
            <p className="text-2xl font-bold">${totalPrice.toFixed(2)}</p>
          </div>
        </div>
      )}
    </ResponsiveContainer>
  );
}

export default function ProductsPage() {
  return (
    <ProtectedRoute>
      <ProductsPageContent />
    </ProtectedRoute>
  );
}
