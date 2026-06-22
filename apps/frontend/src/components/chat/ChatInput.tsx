// apps/frontend/src/components/chat/ChatInput.tsx
'use client';

import { useRef, useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';

const MAX = 2000;

export function ChatInput() {
  const sendMessage = useChatStore((s) => s.sendMessage);
  const status = useChatStore((s) => s.status);

  const [value, setValue] = useState('');
  const ref = useRef<HTMLTextAreaElement>(null);

  const busy = status === 'waiting' || status === 'streaming';
  const tooLong = value.length > MAX;
  const canSend = value.trim().length > 0 && !tooLong && !busy;

  const resetHeight = () => {
    if (ref.current) ref.current.style.height = 'auto';
  };

  const submit = () => {
    if (!canSend) return;
    sendMessage(value);
    setValue('');
    resetHeight();
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const onInput = () => {
    const el = ref.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
  };

  return (
    <div className="border-t border-slate-200 p-3 bg-white">
      <div className="relative">
        <textarea
          ref={ref}
          rows={1}
          value={value}
          disabled={busy}
          onChange={(e) => setValue(e.target.value)}
          onInput={onInput}
          onKeyDown={onKeyDown}
          placeholder="Pregúntame algo…"
          className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:border-sky-400 focus:ring-1 focus:ring-sky-400 text-sm p-3 pr-12 outline-none disabled:opacity-60"
        />
        <button
          type="button"
          onClick={submit}
          disabled={!canSend}
          aria-label="Enviar"
          className="absolute right-2 bottom-2 w-8 h-8 rounded-lg bg-sky-600 text-white flex items-center justify-center disabled:opacity-40 active:scale-95 transition-transform"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
      <div
        className={`text-right text-[11px] mt-1 ${
          tooLong ? 'text-red-500' : 'text-slate-400'
        }`}
      >
        {value.length} / {MAX}
      </div>
    </div>
  );
}
