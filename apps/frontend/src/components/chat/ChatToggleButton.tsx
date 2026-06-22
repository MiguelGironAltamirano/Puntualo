'use client';

import { Bot } from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';

export function ChatToggleButton() {
  const isOpen = useChatStore((s) => s.isOpen);
  const open = useChatStore((s) => s.open);

  if (isOpen) return null;

  return (
    <button
      id="chat-assistant-toggle"
      type="button"
      onClick={() => open()}
      aria-label="Abrir asistente IA"
      className="fixed z-40 bottom-6 right-6 flex items-center gap-2 px-4 py-3 rounded-full bg-sky-600 hover:bg-sky-700 text-white font-bold text-sm shadow-lg shadow-sky-500/20 active:scale-95 transition-all cursor-pointer"
    >
      <Bot aria-hidden="true" className="w-4 h-4" />
      <span className="hidden md:inline">Asistente IA</span>
    </button>
  );
}
