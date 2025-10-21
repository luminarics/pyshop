"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { API_BASE_URL } from "@/config";
import { useAuth } from "@/hooks/useAuth";
import type { Product } from "@/types";

interface UseProductsParams {
  page?: number;
  limit?: number;
}

interface PaginatedProductsResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

interface UseProductsReturn {
  products: Product[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
  total: number;
  page: number;
  totalPages: number;
}

// Fetch products with pagination
async function fetchProducts(
  token: string | null,
  page: number = 1,
  limit: number = 10
): Promise<PaginatedProductsResponse> {
  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(
    `${API_BASE_URL}/products/?skip=${(page - 1) * limit}&limit=${limit}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch products: ${response.statusText}`);
  }

  const data = await response.json();

  // Handle both paginated and non-paginated responses
  if (Array.isArray(data)) {
    return {
      products: data,
      total: data.length,
      page: 1,
      limit: data.length,
      totalPages: 1,
    };
  }

  return {
    products: data.products || data,
    total: data.total || 0,
    page: data.page || page,
    limit: data.limit || limit,
    totalPages: data.totalPages || Math.ceil((data.total || 0) / limit),
  };
}

export function useProducts(params: UseProductsParams = {}): UseProductsReturn {
  const { page = 1, limit = 10 } = params;
  const { token } = useAuth();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["products", page, limit],
    queryFn: () => fetchProducts(token, page, limit),
    enabled: !!token,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    products: data?.products || [],
    isLoading,
    error: error as Error | null,
    refetch,
    total: data?.total || 0,
    page: data?.page || page,
    totalPages: data?.totalPages || 1,
  };
}

// Hook for creating a product
export function useCreateProduct() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { name: string; price: number }): Promise<Product> => {
      if (!token) {
        throw new Error("Not authenticated");
      }

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

      return response.json();
    },
    onSuccess: () => {
      // Invalidate products queries to refetch
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });
}

// Hook for updating a product
export function useUpdateProduct() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: number;
      data: { name: string; price: number };
    }): Promise<Product> => {
      if (!token) {
        throw new Error("Not authenticated");
      }

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

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });
}

// Hook for deleting a product
export function useDeleteProduct() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      if (!token) {
        throw new Error("Not authenticated");
      }

      const response = await fetch(`${API_BASE_URL}/products/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to delete product");
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });
}
