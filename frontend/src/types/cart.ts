export enum CartStatus {
  ACTIVE = "active",
  ABANDONED = "abandoned",
  CONVERTED = "converted",
  EXPIRED = "expired",
}

export interface CartItemRead {
  id: string;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  created_at: string;
  updated_at: string;
}

export interface CartRead {
  id: string;
  user_id?: string;
  session_id?: string;
  status: CartStatus;
  items: CartItemRead[];
  created_at: string;
  updated_at: string;
  expires_at?: string;
}

export interface CartItemCreate {
  product_id: number;
  quantity: number;
}

export interface CartItemUpdate {
  quantity: number;
}

export interface CartSummary {
  total_items: number;
  total_price: number;
  item_count: number;
}
