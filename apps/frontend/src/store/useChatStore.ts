// apps/frontend/src/store/useChatStore.ts
import { create } from 'zustand';
import {
  ChatMessage,
  ChatError,
  createSession,
  getMessages,
  streamMessage,
} from '@/lib/chat';

const SESSION_KEY = 'chat_session_id';

export type ChatStatus =
  | 'idle'
  | 'loading-history'
  | 'waiting'
  | 'streaming'
  | 'ready'
  | 'error';

interface ChatState {
  isOpen: boolean;
  sessionId: string | null;
  messages: ChatMessage[];
  status: ChatStatus;
  error: string | null;
  open: () => Promise<void>;
  close: () => void;
  sendMessage: (content: string, isRetry?: boolean) => Promise<void>;
  retry: () => void;
}

function messageForError(e: unknown): string {
  if (e instanceof ChatError) {
    if (e.code === 'RATE_LIMIT_EXCEEDED')
      return 'Llegaste al límite de mensajes por esta hora. Intenta más tarde.';
    if (e.code === 'USER_NOT_VERIFIED')
      return 'Verifica tu cuenta para usar el asistente.';
    if (e.status === 401) return 'Tu sesión expiró. Inicia sesión de nuevo.';
  }
  return 'Ocurrió un error. Intenta de nuevo.';
}

export const useChatStore = create<ChatState>((set, get) => ({
  isOpen: false,
  sessionId: null,
  messages: [],
  status: 'idle',
  error: null,

  open: async () => {
    set({ isOpen: true });
    if (get().status === 'loading-history') return;
    const { sessionId, messages } = get();
    const stored =
      sessionId ??
      (typeof window !== 'undefined'
        ? localStorage.getItem(SESSION_KEY)
        : null);
    if (stored && messages.length === 0) {
      set({ sessionId: stored, status: 'loading-history' });
      try {
        const history = await getMessages(stored);
        set({ messages: history, status: 'ready' });
      } catch {
        // sesión vieja / de otro usuario: descartarla y empezar limpio
        if (typeof window !== 'undefined') localStorage.removeItem(SESSION_KEY);
        set({ sessionId: null, status: 'idle' });
      }
    }
  },

  close: () => set({ isOpen: false }),

  sendMessage: async (raw, isRetry = false) => {
    const content = raw.trim();
    if (!content || content.length > 2000) return;
    const { status } = get();
    if (status === 'waiting' || status === 'streaming') return;

    // asegurar sesión
    let sessionId = get().sessionId;
    if (!sessionId) {
      try {
        sessionId = await createSession();
        if (typeof window !== 'undefined')
          localStorage.setItem(SESSION_KEY, sessionId);
        set({ sessionId });
      } catch (e) {
        if (e instanceof ChatError && e.status === 401) {
          window.location.href = '/login';
          return;
        }
        set({ status: 'error', error: messageForError(e) });
        return;
      }
    }

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
    };
    const assistantId = crypto.randomUUID();
    set((s) => ({
      messages: [
        ...s.messages,
        userMsg,
        { id: assistantId, role: 'assistant', content: '' },
      ],
      status: 'waiting',
      error: null,
    }));

    const updateAssistant = (text: string) =>
      set((s) => ({
        messages: s.messages.map((m) =>
          m.id === assistantId ? { ...m, content: text } : m
        ),
      }));

    await streamMessage(sessionId, content, {
      onChunk: (full) => {
        if (get().status !== 'streaming') set({ status: 'streaming' });
        updateAssistant(full);
      },
      onDone: (full) => {
        updateAssistant(full);
        set({ status: 'ready' });
      },
      onError: (err) => {
        // sesión inválida → recrear una vez y reintentar
        if (
          (err.code === 'SESSION_NOT_FOUND' || err.code === 'FORBIDDEN') &&
          !isRetry
        ) {
          if (typeof window !== 'undefined')
            localStorage.removeItem(SESSION_KEY);
          set((s) => ({
            sessionId: null,
            status: 'idle',
            messages: s.messages.filter(
              (m) => m.id !== assistantId && m.id !== userMsg.id
            ),
          }));
          void get().sendMessage(content, true);
          return;
        }
        if (err.status === 401) {
          window.location.href = '/login';
          return;
        }
        // quitar la burbuja vacía del asistente y mostrar el error
        set((s) => ({
          messages: s.messages.filter((m) => m.id !== assistantId),
          status: 'error',
          error: messageForError(err),
        }));
      },
    });
  },

  retry: () => {
    const { messages, status } = get();
    if (status !== 'error') return;
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (!lastUser) {
      set({ status: 'idle', error: null });
      return;
    }
    set((s) => ({
      messages: s.messages.filter((m) => m.id !== lastUser.id),
      status: 'idle',
      error: null,
    }));
    get().sendMessage(lastUser.content);
  },
}));
