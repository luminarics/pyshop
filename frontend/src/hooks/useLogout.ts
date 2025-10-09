"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export function useLogout() {
  const { logout } = useAuth();
  const router = useRouter();

  const handleLogout = async (redirectTo: string = "/") => {
    try {
      await logout();
      toast.success("Logged out successfully");
      router.push(redirectTo);
    } catch (error) {
      console.error("Logout error:", error);
      toast.error("Logout failed, but you have been logged out locally");
      router.push(redirectTo);
    }
  };

  return {
    logout: handleLogout,
  };
}
