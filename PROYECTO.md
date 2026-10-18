# Life OS

> Segundo cerebro personal — uso individual, web + PWA.

## Stack

**Frontend** (`frontend/`, deploy en Vercel)
- **React 18 + Vite 5** (JSX, sin TypeScript)
- **Tailwind CSS 3** (dark por defecto, toggle a claro)
- **React Router v6** (rutas anidadas en módulos con sub-tabs)
- **Zustand** para estado UI global (theme, sidebar)
- **Recharts** (Line, Bar, Radar)
- **@hello-pangea/dnd** (drag & drop del kanban de Negocio)
- **framer-motion** (transiciones suaves de página y modales)
- **date-fns** + locale `es` (zona horaria local)
- **vite-plugin-pwa** (instalable, NetworkFirst para la API, CacheFirst para assets)

**Backend** (`backend/`, deploy en Railway)
- **FastAPI** + **Uvicorn**
- **SQLAlchemy 2** + **Alembic** sobre **MySQL** (driver PyMySQL)
- **pandas** para estadísticas (racha, cierre semanal)
- **uv** para dependencias; **pytest**, **ruff** y **mypy** (strict) para calidad

## Estructura

```
frontend/   App React + Vite (PWA)
backend/    API FastAPI: modelos, migraciones, routers, tests
database/   Scripts para la base MySQL local (setup_mysql.sh)
```

Dentro de `frontend/src/`:

```
components/        Componentes UI reutilizables (Button, Card, Modal, Badge, Tabs, Layout, Sidebar, BottomNav, EmptyState, PageHeader)
modules/
  dashboard/       Hábitos + rutina diaria/semanal + cierre semanal
  fisico/          Gym, MMA, Peso & Nutrición (sub-rutas)
  negocio/         Proyectos + Kanban + Ideas + Objetivos del mes
  mental/          Libros, Diario, Ideas/Frases, Estado (mood)
  finanzas/        Ingresos y gastos por mes
  analytics/       Score Bruce, radar, heatmap, barras semanales, peso
lib/               api (cliente HTTP), constants, dates helpers
store/             Zustand stores
hooks/             useAsync (queries declarativas con refetch)
styles/            index.css (Tailwind + utilities + tema claro)
```

Dentro de `backend/app/`: `models/` (ORM), `schemas/` (Pydantic), `routers/` (endpoints por módulo, bajo `/api`), `services/` (cálculos con pandas).

Cada módulo del frontend:
- `index.jsx` orquesta páginas/sub-rutas y carga data.
- `queries.js` encapsula las llamadas a la API del módulo.

## Convenciones

- **Fechas**: `yyyy-MM-dd` (fecha local del usuario) en la API. El frontend manda `today` cuando un cálculo depende del día actual, porque el servidor no conoce la zona horaria. Los timestamps se guardan en UTC y viajan con `Z`.
- **Colores de acento**: `#7F77DD` púrpura, `#1D9E75` teal, `#D85A30` coral. Categorías de rutina: gym=coral, mma=rojo, estudio=azul, negocio=púrpura, personal=teal.
- **Tipografía**: `DM Sans` (UI) y `Space Grotesk` (números/stats grandes), cargadas desde Google Fonts.
- **Cards**: `bg-ink-900` con borde `rgba(255,255,255,0.06)` y radio `rounded-xl`.
- **Mobile**: sidebar se reemplaza por bottom nav <768px.

## Setup local

1. Base: `./database/setup_mysql.sh` (crea base/usuario y escribe `backend/.env`).
2. Backend:
   ```bash
   cd backend
   uv sync
   uv run alembic upgrade head
   uv run uvicorn app.main:app --reload   # http://localhost:8000/docs
   ```
3. Frontend (`frontend/.env` con `VITE_API_URL=http://localhost:8000`):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Decisiones de arquitectura

- **Sin auth todavía**: uso de un solo usuario. Ver "Próximos pasos".
- **IDs UUID** (`CHAR(36)`) generados en Python; `days_of_week` y `tags` como columnas `JSON`.
- **Alembic es la fuente de verdad del schema**; las migraciones se aplican al arrancar el contenedor.
- **Cálculos**: racha y cierre semanal en el backend (pandas). Los de Stats siguen en `analytics/index.jsx` sobre `/api/analytics/data`.
- **Estado**: data local con `useAsync` (re-fetch on demand). Zustand sólo para UI global.

## Próximos pasos sugeridos

- **Autenticación** antes de exponer la API públicamente.
- Pasar los cálculos de Stats (Score Bruce, radar, heatmap) a pandas en el backend.
- Reemplazar PNGs placeholder por íconos reales (192/512).
- Code-splitting (`manualChunks`): Recharts es pesado.
