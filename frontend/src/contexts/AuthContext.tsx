"use client";

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from "react";
import { authStorage } from "@/lib/auth";
import { authApi } from "@/lib/api";
import { isTokenExpired, isTokenExpiringSoon } from "@/lib/jwt";
import type { User } from "@/types/auth";

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Check token expiry every 60 seconds
const TOKEN_CHECK_INTERVAL = 60 * 1000;
// Refresh token if it expires in less than 5 minutes
const REFRESH_THRESHOLD = 5 * 60;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const tokenCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const logout = useCallback(async () => {
    const token = authStorage.getToken();

    // Clear interval
    if (tokenCheckIntervalRef.current) {
      clearInterval(tokenCheckIntervalRef.current);
      tokenCheckIntervalRef.current = null;
    }

    // Call backend logout endpoint
    if (token) {
      try {
        await authApi.logout(token);
      } catch (error) {
        console.error("Logout API call failed:", error);
      }
    }

    authStorage.removeToken();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    const token = authStorage.getToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    // Check if token is expired
    if (isTokenExpired(token)) {
      await logout();
      setIsLoading(false);
      return;
    }

    try {
      const userData = await authApi.getCurrentUser(token);
      setUser(userData);
    } catch (error) {
      // Token is invalid, clear it
      await logout();
    } finally {
      setIsLoading(false);
    }
  }, [logout]);

  const checkTokenExpiry = useCallback(async () => {
    const token = authStorage.getToken();
    if (!token) return;

    if (isTokenExpired(token)) {
      console.log("Token expired, logging out...");
      await logout();
      return;
    }

    // Note: FastAPI-Users doesn't provide token refresh by default
    // Tokens are short-lived (30 min) and users must re-login
    if (isTokenExpiringSoon(token, REFRESH_THRESHOLD)) {
      console.log("Token expiring soon. User will need to re-login after expiration.");
    }
  }, [logout]);

  // Initialize and start token check interval
  useEffect(() => {
    refreshUser();

    // Start checking token expiry periodically
    tokenCheckIntervalRef.current = setInterval(checkTokenExpiry, TOKEN_CHECK_INTERVAL);

    // Listen for unauthorized events from API client
    const handleUnauthorized = () => {
      console.log("Unauthorized event received, logging out...");
      logout();
    };

    window.addEventListener("auth:unauthorized", handleUnauthorized);

    return () => {
      if (tokenCheckIntervalRef.current) {
        clearInterval(tokenCheckIntervalRef.current);
      }
      window.removeEventListener("auth:unauthorized", handleUnauthorized);
    };
  }, [refreshUser, checkTokenExpiry, logout]);

  const login = useCallback(async (username: string, password: string) => {
    const response = await authApi.login({ username, password });
    authStorage.setToken(response.access_token);
    await refreshUser();
  }, [refreshUser]);

  const register = useCallback(async (email: string, username: string, password: string) => {
    await authApi.register({ email, username, password });
    // Auto-login after registration
    await login(email, password);
  }, [login]);

  const value: AuthContextType = {
    user,
    token: authStorage.getToken(),
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
