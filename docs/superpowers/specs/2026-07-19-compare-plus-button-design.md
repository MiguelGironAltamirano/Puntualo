# Botón "+" en cards de profesores → agregar a comparativa

**Fecha:** 2026-07-19 · **Estado:** aprobado por el usuario · **No commitear** (regla del proyecto: los `.md` no se versionan)

## Problema
El "+" en las cards del catálogo (`TeacherCatalog.tsx`) es un `div` decorativo. La página `/compare` mantiene su selección en `useState` local, que se pierde al navegar.

## Decisión (aprobada)
Al hacer click en "+", el profesor se agrega a la comparación y el usuario permanece en el catálogo (el botón pasa a ✓; click de nuevo lo quita). Un badge con el contador en el link "Comparativo" de la navbar da acceso a `/compare`.

## Diseño
- **`src/store/useCompareStore.ts`** (nuevo): store Zustand con `persist` (localStorage, key `puntualo-compare`, `skipHydration: true` + `rehydrate()` en efecto de los consumidores para evitar mismatch de hidratación). Estado: `selected: Teacher[]` (tipo de `components/compare/types`), máx. 4. Acciones: `toggle(teacher)`, `remove(id)`, `clear()`. Exporta también `mapProfessorToTeacher` (movido desde `compare/page.tsx`) y `MAX_COMPARE = 4`.
- **`TeacherCatalog.tsx`**: el "+" pasa a `button` real con `preventDefault`/`stopPropagation` (la card entera es un `Link`). Estado seleccionado → ícono ✓ y estilo activo; con 4 seleccionados y no incluido → deshabilitado con tooltip "Máximo 4 profesores". Al hacer toggle se usa el `ProfessorRead` original (los ids de la API son `string`; `TeacherSummary.id` está mal tipado como `number` — inconsistencia preexistente que no se toca).
- **`Navbar.tsx`**: badge numérico junto a "Comparativo" (desktop y menú móvil), visible solo si hay ≥1 seleccionado.
- **`compare/page.tsx`**: reemplaza el `useState` de `selectedTeachers` por el store (`selected`/`toggle`/`remove`/`clear`). El buscador interno y el fetch de comparación no cambian de lógica.

## Fuera de alcance
Backend, persistencia server-side, corrección del tipado de `TeacherSummary.id`.

## Verificación
`pnpm lint` (sin errores nuevos en archivos tocados) y `pnpm build`. El frontend no tiene suite de tests.
