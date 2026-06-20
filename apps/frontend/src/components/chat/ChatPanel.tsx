// apps/frontend/src/components/chat/ChatPanel.tsx
'use client';

import { useEffect, useRef } from 'react';
import { Bot, X } from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

export function ChatPanel() {
  const isOpen = useChatStore((s) => s.isOpen);
  const close = useChatStore((s) => s.close);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: globalThis.KeyboardEvent) => {
      if (e.key === 'Escape') close();
    };
    window.addEventListener('keydown', onKey);
    panelRef.current?.querySelector('textarea')?.focus();
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, close]);

  if (!isOpen) return null;

  return (
    <div
      ref={panelRef}
      role="dialog"
      aria-label="Asistente Puntualo"
      className="fixed inset-0 z-50 md:static md:inset-auto md:z-auto w-full md:w-[360px] md:shrink-0 h-full bg-white md:border-l border-slate-200 flex flex-col"
    >
      <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-sky-50">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-sky-600 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-bold text-sm text-slate-800">Asistente Puntualo</h2>
            <p className="text-[11px] text-sky-600 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
              En línea
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={close}
          aria-label="Cerrar"
          className="text-slate-400 hover:text-slate-600 p-1"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <MessageList />
      <ChatInput />
    </div>
  );
}
