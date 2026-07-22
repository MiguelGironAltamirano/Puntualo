import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';

/**
 * Configuración de Vitest para pruebas unitarias/render de componentes del frontend.
 *
 * - Entorno `jsdom` para renderizar componentes React sin navegador.
 * - Alias `@/` alineado con el de `tsconfig.json` (`./src`).
 * - `setupFiles` habilita los matchers de `@testing-library/jest-dom`.
 */
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
});
