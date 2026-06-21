// apps/frontend/src/lib/chat.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type ChatRole = 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  created_at?: string;
}

export class ChatError extends Error {
  status: number;
  code: string | null;
  constructor(status: number, code: string | null, message: string) {
    super(message);
    this.name = 'ChatError';
    this.status = status;
    this.code = code;
  }
}

function authHeaders(): Record<string, string> {
  const token =
    typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

async function toChatError(res: Response): Promise<ChatError> {
  const data = await res.json().catch(() => null);
  const code: string | null = data?.detail?.code ?? null;
  const message: string = data?.detail?.message ?? `Error ${res.status}`;
  return new ChatError(res.status, code, message);
}

export async function createSession(): Promise<string> {
  const res = await fetch(`${API_BASE_URL}/chat/sessions`, {
    method: 'POST',
    headers: authHeaders(),
  });
  if (!res.ok) throw await toChatError(res);
  const data = await res.json();
  return data.session_id as string;
}

export async function getMessages(sessionId: string): Promise<ChatMessage[]> {
  const res = await fetch(
    `${API_BASE_URL}/chat/sessions/${sessionId}/messages`,
    { headers: authHeaders() }
  );
  if (!res.ok) throw await toChatError(res);
  return (await res.json()) as ChatMessage[];
}

export interface StreamCallbacks {
  onChunk: (full: string) => void;
  onDone: (full: string) => void;
  onError: (e: ChatError) => void;
}

export async function streamMessage(
  sessionId: string,
  content: string,
  cb: StreamCallbacks
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(
      `${API_BASE_URL}/chat/sessions/${sessionId}/messages`,
      {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ content }),
      }
    );
  } catch {
    cb.onError(new ChatError(0, 'NETWORK', 'No se pudo conectar con el servidor.'));
    return;
  }

  if (!res.ok || !res.body) {
    cb.onError(await toChatError(res));
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let full = '';

  const handleLine = (raw: string): boolean => {
    // returns true if [DONE] reached
    const line = raw.replace(/\r$/, '');
    if (!line.startsWith('data:')) return false;
    const payload = line.slice(5).replace(/^ /, ''); // quita 1 espacio SSE
    if (payload === '[DONE]') return true;
    full += payload;
    cb.onChunk(full);
    return false;
  };

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? ''; // conserva la última línea (posiblemente parcial)
      for (const line of lines) {
        if (handleLine(line)) {
          cb.onDone(full);
          return;
        }
      }
    }
    // flush del remanente
    if (handleLine(buffer)) {
      cb.onDone(full);
      return;
    }
    cb.onDone(full);
  } catch {
    cb.onError(new ChatError(0, 'STREAM', 'Se interrumpió la respuesta.'));
  }
}
