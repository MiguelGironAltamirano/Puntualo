import { defineConfig, devices } from '@playwright/test';
import path from 'node:path';

/**
 * Configuración de Playwright para las pruebas de aceptación (e2e) del frontend.
 *
 * - `testDir` apunta a los specs de este mismo paquete.
 * - `webServer` levanta el frontend Next.js (`next dev`) en el puerto 3000 antes
 *   de correr los tests y lo reutiliza si ya está corriendo (dev local).
 * - Las pruebas interceptan la red (`page.route`) hacia `/auth/login`, así son
 *   deterministas y NO dependen del backend ni de credenciales reales (aptas para CI).
 */
export default defineConfig({
  testDir: './specs',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'pnpm dev',
    cwd: path.resolve(__dirname, '../../frontend'),
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
  },
});
