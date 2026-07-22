// apps/frontend/src/components/chat/markdown.ts
// Parser mínimo de markdown inline para los mensajes del chatbot.
// Solo cubre lo que el modelo emite en respuestas de chat: **negrita**,
// *cursiva*, `código` y viñetas al inicio de línea. Cualquier marcador
// sin cerrar (p. ej. a mitad de streaming) se deja como texto literal.

export type Segment =
  | { type: 'text'; content: string }
  | { type: 'bold'; content: string }
  | { type: 'italic'; content: string }
  | { type: 'code'; content: string };

const INLINE = /\*\*([^*\n]+)\*\*|\*([^*\s][^*\n]*)\*|`([^`\n]+)`/g;

export function parseInline(line: string): Segment[] {
  const segments: Segment[] = [];
  let last = 0;
  for (const match of line.matchAll(INLINE)) {
    if (match.index > last) {
      segments.push({ type: 'text', content: line.slice(last, match.index) });
    }
    if (match[1] !== undefined) {
      segments.push({ type: 'bold', content: match[1] });
    } else if (match[2] !== undefined) {
      segments.push({ type: 'italic', content: match[2] });
    } else {
      segments.push({ type: 'code', content: match[3] });
    }
    last = match.index + match[0].length;
  }
  if (last < line.length) {
    segments.push({ type: 'text', content: line.slice(last) });
  }
  return segments;
}

// Convierte viñetas markdown ("* item", "- item") en "• item".
export function normalizeBullet(line: string): string {
  return line.replace(/^(\s*)[*-]\s+/, '$1• ');
}
