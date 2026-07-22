/**
 * Pruebas del store global de autenticación (Zustand).
 *
 * Nivel:   Unitaria
 * Tipo:    Funcional
 * Técnica: Caja Blanca
 * Bajo prueba: store/useAuthStore.ts
 */
import { beforeEach, describe, expect, it } from 'vitest';

import { useAuthStore } from './useAuthStore';

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reinicia el estado entre pruebas.
    useAuthStore.setState({ isAnonymous: false, token: null });
  });

  it('arranca sin token y no anónimo', () => {
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.isAnonymous).toBe(false);
  });

  it('setToken guarda el token de sesión', () => {
    useAuthStore.getState().setToken('abc123');
    expect(useAuthStore.getState().token).toBe('abc123');

    useAuthStore.getState().setToken(null);
    expect(useAuthStore.getState().token).toBeNull();
  });

  it('toggleAnonymous alterna el modo anónimo', () => {
    expect(useAuthStore.getState().isAnonymous).toBe(false);
    useAuthStore.getState().toggleAnonymous();
    expect(useAuthStore.getState().isAnonymous).toBe(true);
    useAuthStore.getState().toggleAnonymous();
    expect(useAuthStore.getState().isAnonymous).toBe(false);
  });
});
