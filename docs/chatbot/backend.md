# Chatbot RAG (Tarea 4.5) — Cómo funciona el backend

> **Audiencia:** equipo frontend que va a integrar la funcionalidad de chat.
> **Base URL (dev):** `http://localhost:8000`
> **Prefijo del módulo:** `/chat` (no hay prefijo global tipo `/api/v1`, igual que el resto del proyecto).

---

## 1. Resumen en una frase

Un asistente que **recomienda profesores de Puntualo** a partir de los datos del
sistema. El usuario manda un mensaje y el backend responde **en streaming (SSE)**,
token a token, usando RAG (retrieval) + *function calling* sobre Gemini.

El bot **solo usa datos reales** del sistema (profesores validados, resúmenes IA,
puntajes). No inventa profesores ni cursos, responde en español y redirige
cortésmente si la pregunta no es académica.

---

## 2. Autenticación y requisitos

Todos los endpoints requieren JWT en el header:

```
Authorization: Bearer <access_token>
```

Además, **el usuario debe estar verificado** (`is_verified = true`). Si no lo está,
cualquier endpoint del chat responde:

```
403 { "detail": { "code": "USER_NOT_VERIFIED", "message": "El usuario debe estar verificado..." } }
```

Sin token válido → `401`.

---

## 3. Endpoints

### 3.1 Abrir una sesión

```
POST /chat/sessions
→ 201
{ "session_id": "uuid-string" }
```

Crea una sesión de chat para el usuario autenticado. Guarda el `session_id`; lo
necesitas para todo lo demás.

---

### 3.2 Listar historial de una sesión

```
GET /chat/sessions/{session_id}/messages
→ 200
[
  { "id": "uuid", "role": "user",      "content": "...", "created_at": "2026-06-14T..." },
  { "id": "uuid", "role": "assistant", "content": "...", "created_at": "2026-06-14T..." }
]
```

Devuelve **todos** los mensajes de la sesión en orden cronológico (ascendente).
Útil para rehidratar el chat al recargar o reabrir una conversación.

- `role` es `"user"` o `"assistant"`.
- Solo puedes ver sesiones **propias** (ver errores abajo).

---

### 3.3 Cerrar una sesión

```
DELETE /chat/sessions/{session_id}
→ 204 (sin body)
```

Marca la sesión como terminada (`ended_at`). No borra los mensajes; el historial
sigue consultable.

---

### 3.4 Enviar un mensaje (respuesta en streaming SSE) ⭐

Este es el endpoint principal.

```
POST /chat/sessions/{session_id}/messages
Content-Type: application/json

{ "content": "¿Qué profe me recomiendas para Cálculo I?" }
```

- `content`: string, **obligatorio**, entre **1 y 2000 caracteres**.
- **Respuesta:** `Content-Type: text/event-stream` (Server-Sent Events).

#### Formato del stream

El backend emite varios eventos `data:` con **fragmentos de texto plano** de la
respuesta, y al final un evento `done`:

```
data: Hola, para Cálculo I

data:  te recomiendo a la profesora

data:  Juana Pérez porque...

event: done
data: [DONE]
```

El frontend debe **concatenar** todos los `data:` en orden para reconstruir la
respuesta completa, e ir renderizándola en vivo (efecto "escribiendo"). El evento
`done` con payload `[DONE]` indica que terminó.

> **Importante:** el mensaje del usuario se persiste **antes** de empezar el stream,
> y el mensaje del asistente se persiste **automáticamente en el backend** cuando el
> stream termina. El frontend **no** necesita reenviar nada para guardar la respuesta.

#### Rate limit

Límite de **30 mensajes por hora por usuario** (ventana deslizante de 1h, contada en
Redis). Al excederlo:

```
429 { "detail": { "code": "RATE_LIMIT_EXCEEDED", "message": "Has alcanzado el límite de mensajes por hora" } }
```

---

## 4. Tabla de errores

| HTTP | code                  | Cuándo ocurre                                         |
|------|-----------------------|------------------------------------------------------|
| 401  | —                     | Falta token o es inválido                             |
| 403  | `USER_NOT_VERIFIED`   | El usuario no está verificado                         |
| 403  | `FORBIDDEN`           | La sesión pertenece a **otro** usuario               |
| 404  | `SESSION_NOT_FOUND`   | El `session_id` no existe                             |
| 429  | `RATE_LIMIT_EXCEEDED` | Más de 30 mensajes en la última hora                 |
| 422  | —                     | `content` vacío o > 2000 chars (validación Pydantic)  |

Todos los errores de dominio vienen como `{ "detail": { "code", "message" } }`.

---

## 5. Qué pasa por dentro (contexto, no hace falta para integrar)

Cuando llega un mensaje, el orquestador hace:

1. **Retrieval semántico** — embebe la pregunta con **Cohere `embed-v4.0` (1536 dims)**
   y busca los profesores más cercanos por `pgvector` (distancia coseno) sobre
   `professor_embeddings`. Si no hay embeddings o Cohere falla, **degrada** a una
   búsqueda textual `ILIKE` sobre el resumen IA. Trae hasta `TOP_K = 5` profesores.
2. **Construye el contexto** — nombres, facultad, puntaje, resumen IA y hashtags de
   esos profesores, más los últimos **10 turnos** de la conversación.
3. **Loop de function calling** (máx. 4 rondas) — el modelo Gemini
   (`gemini-2.5-flash`) puede llamar tools que consultan la BD:
   - `search_professors(query, course_id?, faculty_id?)` → lista breve de profes validados.
   - `get_professor_details(professor_id)` → detalle + resumen IA + cursos + puntajes.
   - `compare_professors(professor_ids[])` → comparación por métricas/categorías.
4. **Stream final** — el modelo redacta la respuesta y se transmite por SSE.

> Las tools **nunca** exponen identidad de los autores de comentarios ni `user_id`.
> Solo trabajan con profesores `validation_status = "validated"`.

### Config relevante (variables de entorno)

| Variable                          | Default            | Significado                          |
|-----------------------------------|--------------------|--------------------------------------|
| `GEMINI_MODEL`                    | `gemini-2.5-flash` | Modelo de chat                       |
| `COHERE_EMBED_MODEL`              | `embed-v4.0`       | Modelo de embeddings                 |
| `COHERE_EMBED_DIM`                | `1536`             | Dimensión de embeddings              |
| `CHATBOT_TOP_K`                   | `5`                | Profes recuperados por consulta      |
| `CHATBOT_HISTORY_TURNS`           | `10`               | Turnos de historial enviados al LLM  |
| `CHATBOT_MAX_TOOL_ROUNDS`         | `4`                | Rondas máx. de function calling      |
| `CHATBOT_RATE_LIMIT_PER_HOUR`     | `30`               | Mensajes por hora por usuario        |
| `CHATBOT_SYSTEM_PROMPT_VERSION`   | `system_v1`        | Versión del system prompt            |

---

## 6. Ejemplo de consumo del stream (referencia)

```ts
async function sendMessage(sessionId: string, content: string, token: string) {
  const res = await fetch(`/chat/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ content }),
  });

  if (res.status === 429) throw new Error("RATE_LIMIT");
  if (!res.ok || !res.body) throw new Error("CHAT_ERROR");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let full = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    const text = decoder.decode(value, { stream: true });

    // Parseo simple de SSE: líneas que empiezan con "data:"
    for (const line of text.split("\n")) {
      if (!line.startsWith("data:")) continue;
      const payload = line.slice(5).trimStart();
      if (payload === "[DONE]") return full;
      full += payload;           // concatenar fragmento
      onChunk(full);             // re-render incremental
    }
  }
  return full;
}
```

> Nota: usa `fetch` + `ReadableStream` (no la API nativa `EventSource`), porque
> `EventSource` solo soporta `GET` y aquí el envío es `POST` con body.

---

## 7. Flujo típico desde el frontend

1. Al abrir el chat → `POST /chat/sessions` → guardar `session_id`.
2. (Opcional) `GET /chat/sessions/{id}/messages` para rehidratar historial.
3. Por cada mensaje del usuario → `POST /chat/sessions/{id}/messages` y renderizar
   el stream en vivo.
4. Al cerrar/limpiar la conversación → `DELETE /chat/sessions/{id}` (opcional).
