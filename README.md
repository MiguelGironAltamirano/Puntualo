# Puntualo — Plataforma de Opiniones Docentes UNMSM

Puntualo es una plataforma web orientada a estudiantes de la Universidad Nacional Mayor de San Marcos que permite consultar, comparar y comentar sobre docentes universitarios mediante un sistema centralizado de reseñas, calificaciones y análisis de reputación académica.

La arquitectura del proyecto está basada en:

- Frontend: Next.js + TypeScript + TailwindCSS
- Backend: FastAPI + SQLAlchemy + Alembic
- Base de Datos: PostgreSQL
- Infraestructura Local: Docker + Docker Compose
- Monorepo: PNPM Workspace

---

# Estructura del Proyecto

```txt
puntualo-root/
├── apps/
│   ├── frontend/
│   └── backend/
├── packages/
├── docker-compose.yml
├── .gitignore
├── README.md
├── AGENTS.md
└── CLAUDE.md
```

---

# Tecnologías Principales

| Área | Tecnología |
|---|---|
| Frontend | Next.js 15 |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Migraciones | Alembic |
| Base de Datos | PostgreSQL 16 |
| Contenedores | Docker |
| Package Manager | PNPM |
| Estado Frontend | Zustand |
| Validaciones | Zod + Pydantic |

---

# Requisitos Previos

Instalar previamente:

- Node.js 20+
- PNPM
- Python 3.12+
- Docker Desktop
- Git

---

# Recomendaciones para Windows 11

- Docker Desktop con WSL2 habilitado
- Windows Terminal
- DataGrip o DBeaver para visualizar PostgreSQL

---

# Configuración Inicial del Proyecto

## 1. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
```

```bash
cd puntualo-root
```

---

# Configuración del Frontend

## 2. Instalar Dependencias Frontend

Ir al frontend:

```bash
cd apps/frontend
```

Instalar dependencias:

```bash
pnpm install
```

---

# Configuración del Backend

## 3. Crear Entorno Virtual Python

Ir al backend:

```bash
cd ../backend
```

## Windows PowerShell

Crear entorno virtual:

```powershell
python -m venv .venv
```

Activar entorno virtual:

```powershell
.\.venv\Scripts\activate
```

---

## 4. Instalar Dependencias Python

Con el entorno virtual activado:

```powershell
pip install -r requirements.txt
```

---

# Configuración Docker

## 5. Verificar Docker Desktop

Antes de iniciar PostgreSQL:

1. Abrir Docker Desktop.
2. Verificar que Docker esté corriendo.
3. Confirmar que WSL2 esté habilitado.

---

## 6. Verificar Archivo docker-compose.yml

Ubicación:

```txt
puntualo-root/docker-compose.yml
```

Contenido esperado:

```yaml
services:

  postgres:

    image: postgres:16

    container_name: puntualo_postgres

    restart: always

    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: puntualo_db

    ports:
      - "5432:5432"

    volumes:
      - puntualo_postgres_data:/var/lib/postgresql/data

volumes:
  puntualo_postgres_data:
```

---

## 7. Levantar PostgreSQL con Docker

Desde la raíz del proyecto:

```bash
docker compose up -d
```

---

## 8. Verificar Contenedores Activos

```bash
docker ps
```

Debe aparecer:

```txt
puntualo_postgres
```

y en la columna `PORTS`:

```txt
0.0.0.0:5432->5432/tcp
```

---

## 9. Verificar Logs PostgreSQL

```bash
docker logs puntualo_postgres
```

Debe aparecer:

```txt
database system is ready to accept connections
```

---

## 10. Verificar Conexión PostgreSQL Manualmente

Ejecutar:

```bash
docker exec -it puntualo_postgres psql -U admin -d puntualo_db
```

Si funciona correctamente aparecerá:

```txt
puntualo_db=#
```

Salir de PostgreSQL:

```sql
\q
```

---

# Variables de Entorno Backend

## 11. Crear Archivo `.env`

Ubicación:

```txt
apps/backend/.env
```

Contenido:

```env
DATABASE_URL=postgresql://admin:admin123@0.0.0.0:5432/puntualo_db

SECRET_KEY=change_this_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

# Configuración de Migraciones Alembic

## 12. Ejecutar Migraciones

Ir al backend:

```bash
cd apps/backend
```

Activar entorno virtual:

```powershell
.\.venv\Scripts\activate
```

Aplicar migraciones:

```powershell
alembic upgrade head
```

---

## 13. Verificar Migración Actual

```powershell
alembic current
```

---

## 14. Verificar Tablas PostgreSQL

Entrar al contenedor:

```bash
docker exec -it puntualo_postgres psql -U admin -d puntualo_db
```

Dentro de PostgreSQL ejecutar:

```sql
\dt
```

Deben aparecer tablas como:

```txt
users
alembic_version
```

Salir:

```sql
\q
```

---

# Ejecución del Backend

## 15. Levantar FastAPI en Desarrollo

Ubicación:

```txt
apps/backend
```

Activar entorno virtual:

```powershell
.\.venv\Scripts\activate
```

Ejecutar servidor:

```powershell
uvicorn app.main:app --reload
```

---

## 16. Verificar Backend

FastAPI estará disponible en:

```txt
http://127.0.0.1:8000
```

Swagger UI:

```txt
http://127.0.0.1:8000/docs
```

Redoc:

```txt
http://127.0.0.1:8000/redoc
```

---

# Ejecución del Frontend

## 17. Levantar Next.js

Ir al frontend:

```bash
cd apps/frontend
```

Ejecutar:

```bash
pnpm dev
```

---

## 18. Verificar Frontend

Frontend disponible en:

```txt
http://localhost:3000
```

---

# Acceso PostgreSQL desde DataGrip / DBeaver

## Configuración Recomendada

| Campo | Valor |
|---|---|
| Host | 0.0.0.0 |
| Port | 5432 |
| Database | puntualo_db |
| User | admin |
| Password | admin123 |

---

# Nota para Windows + WSL2

En algunos entornos Windows 11 + Docker + WSL2:

```txt
localhost
```

puede no resolver correctamente PostgreSQL.

Usar:

```txt
0.0.0.0
```

como host de conexión.

---

# Comandos Útiles

## Reiniciar PostgreSQL Docker

```bash
docker compose down
docker compose up -d
```

## Eliminar Base de Datos Local y Volúmenes

Advertencia: elimina todos los datos persistentes.

```bash
docker compose down -v
```

## Ver Logs PostgreSQL

```bash
docker logs puntualo_postgres
```

## Ver Contenedores Activos

```bash
docker ps
```

## Ver Volúmenes Docker

```bash
docker volume ls
```

## Ver Redes Docker

```bash
docker network ls
```

---

# Flujo General de Desarrollo

```txt
1. Crear rama feature/*
2. Implementar cambios
3. Ejecutar migraciones si aplica
4. Verificar backend y frontend
5. Commit
6. Pull Request
```

---

# Arquitectura Backend

Cada módulo backend sigue la estructura:

```txt
router.py
service.py
schemas.py
```

Separación de responsabilidades:

- `router.py`: endpoints HTTP
- `service.py`: lógica de negocio
- `schemas.py`: validaciones Pydantic

---

# Arquitectura Frontend

Separación entre:

- componentes UI reutilizables;
- componentes de negocio;
- estado global;
- validaciones compartidas.

---

# Equipo

| Integrante | Área |
|---|---|
| Miguel | Backend / Arquitectura |
| Ángel | Frontend |
| Mathias | Backend |
| Nicolas | Base de Datos |

---
