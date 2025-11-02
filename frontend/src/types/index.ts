// Global type definitions
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
  description?: string;
  image_url?: string;
  stock: number;
  created_at: string;
  updated_at?: string;
}

export interface CartItem {
  id: string;
  product: Product;
  quantity: number;
  total: number;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}
