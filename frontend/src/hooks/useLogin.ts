"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { ApiError } from "@/lib/api";

export function useLogin() {
  const { login } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (username: string, password: string, redirectTo: string = "/") => {
    setIsLoading(true);
    setError(null);

    try {
      await login(username, password);
      toast.success("Login successful!");
      router.push(redirectTo);
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : "An unexpected error occurred";
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    login: handleLogin,
    isLoading,
    error,
  };
}
