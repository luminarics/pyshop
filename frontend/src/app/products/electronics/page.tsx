"use client";

import React, { useState } from "react";
import { Cpu, ShoppingBag, RefreshCw, ArrowRight } from "lucide-react";
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

function ElectronicsProductsContent() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const { products, isLoading, error, refetch, total, totalPages } = useProducts({
    page,
    limit: pageSize,
    category: "electronics",
  });
  const queryClient = useQueryClient();
  const [cartItems, setCartItems] = useState<Map<number, number>>(new Map());

  // Filter for electronics products (adjust based on your category field)
  // For now, we'll show all products. You can add category filtering when you implement categories
  const electronicsProducts = products;

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setPage(1);
  };

  const addToCartMutation = useMutation({
    mutationFn: async ({ productId, quantity }: { productId: number; quantity: number }) => {
      const token = authStorage.getToken();
      if (!token) throw new Error("Not authenticated");
      return cartApi.addItem(token, { product_id: productId, quantity });
    },
    onSuccess: (_data, variables) => {
      const product = electronicsProducts.find((p) => p.id === variables.productId);
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      toast.success(`${product?.name || "Product"} added to cart`);

      setCartItems((prev) => {
        const newCart = new Map(prev);
        const currentQuantity = newCart.get(variables.productId) || 0;
        newCart.set(variables.productId, currentQuantity + variables.quantity);
        return newCart;
      });
    },
    onError: (error: Error) => {
      if (error instanceof ApiError) {
        toast.error(error.message);
      } else {
        toast.error("Failed to add item to cart");
      }
    },
  });

  const handleAddToCart = (product: Product) => {
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
    const product = electronicsProducts.find((p) => p.id === productId);
    return sum + (product ? product.price * qty : 0);
  }, 0);

  return (
    <ResponsiveContainer size="2xl" className="py-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <Cpu className="h-8 w-8 text-blue-500" />
            <ResponsiveText as="h1" variant="h1">
              Electronics
            </ResponsiveText>
          </div>
          <p className="text-muted-foreground">
            Explore the latest gadgets and electronic devices
          </p>
        </div>

        <div className="flex items-center gap-4">
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
          Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} electronics products
        </div>
      )}

      {/* Products Grid */}
      <ProductGridLayout
        products={electronicsProducts}
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
        emptyMessage="No electronics products available at the moment."
      />
    </ResponsiveContainer>
  );
}

export default function ElectronicsProductsPage() {
  return (
    <ProtectedRoute>
      <ElectronicsProductsContent />
    </ProtectedRoute>
  );
}
