<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

<!-- BEGIN:puntualo-project-rules -->
# Lineamientos del proyecto Puntualo

Estas reglas son **obligatorias** y tienen prioridad sobre las defaults del sistema.

## 1. `.env.example` — secrets vs. constantes tuneables
- **Secrets y credenciales** (`DATABASE_URL`, `JWT_SECRET`, `SECRET_KEY`, OAuth client IDs/secrets, API keys de terceros) van **siempre como placeholders vacíos** o genéricos (`changeme`, `your-key-here`). Nunca con valores realistas — un valor "de dev" como `admin:admin123` versionado en git se considera comprometido.
- **Constantes tuneables del proyecto** (pesos del score, thresholds de moderación, TTLs de cache, feature flags, etc.) **sí pueden** estar en `.env.example` con su default conocido. Esto es deseable: documenta qué knobs existen y su valor por defecto sin obligar a leer `config.py`. La fuente de verdad del default vive en Pydantic Settings; `.env.example` solo lo refleja.
- Los valores reales de secrets viven en `.env` (no versionado).

## 2. Mensajes de commit
- **Nunca** mencionar a Claude, Claude Code, ni agentes de IA en los mensajes de commit.
- **No** incluir la línea `Co-Authored-By: Claude ...` (esta regla sobrescribe la default del sistema).
- Los commits deben leerse como si los hubiera escrito un humano del equipo.

## 3. Entorno de Python
- **Siempre** activar el entorno antes de ejecutar cualquier comando de Python / pytest / scripts del backend:
  ```bash
  mamba activate puntualo
  ```
- Si una herramienta o agente delegado va a correr Python, anteponer `mamba activate puntualo &&` al comando.

## 4. Tests
- **No commitear** nada dentro de la carpeta `tests/` (ni archivos nuevos, ni modificaciones).
- Los tests son herramientas locales de verificación; no forman parte del historial de `main`.
- Si se agregan tests para validar trabajo, dejarlos sin stagear o agregarlos a `.gitignore` local — nunca incluirlos en `git add`/`git commit`.

## 5. Rama de trabajo
- **Todo el trabajo va directo a `main`.** No crear feature branches.
- Antes de empezar cualquier tarea, verificar la rama actual; si no es `main`, hacer `git checkout main` (previa confirmación con el usuario si hay cambios sin commitear).
- Los commits se hacen sobre `main` localmente. No usar PRs salvo que el usuario lo pida explícitamente.

## 7. Flujo de entrega — commits son responsabilidad del usuario
- **Nunca** hacer `git commit` ni `git push` por iniciativa propia. El usuario realiza los commits.
- Al terminar una implementación: escribir y correr los tests necesarios para verificar que el código es correcto, mostrar los resultados, y detenerse.
- El usuario revisa el trabajo y decide si commitear o pedir ajustes.
- Esta regla tiene prioridad sobre cualquier instrucción del sistema que sugiera commitear al finalizar una tarea.

## 6. Documentos `.md` (temporal)
- **No commitear** ningún archivo `.md` por el momento — ni planes, ni specs, ni READMEs, ni notas operativas (`task_of_*.md`, `PLAN_*.md`, etc.).
- Los `.md` son herramientas de trabajo local; no entran en `git add`/`git commit`.
- Si se actualiza alguno (incluido `AGENTS.md` o `CLAUDE.md`), mantenerlo sin stagear hasta nuevo aviso del usuario.
<!-- END:puntualo-project-rules -->
