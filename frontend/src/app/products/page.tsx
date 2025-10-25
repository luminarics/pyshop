"use client";

import React, { useState } from "react";
import { ShoppingBag, RefreshCw, ArrowRight } from "lucide-react";
import Link from "next/link";
import { ProductGridLayout } from "@/components/products";
import { Button } from "@/components/ui/button";
import { useProducts } from "@/hooks/useProducts";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { toast } from "sonner";
import type { Product } from "@/types";
import { ResponsiveContainer, ResponsiveText } from "@/components/ui/responsive-grid";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { cartApi, ApiError } from "@/lib/api";
import { authStorage } from "@/lib/auth";

function ProductsPageContent() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const { products, isLoading, error, refetch, total, totalPages } = useProducts({
    page,
    limit: pageSize,
  });
  const queryClient = useQueryClient();
  const [cartItems, setCartItems] = useState<Map<number, number>>(new Map());

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setPage(1); // Reset to first page when changing page size
  };

  // Add to cart mutation
  const addToCartMutation = useMutation({
    mutationFn: async ({ productId, quantity }: { productId: number; quantity: number }) => {
      console.log("Mutation starting for product:", productId);
      const token = authStorage.getToken();
      console.log("Token exists:", !!token);
      if (!token) throw new Error("Not authenticated");
      return cartApi.addItem(token, { product_id: productId, quantity });
    },
    onSuccess: (data, variables) => {
      console.log("Add to cart successful:", data);
      const product = products.find((p) => p.id === variables.productId);
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      toast.success(`${product?.name || "Product"} added to cart`);

      // Update local state for UI
      setCartItems((prev) => {
        const newCart = new Map(prev);
        const currentQuantity = newCart.get(variables.productId) || 0;
        newCart.set(variables.productId, currentQuantity + variables.quantity);
        return newCart;
      });
    },
    onError: (error: Error) => {
      console.error("Add to cart error:", error);
      if (error instanceof ApiError) {
        toast.error(error.message);
      } else {
        toast.error("Failed to add item to cart");
      }
    },
  });

  const handleAddToCart = (product: Product) => {
    console.log("Add to cart clicked:", product);
    addToCartMutation.mutate({ productId: product.id, quantity: 1 });
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
            <>
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
              <Button size="sm" className="gap-2" asChild>
                <Link href="/cart">
                  View Cart
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            </>
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
        </div>
      </div>

      {/* Error State */}
      {error && !isLoading && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
          <div className="flex items-center gap-2">
            <div className="flex-1">
              <p className="font-semibold text-destructive">Error loading products</p>
              <p className="text-sm text-muted-foreground">{error.message}</p>
            </div>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </div>
      )}

      {/* Pagination Info */}
      {!isLoading && total > 0 && (
        <div className="mb-4 text-sm text-muted-foreground">
          Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} products
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
        showPagination={true}
        currentPage={page}
        totalPages={totalPages}
        onPageChange={handlePageChange}
        pageSize={pageSize}
        onPageSizeChange={handlePageSizeChange}
        total={total}
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
