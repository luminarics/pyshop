"use client";

import { ComponentType } from "react";
import { GuestRoute } from "./GuestRoute";

export interface WithGuestOptions {
  redirectTo?: string;
}

/**
 * Higher-order component that wraps a component with guest-only access
 * Redirects authenticated users away from login/register pages
 *
 * @example
 * ```tsx
 * const GuestOnlyLogin = withGuest(LoginPage);
 *
 * // With options
 * const GuestOnlyRegister = withGuest(RegisterPage, {
 *   redirectTo: '/dashboard'
 * });
 * ```
 */
export function withGuest<P extends object>(
  Component: ComponentType<P>,
  options?: WithGuestOptions
) {
  const WrappedComponent = (props: P) => {
    return (
      <GuestRoute redirectTo={options?.redirectTo}>
        <Component {...props} />
      </GuestRoute>
    );
  };

  WrappedComponent.displayName = `withGuest(${Component.displayName || Component.name || "Component"})`;

  return WrappedComponent;
}
