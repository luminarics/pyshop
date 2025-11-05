import { useQuery } from "@tanstack/react-query";
import { cartApi } from "@/lib/api";
import { authStorage } from "@/lib/auth";
import { CartRead } from "@/types/cart";

export function useCartCount() {
  const { data: cart } = useQuery({
    queryKey: ["cart"],
    queryFn: async (): Promise<CartRead | null> => {
      const token = authStorage.getToken();
      if (!token) {
        return null;
      }
      try {
        return await cartApi.getCart(token);
      } catch (error) {
        // Return null on error (e.g., 401, network issues)
        return null;
      }
    },
    // Refetch every 30 seconds when the window is focused
    refetchOnWindowFocus: true,
    refetchInterval: 30000,
    // Don't retry on failure to avoid spamming the API
    retry: false,
  });

  const itemCount = cart?.items.reduce((sum, item) => sum + item.quantity, 0) || 0;

  return {
    itemCount,
    hasItems: itemCount > 0,
  };
}
