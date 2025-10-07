import React, { ReactElement } from 'react'
import { render, RenderOptions, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

// Enhanced providers wrapper for testing
interface ProvidersProps {
  children: React.ReactNode
  // Add any global providers here
  initialProps?: {
    theme?: 'light' | 'dark'
    locale?: string
  }
}

const AllTheProviders = ({ children }: ProvidersProps) => {
  // You can add theme providers, router providers, etc. here
  // Example:
  // return (
  //   <ThemeProvider theme={initialProps?.theme || 'light'}>
  //     <QueryClient client={queryClient}>
  //       {children}
  //     </QueryClient>
  //   </ThemeProvider>
  // )

  return <>{children}</>
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  providerProps?: ProvidersProps['initialProps']
}

const customRender = (
  ui: ReactElement,
  options?: CustomRenderOptions
) => {
  const { providerProps, ...renderOptions } = options || {}

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AllTheProviders children={children} {...(providerProps && { initialProps: providerProps })}>
    </AllTheProviders>
  )

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// re-export everything
export * from '@testing-library/react'
export { userEvent, screen, within }

// override render method
export { customRender as render }

// Enhanced testing utilities
export const renderWithUser = (ui: ReactElement, options?: CustomRenderOptions) => {
  return {
    user: userEvent.setup(),
    ...customRender(ui, options),
  }
}

// Common test utilities
export const createMockEvent = (overrides = {}) => ({
  preventDefault: vi.fn(),
  stopPropagation: vi.fn(),
  target: { value: '' },
  ...overrides,
})

export const createMockComponent = (name: string) => {
  const MockComponent = (props: any) => (
    <div data-testid={`mock-${name.toLowerCase()}`} {...props} />
  )
  MockComponent.displayName = `Mock${name}`
  return MockComponent
}

// Helper to test responsive breakpoints
export const mockBreakpoint = (breakpoint: string) => {
  const mediaQueries = {
    xs: '(min-width: 475px)',
    sm: '(min-width: 640px)',
    md: '(min-width: 768px)',
    lg: '(min-width: 1024px)',
    xl: '(min-width: 1280px)',
    '2xl': '(min-width: 1536px)',
  }

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: query === mediaQueries[breakpoint as keyof typeof mediaQueries],
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
}

// Helper to wait for async operations
export const waitForElement = async (callback: () => HTMLElement | null) => {
  return new Promise<HTMLElement>((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Element not found')), 5000)

    const checkElement = () => {
      const element = callback()
      if (element) {
        clearTimeout(timeout)
        resolve(element)
      } else {
        setTimeout(checkElement, 100)
      }
    }

    checkElement()
  })
}