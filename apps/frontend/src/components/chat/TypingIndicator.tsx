// apps/frontend/src/components/chat/TypingIndicator.tsx
import { Bot } from 'lucide-react';

export function TypingIndicator() {
  return (
    <div className="flex gap-2 justify-start">
      <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center shrink-0">
        <Bot className="w-4 h-4 text-sky-600" />
      </div>
      <div className="bg-slate-100 border border-slate-200 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
        <span className="text-xs text-slate-500">Buscando profesores</span>
        <span className="flex gap-1">
          <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
          <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
          <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
        </span>
      </div>
    </div>
  );
}
