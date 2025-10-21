// Environment configuration
export const config = {
  // API Configuration
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    timeout: 10000,
  },

  // App Configuration
  app: {
    name: process.env.NEXT_PUBLIC_APP_NAME || "PyShop",
    version: process.env.NEXT_PUBLIC_APP_VERSION || "1.0.0",
    environment: process.env.NODE_ENV || "development",
  },

  // Authentication
  auth: {
    tokenKey: "auth_token",
    refreshTokenKey: "refresh_token",
    sessionTimeout: 30 * 60 * 1000, // 30 minutes
  },

  // Features flags
  features: {
    enableRegistration: process.env.NEXT_PUBLIC_ENABLE_REGISTRATION !== "false",
    enableGuestCheckout:
      process.env.NEXT_PUBLIC_ENABLE_GUEST_CHECKOUT === "true",
    enableAnalytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === "true",
  },

  // UI Configuration
  ui: {
    pagination: {
      defaultPageSize: 10,
      pageSizeOptions: [5, 10, 20, 50],
    },
    toast: {
      defaultDuration: 5000,
      position: "top-right" as const,
    },
  },
} as const;

// Export commonly used values
export const API_BASE_URL = config.api.baseUrl;

export default config;
