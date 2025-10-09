"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { ApiError } from "@/lib/api";

export function useRegister() {
  const { register } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (
    email: string,
    username: string,
    password: string,
    redirectTo: string = "/"
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      await register(email, username, password);
      toast.success("Registration successful! Welcome!");
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
    register: handleRegister,
    isLoading,
    error,
  };
}
