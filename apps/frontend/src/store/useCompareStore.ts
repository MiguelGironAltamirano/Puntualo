import { useEffect } from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Teacher } from '@/components/compare/types';
import { ProfessorRead } from '@/lib/api';

export const MAX_COMPARE = 4;

/**
 * Maps API ProfessorRead to compare Teacher type. Las métricas detalladas
 * llegan después vía el endpoint de comparación; aquí solo lo básico.
 */
export function mapProfessorToTeacher(professor: ProfessorRead): Teacher {
    return {
        id: professor.id,
        name: professor.full_name,
        course: 'Ver en perfil',
        school: `${professor.total_evaluations} evaluaciones`,
        rating: professor.global_score ?? 0,
        difficulty: 3.0,
        clarity: 3.5,
        helpfulness: 3.5,
        punctuality: 4.0,
        takeAgain: '75%',
        avatar: '',
        tags: professor.validation_status === 'validated' ? ['Verificado'] : [],
        reviews: [],
        aiSummary: {
            pros: [],
            contras: []
        }
    };
}

interface CompareState {
    selected: Teacher[];
    toggle: (teacher: Teacher) => void;
    remove: (id: Teacher['id']) => void;
    clear: () => void;
}

// La selección de la comparativa se comparte entre el catálogo y /compare,
// y persiste en localStorage para sobrevivir navegación y recargas.
export const useCompareStore = create<CompareState>()(
    persist(
        (set) => ({
            selected: [],
            toggle: (teacher) => set((state) => {
                if (state.selected.some(t => t.id === teacher.id)) {
                    return { selected: state.selected.filter(t => t.id !== teacher.id) };
                }
                if (state.selected.length >= MAX_COMPARE) return state;
                return { selected: [...state.selected, teacher] };
            }),
            remove: (id) => set((state) => ({
                selected: state.selected.filter(t => t.id !== id),
            })),
            clear: () => set({ selected: [] }),
        }),
        {
            name: 'puntualo-compare',
            // El HTML se prerenderiza sin selección; hidratar en un efecto
            // (useCompareHydration) evita mismatch servidor/cliente.
            skipHydration: true,
        }
    )
);

// Rehidrata la selección desde localStorage tras el montaje. Idempotente:
// cada componente que lee del store la llama sin importar el orden.
export function useCompareHydration() {
    useEffect(() => {
        useCompareStore.persist.rehydrate();
    }, []);
}
