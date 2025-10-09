"use client";

import { ComponentType } from "react";
import { ProtectedRoute } from "./ProtectedRoute";

export interface WithAuthOptions {
  redirectTo?: string;
  loadingComponent?: React.ReactNode;
}

/**
 * Higher-order component that wraps a component with authentication protection
 *
 * @example
 * ```tsx
 * const ProtectedDashboard = withAuth(Dashboard);
 *
 * // With options
 * const ProtectedProfile = withAuth(Profile, {
 *   redirectTo: '/login?redirected=true'
 * });
 * ```
 */
export function withAuth<P extends object>(
  Component: ComponentType<P>,
  options?: WithAuthOptions
) {
  const WrappedComponent = (props: P) => {
    return (
      <ProtectedRoute redirectTo={options?.redirectTo}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };

  WrappedComponent.displayName = `withAuth(${Component.displayName || Component.name || "Component"})`;

  return WrappedComponent;
}
