"use client";

import { useState, useEffect, useCallback } from "react";
import { API_BASE_URL } from "@/config";
import { useAuth } from "@/hooks/useAuth";
import type { Product } from "@/types";

interface UseProductsReturn {
  products: Product[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useProducts(): UseProductsReturn {
  const { token } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = useCallback(async () => {
    if (!token) {
      setError("Not authenticated");
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/products/`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch products: ${response.statusText}`);
      }

      const data = await response.json();
      setProducts(Array.isArray(data) ? data : []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load products";
      setError(message);
      console.error("Error fetching products:", err);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  return {
    products,
    isLoading,
    error,
    refetch: fetchProducts,
  };
}

// Hook for creating a product
export function useCreateProduct() {
  const { token } = useAuth();
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createProduct = useCallback(
    async (data: { name: string; price: number }): Promise<Product | null> => {
      if (!token) {
        setError("Not authenticated");
        return null;
      }

      try {
        setIsCreating(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/products/`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          throw new Error("Failed to create product");
        }

        const product = await response.json();
        return product;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to create product";
        setError(message);
        return null;
      } finally {
        setIsCreating(false);
      }
    },
    [token]
  );

  return { createProduct, isCreating, error };
}

// Hook for updating a product
export function useUpdateProduct() {
  const { token } = useAuth();
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateProduct = useCallback(
    async (
      id: number,
      data: { name: string; price: number }
    ): Promise<Product | null> => {
      if (!token) {
        setError("Not authenticated");
        return null;
      }

      try {
        setIsUpdating(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/products/${id}`, {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          throw new Error("Failed to update product");
        }

        const product = await response.json();
        return product;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to update product";
        setError(message);
        return null;
      } finally {
        setIsUpdating(false);
      }
    },
    [token]
  );

  return { updateProduct, isUpdating, error };
}

// Hook for deleting a product
export function useDeleteProduct() {
  const { token } = useAuth();
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deleteProduct = useCallback(
    async (id: number): Promise<boolean> => {
      if (!token) {
        setError("Not authenticated");
        return false;
      }

      try {
        setIsDeleting(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/products/${id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to delete product");
        }

        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to delete product";
        setError(message);
        return false;
      } finally {
        setIsDeleting(false);
      }
    },
    [token]
  );

  return { deleteProduct, isDeleting, error };
}
