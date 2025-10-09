"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

interface GuestRouteProps {
  children: React.ReactNode;
  redirectTo?: string | undefined;
}

/**
 * GuestRoute component prevents authenticated users from accessing pages
 * like login and register, redirecting them to a specified page instead.
 */
export function GuestRoute({ children, redirectTo = "/" }: GuestRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, redirectTo, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // If user is authenticated, don't render children (they'll be redirected)
  if (isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
