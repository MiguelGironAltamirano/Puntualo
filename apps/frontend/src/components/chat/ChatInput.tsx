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
      <div className="flex items-end gap-1.5 rounded-xl border border-slate-200 bg-slate-50 p-1.5 focus-within:bg-white focus-within:border-sky-400 focus-within:ring-1 focus-within:ring-sky-400">
        <textarea
          ref={ref}
          rows={1}
          value={value}
          disabled={busy}
          onChange={(e) => setValue(e.target.value)}
          onInput={onInput}
          onKeyDown={onKeyDown}
          placeholder="Pregúntame algo…"
          className="flex-1 resize-none bg-transparent text-sm p-1.5 outline-none disabled:opacity-60"
        />
        <button
          type="button"
          onClick={submit}
          disabled={!canSend}
          aria-label="Enviar"
          className="w-8 h-8 shrink-0 rounded-lg bg-sky-600 text-white flex items-center justify-center disabled:opacity-40 active:scale-95 transition-transform"
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
