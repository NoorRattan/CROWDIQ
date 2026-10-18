import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    include: ['src/__tests__/unit/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      include: [
        'src/components/crowd/DensityBadge.tsx',
        'src/components/layout/EmergencyBanner.tsx',
        'src/components/order/OrderStatusTracker.tsx',
        'src/components/ui/Button.tsx',
        'src/components/ui/Badge.tsx',
        'src/hooks/useDebounce.ts',
        'src/hooks/useOrderStatus.ts',
      ],
      exclude: [
        'src/**/*.d.ts',
        'src/main.tsx',
        'src/vite-env.d.ts',
        'src/__tests__/**',
        'src/locales/**',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
      'jest-axe': path.resolve(import.meta.dirname, './src/test/jestAxeShim.ts'),
    },
  },
});
