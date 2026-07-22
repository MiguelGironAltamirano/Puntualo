/**
 * Prueba de aceptación end-to-end — flujo de autenticación en el frontend.
 *
 * Nivel:   Aceptación
 * Tipo:    Funcional
 * Técnica: Caja Negra
 * Objetivo: recorrer login -> validar credenciales -> redirigir, desde el navegador real.
 *
 * Runner: Playwright (config en ../playwright.config.ts). El frontend se levanta
 * con `next dev`. La llamada `/auth/login` se intercepta con `page.route`, de modo
 * que los casos son deterministas y no dependen del backend real ni de credenciales
 * (siguen el escenario aunque la VM esté caída). Trazable a PRUEBAS.md (Aceptación e2e).
 */
import { test, expect } from '@playwright/test';

const VALID_EMAIL = 'estudiante@unmsm.edu.pe';
const PASSWORD = 'Clave-Segura1';

// Localizadores robustos: los inputs no tienen label asociado por `for/id`,
// así que apuntamos por tipo/placeholder/rol (caja negra desde el DOM).
const emailInput = 'input[type="email"]';
const passwordInput = 'input[type="password"]';

test.describe('Autenticación (e2e)', () => {
  test('la página de login renderiza el formulario', async ({ page }) => {
    await page.goto('/login');

    await expect(page.locator(emailInput)).toBeVisible();
    await expect(page.locator(passwordInput)).toBeVisible();
    await expect(page.getByRole('button', { name: /acceder/i })).toBeVisible();
  });

  test('login inválido muestra mensaje de error', async ({ page }) => {
    // Backend responde 401 -> la UI debe mostrar el detalle de error.
    await page.route('**/auth/login', (route) =>
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Credenciales inválidas' }),
      }),
    );

    await page.goto('/login');
    await page.locator(emailInput).fill(VALID_EMAIL);
    await page.locator(passwordInput).fill('clave-incorrecta');
    await page.getByRole('button', { name: /acceder/i }).click();

    await expect(page.getByText(/credenciales inválidas/i)).toBeVisible();
    // No debe navegar fuera de /login.
    await expect(page).toHaveURL(/\/login$/);
  });

  test('login válido redirige al home autenticado (/teachers)', async ({ page }) => {
    // Backend responde 200 con tokens y rol student -> la UI redirige a /teachers.
    await page.route('**/auth/login', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'fake-access-token',
          refresh_token: 'fake-refresh-token',
          token_type: 'bearer',
          role: 'student',
        }),
      }),
    );
    // La página /teachers pide datos al backend; los stubbeamos vacíos para que
    // la navegación complete sin depender de la API real.
    await page.route(/\/(professors|evaluations|catalogs|hashtags)/, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0, page: 1, page_size: 20 }),
      }),
    );

    await page.goto('/login');
    await page.locator(emailInput).fill(VALID_EMAIL);
    await page.locator(passwordInput).fill(PASSWORD);
    await page.getByRole('button', { name: /acceder/i }).click();

    await page.waitForURL('**/teachers', { timeout: 15_000 });
    await expect(page).toHaveURL(/\/teachers/);
  });
});
