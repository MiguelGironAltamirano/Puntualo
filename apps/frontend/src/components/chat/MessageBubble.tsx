// apps/frontend/src/components/chat/MessageBubble.tsx
import { Bot } from 'lucide-react';
import { ChatMessage } from '@/lib/chat';

export function MessageBubble({
  message,
  streaming = false,
}: {
  message: ChatMessage;
  streaming?: boolean;
}) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center shrink-0">
          <Bot className="w-4 h-4 text-sky-600" />
        </div>
      )}
      <div
        className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm whitespace-pre-wrap break-words ${
          isUser
            ? 'bg-sky-600 text-white rounded-tr-sm'
            : 'bg-slate-100 text-slate-800 border border-slate-200 rounded-tl-sm'
        }`}
      >
        {message.content}
        {streaming && (
          <span className="inline-block w-1.5 h-4 ml-0.5 align-middle bg-sky-500 animate-pulse" />
        )}
      </div>
    </div>
  );
}
