# Chatbot RAG (Tarea 4.5) — Cómo debería verse la vista (spec frontend)

> **Audiencia:** quien implemente la UI del chatbot.
> **Stack actual:** Next.js 16 (App Router), React 19, Tailwind 4, zustand 5,
> `lucide-react` para iconos. Token en `useAuthStore`.
> **Contrato de API:** ver [`backend.md`](./backend.md). Esta es una **propuesta de
> diseño**, no una imposición; ajústala a lo que mejor encaje con el sistema de diseño
> existente.

---

## 1. Concepto

Un asistente conversacional que recomienda profesores. La interacción es la de un
chat clásico: lista de mensajes + caja de texto, con respuestas que aparecen
**token a token** (efecto "escribiendo") porque el backend transmite por streaming.

El bot **solo habla de temas académicos / profesores de Puntualo**, responde en
español y nunca inventa datos. La UI debe dejar clara esa expectativa (placeholder,
mensaje de bienvenida).

---

## 2. Punto de entrada

Recomendado: **botón flotante** (FAB) abajo a la derecha, presente en las vistas
autenticadas (catálogo de profesores, detalle, comparación).

```
                                            ┌──────────────┐
   … contenido de la página …               │  💬  Asistente│  ← FAB redondo
                                            └──────────────┘
```

- Solo visible para usuarios **autenticados y verificados** (el backend exige
  `is_verified`; si no lo está, mostrar un estado deshabilitado con tooltip
  "Verifica tu cuenta para usar el asistente").
- Alternativa/complemento: un ítem en el `Navbar`.

Al hacer clic abre el panel de chat.

---

## 3. Layout del panel

### Desktop — drawer lateral o panel anclado al FAB (~400px de ancho)

```
┌─────────────────────────────────────┐
│  Asistente Puntualo            ✕     │  ← header: título + cerrar
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │ 🤖 ¡Hola! Puedo recomendarte  │  │  ← mensaje assistant (izq.)
│  │    profesores. ¿Para qué curso│  │
│  │    buscas?                    │  │
│  └───────────────────────────────┘  │
│                                     │
│        ┌──────────────────────────┐ │
│        │ Quiero un profe de Cálculo│ │  ← mensaje user (der.)
│        └──────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ 🤖 Te recomiendo a ▌          │  │  ← respuesta en streaming
│  └───────────────────────────────┘  │
│                                     │
├─────────────────────────────────────┤
│ ┌─────────────────────────┐ ┌─────┐ │
│ │ Escribe tu pregunta...   │ │ ➤   │ │  ← input + enviar
│ └─────────────────────────┘ └─────┘ │
│            0 / 2000                  │  ← contador de caracteres
└─────────────────────────────────────┘
```

### Mobile — pantalla completa (drawer a pantalla completa o ruta `/chat`)

Mismo contenido, ocupando toda la pantalla, con el input fijo abajo (cuidado con el
teclado virtual: usar `dvh`/safe-area).

---

## 4. Componentes sugeridos

Siguiendo la convención del repo (`src/components/...`, hooks en `src/lib`, store en
`src/store`):

```
src/components/chat/
  ChatLauncher.tsx     # FAB / botón de apertura
  ChatPanel.tsx        # contenedor: header + lista + input
  MessageList.tsx      # render de mensajes + autoscroll
  MessageBubble.tsx    # burbuja individual (user / assistant)
  ChatInput.tsx        # textarea + contador + botón enviar
  TypingIndicator.tsx  # "escribiendo…" mientras llega el primer chunk
src/store/
  useChatStore.ts      # session_id, messages[], status
src/lib/
  chat.ts              # llamadas a /chat/* y parseo del stream SSE
```

---

## 5. Manejo del streaming (clave de UX)

El backend manda fragmentos de texto por SSE y un evento `done` al final
(ver `backend.md` §3.4 y §6). La UI debe:

1. Al enviar, **agregar inmediatamente** la burbuja del usuario y una burbuja vacía
   de assistant en estado "pensando" (mostrar `TypingIndicator`).
2. Con cada fragmento recibido, **append** al contenido de esa burbuja y re-render
   (efecto escribiendo). Mostrar un cursor `▌` mientras dure el stream.
3. Al recibir `[DONE]`, fijar el mensaje final y volver a habilitar el input.
4. Hacer **autoscroll** al final mientras llegan tokens (salvo que el usuario haya
   scrolleado hacia arriba manualmente).

> El mensaje del asistente lo **persiste el backend solo**; no hay que reenviarlo.
> Al reabrir el chat, rehidratar con `GET /chat/sessions/{id}/messages`.

Usar `fetch` + `ReadableStream`, **no** `EventSource` (el envío es `POST` con body).

---

## 6. Estados de la UI

| Estado            | Qué mostrar                                                        |
|-------------------|-------------------------------------------------------------------|
| Sin sesión        | Mensaje de bienvenida; crear sesión al primer envío o al abrir.   |
| Cargando historial| Skeleton de burbujas (reusar `SkeletonLoaders`).                  |
| Esperando 1er chunk| `TypingIndicator` ("Buscando profesores…").                      |
| Streaming         | Texto creciendo + cursor; input deshabilitado.                    |
| Listo             | Input habilitado, foco en el textarea.                            |
| Vacío (sin datos) | El bot responde honestamente "no encontré coincidencias" (texto). |
| Error             | Banner/burbuja de error con opción "Reintentar".                  |

---

## 7. Mapeo de errores a UX

Tomados de la tabla de `backend.md` §4:

| code                  | Mensaje sugerido al usuario                                        |
|-----------------------|-------------------------------------------------------------------|
| `RATE_LIMIT_EXCEEDED` | "Llegaste al límite de mensajes por esta hora. Intenta más tarde." |
| `USER_NOT_VERIFIED`   | "Verifica tu cuenta para usar el asistente." (idealmente bloquear antes) |
| `SESSION_NOT_FOUND`   | Recrear sesión silenciosamente (`POST /chat/sessions`) y reintentar. |
| `FORBIDDEN`           | Recrear sesión (la guardada no es del usuario actual).            |
| `401`                 | Redirigir a login / refrescar token.                              |
| `422`                 | Validación local: no enviar vacío ni > 2000 chars.               |

**Validación en el cliente:** deshabilitar "enviar" si el texto está vacío o supera
**2000 caracteres**; mostrar el contador (`n / 2000`).

---

## 8. Contenido y tono

- **Mensaje de bienvenida** (no viene del backend; ponlo en el cliente): algo como
  *"¡Hola! Soy el asistente de Puntualo. Puedo recomendarte profesores por curso,
  facultad o tema. ¿Qué buscas?"*
- **Sugerencias rápidas** (chips opcionales) para arrancar la conversación:
  *"Profe de Cálculo I"*, *"Compara dos profesores"*, *"Mejor puntuado de mi facultad"*.
- Las respuestas llegan como **texto plano en español**. Renderizar respetando saltos
  de línea. (No hay un renderer de markdown instalado; si se quiere formato, evaluar
  agregar uno, pero el backend hoy devuelve texto.)
- **Mejora futura (opcional):** el bot menciona nombres de profesores que existen en
  el catálogo. Se podría enriquecer detectando esos nombres y enlazándolos a
  `/teachers/[id]`. No es necesario para la primera versión; el bot devuelve texto, no
  tarjetas estructuradas.

---

## 9. Estilo visual

Alinear con el sistema actual (Tailwind 4, paleta `sky-*` ya usada en loaders):

- Burbujas usuario: fondo `sky-600`, texto blanco, alineadas a la derecha.
- Burbujas assistant: fondo `slate-100`/blanco con borde, alineadas a la izquierda.
- Iconos con `lucide-react` (ej. `MessageCircle`, `Send`, `X`, `Bot`).
- Bordes redondeados generosos (`rounded-2xl`) y sombras suaves como el resto de la app.

---

## 10. Accesibilidad

- El panel debe ser navegable por teclado; `Esc` cierra, `Enter` envía
  (`Shift+Enter` = salto de línea).
- `aria-live="polite"` en la lista de mensajes para que lectores de pantalla anuncien
  las respuestas en streaming.
- Foco gestionado: al abrir el panel, foco al input; al cerrar, devolver foco al FAB.
- Contraste suficiente en burbujas y estados deshabilitados.

---

## 11. Checklist de implementación

- [ ] FAB/entrada visible solo para usuarios verificados.
- [ ] Crear/recuperar `session_id` y persistirlo (store).
- [ ] Rehidratar historial con `GET /chat/sessions/{id}/messages`.
- [ ] Enviar mensaje y **renderizar el stream SSE** en vivo.
- [ ] Validación de longitud (1–2000) + contador.
- [ ] Manejo de los 6 estados (§6) y errores (§7).
- [ ] Autoscroll inteligente y cursor de "escribiendo".
- [ ] Responsive (drawer desktop / pantalla completa mobile) + accesibilidad.
```
