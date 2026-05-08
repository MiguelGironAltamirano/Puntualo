import { create } from 'zustand';

// Definimos la forma de nuestros datos para TypeScript
interface AuthState {
    isAnonymous: boolean;
    token: string | null;
    toggleAnonymous: () => void;
    setToken: (token: string | null) => void;
}

// Creamos el store global
export const useAuthStore = create<AuthState>((set) => ({
    isAnonymous: false, // Inicia como no anónimo por defecto
    token: null,        // Al inicio no hay sesión activa
    toggleAnonymous: () => set((state) => ({ isAnonymous: !state.isAnonymous })),
    setToken: (token) => set({ token }),
}));