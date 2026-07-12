// apps/frontend/src/components/chat/MessageList.tsx
'use client';

import { useEffect, useRef } from 'react';
import { useChatStore } from '@/store/useChatStore';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { SkeletonList } from '@/components/loaders/SkeletonLoaders';

const WELCOME =
  '¡Hola! Soy el asistente de Puntualo. Puedo recomendarte profesores por curso, facultad o tema. ¿Qué buscas?';

export function MessageList() {
  const messages = useChatStore((s) => s.messages);
  const status = useChatStore((s) => s.status);
  const error = useChatStore((s) => s.error);
  const retry = useChatStore((s) => s.retry);

  const containerRef = useRef<HTMLDivElement>(null);
  const stick = useRef(true);

  const onScroll = () => {
    const el = containerRef.current;
    if (!el) return;
    stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
  };

  useEffect(() => {
    const el = containerRef.current;
    if (stick.current && el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
  }, [messages, status]);

  if (status === 'loading-history') {
    return (
      <div className="flex-1 overflow-y-auto p-4">
        <SkeletonList count={3} />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      onScroll={onScroll}
      aria-live="polite"
      className="flex-1 overflow-y-auto p-4 space-y-4"
    >
      {messages.length === 0 && (
        <MessageBubble
          message={{ id: 'welcome', role: 'assistant', content: WELCOME }}
        />
      )}

      {messages.map((m, i) => {
        if (m.role === 'assistant' && m.content === '') return null;
        const isLast = i === messages.length - 1;
        return (
          <MessageBubble
            key={m.id}
            message={m}
            streaming={isLast && status === 'streaming' && m.role === 'assistant'}
          />
        );
      })}

      {status === 'waiting' && <TypingIndicator />}

      {status === 'error' && error && (
        <div className="flex flex-col items-start gap-2">
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-2xl px-3 py-2">
            {error}
          </div>
          <button
            onClick={retry}
            className="text-xs font-bold text-sky-600 hover:underline"
          >
            Reintentar
          </button>
        </div>
      )}
    </div>
  );
}
