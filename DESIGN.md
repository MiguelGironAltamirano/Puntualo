# DESIGN.md — Sistema de diseño de Puntualo

> Documento de referencia del lenguaje visual actual de Puntualo, extraído del código real
> (`apps/frontend`, Next.js 16 + React 19 + Tailwind v4). Sirve como base para **rediseñar y
> optimizar la landing page** sin romper la coherencia con el resto del producto.
>
> Estado actual: el diseño **no usa tokens**; los colores están hardcodeados como hex en clases
> Tailwind a lo largo de los componentes. Una de las metas de este documento es **consolidar esos
> valores en tokens** antes de rediseñar (ver §7).
>
> **Actualizado (2026-06):** pase de harden + audit (WCAG AA) + craft + polish sobre la landing.
> Resuelto: metadata real, `lang="es"`, fuente Geist (se quitó el `Arial` que la anulaba), foco
> visible en todos los CTAs, contraste AA. Nuevas secciones: barra de confianza en el hero,
> "Cómo funciona" y CTA final. Cambios reflejados abajo en §2–§9.

---

## 1. Personalidad de marca

Puntualo es una plataforma EdTech para que estudiantes universitarios elijan docentes con datos
(reseñas, métricas, síntesis por IA). El tono visual es:

- **Confiable y limpio** — fondos blancos, mucho espacio en blanco, sombras muy suaves.
- **Académico pero moderno** — azul cian como color de confianza/datos, naranja como energía/acción.
- **Datos sobre adornos** — tarjetas, métricas, badges; nada de ilustraciones pesadas.

Palabra clave de la landing: *"Decisiones académicas respaldadas por datos."*

---

## 2. Paleta de color

Frecuencia real de uso en `src/` (los más usados primero). Los nombres son la convención propuesta.

### Marca

| Token propuesto      | Hex        | Uso real                                              |
| -------------------- | ---------- | ---------------------------------------------------- |
| `--color-brand`      | `#0284c7`  | Logo "Puntualo", enlaces activos, acentos, íconos IA (sky-600) |
| `--color-brand-700`  | `#0369a1`  | Texto enfatizado dentro de tarjetas IA               |
| `--color-brand-600`  | `#0ea5e9`  | Variante clara (barras, "puntos a considerar")       |
| `--color-brand-900`  | `#004a7c` / `#0c4a6e` | Texto sobre fondos azul claro             |

### Acción (CTA)

| Token propuesto       | Hex        | Uso real                                             |
| --------------------- | ---------- | ---------------------------------------------------- |
| `--color-action`      | `#c2410c`  | **Fondo de botones con texto** ("Buscar", "Register", "Verificar"). Pasa AA con texto blanco (~5:1). |
| `--color-action-hover`| `#9a3412`  | Hover unificado del botón naranja                    |
| `--color-action-accent`| `#ff8a00` | Naranja brillante solo en usos **no-texto**: barras de comparación, glows. NO usar con texto encima (blanco da ~2.4:1, falla AA). |

> ✅ **Resuelto:** los dos hover (`#e67e00`/`#ea580c`) se unificaron a `#9a3412`. El naranja
> brillante `#ff8a00` quedó reservado para acentos no-texto; los botones usan `#c2410c` por contraste AA.

### Neutros (texto y superficies)

| Token propuesto        | Hex        | Uso real                                            |
| ---------------------- | ---------- | --------------------------------------------------- |
| `--color-ink`          | `#0f172a`  | Títulos (slate-900)                                 |
| `--color-ink-soft`     | `#1e293b` / `#334155` | Texto secundario fuerte                  |
| `--color-text`         | `#64748b`  | Cuerpo de texto (slate-500)                         |
| `--color-text-muted`   | `#94a3b8`  | Texto terciario, placeholders, copyright            |
| `--color-border`       | `#e2e8f0`  | Bordes de inputs/tarjetas (slate-200)               |
| `--color-surface`      | `#ffffff`  | Tarjetas, navbar                                    |
| `--color-surface-50`   | `#f8fafc`  | Footer, chips, fondos sutiles                       |
| `--color-surface-100`  | `#f1f5f9`  | Chips de íconos, badge "potenciado por IA"          |

### Acentos suaves (glows y fondos informativos)

| Token propuesto          | Hex        | Uso real                                          |
| ------------------------ | ---------- | ------------------------------------------------- |
| `--color-glow-blue`      | `#e0f2fe`  | Halos difuminados del hero, chip de ícono IA      |
| `--color-tint-blue`      | `#f0f9ff`  | Fondo de la caja "Síntesis IA", hover de botones outline |
| `--color-border-blue`    | `#bae6fd`  | Borde de botones outline secundarios              |

### Semánticos

| Estado    | Hex                                  | Uso                                        |
| --------- | ------------------------------------ | ------------------------------------------ |
| Éxito     | `#22c55e` / `#16a34a`                | Validaciones, métricas positivas           |
| Error     | `#ef4444` / `#f87171` / `#fca5a5`    | Errores, reportes, eliminar                |
| Aviso     | `#ff8a00` / `#fff7ed` / `#9a3412` / `#fed7aa` | Banner "cuenta no verificada"     |

---

## 3. Tipografía

- **Fuente:** `Geist` (Google Fonts, vía `next/font`), variable `--font-geist-sans`.
  - Mono: `Geist_Mono` (`--font-geist-mono`), apenas usada.
- ✅ **Resuelto:** `globals.css` ahora aplica `body { font-family: var(--font-geist-sans), ... }`.
  Se eliminó el `Arial` que anulaba Geist; la tipografía de marca se aplica de verdad en todo el body.

### Escala usada en la landing

| Rol               | Clases Tailwind                                          | Peso          |
| ----------------- | ------------------------------------------------------- | ------------- |
| H1 hero           | `text-4xl sm:text-5xl md:text-[3.5rem]` `tracking-tight` | `font-extrabold` |
| H2 sección        | `text-xl` / `text-4xl sm:text-5xl`                       | `font-extrabold` |
| H3 tarjeta        | `text-lg`                                                | `font-extrabold` |
| Subtítulo / lead  | `text-lg` (hero) / `text-sm sm:text-base`                | `font-medium` |
| Cuerpo            | `text-sm` `leading-relaxed`                              | `font-medium` |
| Botones           | `text-sm` / `text-xs`                                    | `font-bold`   |
| Labels / eyebrow  | `text-xs uppercase tracking-[0.2em]` o `tracking-[0.2em]` | `font-bold` |

**Regla de oro de la marca:** títulos en `font-extrabold` + `tracking-tight`; cuerpo en `font-medium`
(no `font-normal`). Es lo que da la sensación "densa y segura" del producto.

---

## 4. Forma, espaciado y elevación

- **Radios:**
  - `rounded-full` → píldoras: botones, badges, chips, input de búsqueda del hero, halos.
  - `rounded-2xl` → tarjetas y paneles.
  - `rounded-xl` → chips de ícono (10×10), dropdowns, cajas internas.
- **Sombras (muy suaves, marca registrada del look):**
  - Tarjeta base: `shadow-[0_4px_20px_rgb(0,0,0,0.03)]`, hover → `hover:shadow-md`.
  - Input hero: `shadow-[0_8px_30px_rgb(0,0,0,0.06)]`.
  - Tarjetas destacadas: `shadow-[0_8px_24px_rgb(0,0,0,0.05)]`.
- **Bordes:** `border border-gray-100` / `border-slate-200` en casi todo. Botones outline usan
  `border-2 border-[#bae6fd]`.
- **Contenedores:**
  - Navbar: `max-w-[1400px]`, alto fijo `h-[72px]`, `sticky top-0`, `bg-white/95 backdrop-blur-sm`.
  - Main de la landing: `max-w-[1000px] mx-auto`, padding `px-4 sm:px-6 lg:px-8`, `pt-20 pb-24`.
  - Footer: `max-w-6xl`.
- **Halos de fondo (hero):** dos círculos `bg-[#e0f2fe]` de ~500px con `blur-[100px]`, `opacity-50`,
  `pointer-events-none`, detrás del contenido (`z-0` vs `z-10`).

---

## 5. Componentes clave (catálogo real)

Ubicación: `apps/frontend/src/components/`.

| Componente            | Archivo                              | Rol en la landing |
| --------------------- | ------------------------------------ | ----------------- |
| `Navbar`              | `layout/Navbar.tsx`                  | Header sticky con logo, nav, buscador opcional, menú auth |
| `HeroSection`         | `home/HeroSection.tsx`               | Badge IA + H1 + lead + input píldora + tags + **microcopy del muro** + **barra de confianza** (señales reales) |
| `FeatureCards`        | `home/FeatureCards.tsx`              | Grid de 3 cards (IA, Comparativa, Filtros) |
| `HomeAISummary`       | `home/HomeAISummary.tsx`             | Card "Síntesis IA" con caja de consenso |
| `HowItWorks`          | `home/HowItWorks.tsx`                | **Nuevo.** 3 pasos numerados (Busca → Compara → Decide) |
| `FinalCTA`            | `home/FinalCTA.tsx`                  | **Nuevo.** Panel cian con CTA registro/login |
| Footer                | inline en `app/page.tsx`             | Logo + enlaces + copyright |

> **Foco visible:** patrón estándar en todos los interactivos →
> `focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2`
> (naranja usa `ring-orange-300`). Íconos-botón llevan `aria-label`.
>
> **Motion:** clase `.pl-reveal` (fade-up al cargar) definida en `globals.css`, envuelta en
> `@media (prefers-reduced-motion: no-preference)`; el contenido es visible por defecto. Hay además
> una red de seguridad global `@media (prefers-reduced-motion: reduce)`.

Otros componentes del producto (no landing, pero comparten lenguaje): `teachers/*` (catálogo,
modales de evaluar/reportar/registrar), `compare/*`, `chat/*`, `filters/*`, `pagination/*`,
`loaders/SkeletonLoaders.tsx`.

### Patrones de botón

```txt
CTA primario (naranja):   px-8 py-2 rounded-full bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold
Secundario (outline):     px-6 py-2.5 rounded-full border-2 border-[#bae6fd] text-[#0284c7] font-bold hover:bg-[#f0f9ff]
Chip / tag:               px-4 py-1.5 rounded-full bg-[#f8fafc] border border-gray-200 text-xs font-bold text-[#64748b]
Badge IA:                 px-4 py-1.5 rounded-full bg-[#f1f5f9] text-[#475569] text-xs font-semibold
```

### Iconografía

`lucide-react` con `strokeWidth={2.5}` (trazo grueso, consistente). Íconos típicos: `Search`,
`Lightbulb`, `Filter`, `AlignRight`, `Bell`, `User`, `MapPin`.

---

## 6. Anatomía actual de la landing (`app/page.tsx`)

La página tiene **3 estados** según sesión:

1. **`isCheckingSession`** → spinner textual "Cargando tu inicio…".
2. **Usuario logueado** → saludo personalizado + (banner de verificación si aplica) + 2 cards de acceso.
3. **Visitante (landing real)** → `Navbar` → halos → `HeroSection` (con barra de confianza) →
   `FeatureCards` → `HowItWorks` → `FinalCTA` → `footer`.

Flujo de conversión actual: **Hero search / tags / CTAs → `/login`** (el buscador requiere auth).
El muro ahora se **comunica** con microcopy ("Crea una cuenta gratis para buscar…") y el `FinalCTA`
empuja a `/register`. Pendiente decidir si se permite un preview sin login (opción A, no implementada).

---

## 7. Deuda de diseño a resolver antes/durante el rediseño

1. **Tokenizar colores.** ⏳ Pendiente (deuda #1). Hoy hay ~40 hex repetidos en clases. Definir tokens
   en `@theme` de `globals.css` (Tailwind v4) y reemplazar `bg-[#0284c7]` → `bg-brand`, etc. Requiere
   un barrido por **todo el producto** + regresión visual; no hacerlo a medias.
2. **Arreglar la fuente.** ✅ Hecho — `body` usa `var(--font-geist-sans)`.
3. **Unificar hovers.** ✅ Naranja unificado a `#9a3412`. ⏳ Cian (`#0284c7` vs `#0ea5e9`) sigue: son
   usos distintos (marca vs acentos de barra/datos), revisar si conviene unificar.
4. **Metadata real.** ✅ Hecho — `layout.tsx` con title/description/OpenGraph/Twitter reales,
   `metadataBase`, `viewport`+`themeColor` en su export separado (Next 16).
5. **Estados de color repetidos** (éxito/error con 2-3 hex cada uno) → ⏳ consolidar a un token por estado.
6. **Campana de notificaciones** (`Navbar`): ⏳ control sin acción (no hay feature de notificaciones);
   tiene `aria-label` pero falta decidir si se conecta o se quita.
7. **OG image + métricas reales:** ⏳ falta `opengraph-image` 1200×630 y, cuando exista endpoint
   público de conteos, números genuinos arriba del pliegue (no inventar métricas).

---

## 8. Lineamientos para el rediseño de la landing (optimización)

Objetivo declarado: **rediseñar la landing para optimizarla**. Mantener el ADN visual (azul confianza
+ naranja acción, tarjetas suaves, tipografía densa), mejorando conversión y claridad:

- **Conserva el sistema:** mismos tokens (§2), radios `rounded-full`/`rounded-2xl`, sombras suaves,
  `font-extrabold` en titulares. Cualquier propuesta nueva debe poder expresarse con estos tokens.
- **Jerarquía del hero:** un único CTA primario naranja dominante; el resto (tags, secundarios) en
  outline cian o chips. Evitar competir dos naranjas.
- **Prueba social / datos arriba del pliegue:** la marca vende "decisiones con datos" — considerar
  métricas reales o conteos (nº de docentes, reseñas) cerca del hero.
- **Fricción de auth:** hoy todo CTA lleva a `/login`. Evaluar permitir una búsqueda/preview sin
  login para reducir rebote, o comunicar claramente el valor antes del muro.
- **Secciones sugeridas** (orden de conversión): Hero → prueba social/métricas → "¿Por qué Puntualo?"
  (las 3 features, ya existentes) → cómo funciona (3 pasos) → CTA final de registro → footer.
- **Accesibilidad:** verificar contraste de `#64748b` sobre blanco para texto pequeño; el naranja
  `#ff8a00` sobre blanco en texto fino no pasa AA — usarlo solo en botones con texto blanco.
- **Responsive:** el patrón actual (`grid-cols-1 md:grid-cols-2`, `max-w-[1000px]`) funciona; mantener
  el contenedor centrado y los breakpoints `sm`/`md`/`lg` ya usados.

---

## 9. Referencia rápida (cheat sheet)

```txt
Marca:        #0284c7   Acción(botón): #c2410c  hover #9a3412   Acento naranja(no-texto): #ff8a00
Título:       #0f172a   Cuerpo:   #64748b   Tenue: #64748b (subido de #94a3b8 por AA)
Superficies:  #ffffff / #f8fafc / #f1f5f9   Borde: #e2e8f0
Tint azul:    #f0f9ff   Glow:     #e0f2fe    Borde azul: #bae6fd

Radios:   pill rounded-full · card rounded-2xl · chip rounded-xl
Sombra:   shadow-[0_4px_20px_rgb(0,0,0,0.03)]  (hover: shadow-md)
Tipo:     Geist · títulos font-extrabold tracking-tight text-balance · cuerpo font-medium
Iconos:   lucide-react · strokeWidth 2.5
Foco:     focus-visible:ring-2 ring-sky-400 ring-offset-2
Motion:   .pl-reveal (fade-up) bajo prefers-reduced-motion: no-preference
Layout:   main max-w-[1000px] · navbar max-w-[1400px] h-[72px] sticky
```
