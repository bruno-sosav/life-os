# Life OS

Mi segundo cerebro: una app web instalable (PWA) donde organizo mi rutina, mis entrenamientos, lo que estoy aprendiendo, mis finanzas y los proyectos de mi emprendimiento. La uso todos los días desde el celu y la compu.

Es un proyecto full stack hecho de punta a punta: una **API en Python (FastAPI + MySQL)** con la lógica y las estadísticas, y un **frontend en React** que solo muestra y pide datos.

## Qué hace

| Sección | Qué tiene |
|---|---|
| **Hoy** | Agenda del día con hábitos y bloques de rutina, racha de días cumplidos, ánimo y horas de sueño, y un cierre semanal. |
| **Físico** | Registro de entrenamientos por tipo (gym, calistenia, correr…) con campos propios y ejercicios, progresión de cada ejercicio con su récord, calendario del mes, peso con meta y nutrición. |
| **Mental** | Skills que estoy aprendiendo, con práctica en minutos, meta semanal y recursos, más listas libres para tachar (compras, películas, cosas para aprender). |
| **Negocio** | Tablero tipo Trello por proyecto (Pendiente / En proceso / Finalizado) con arrastrar y soltar, ideas y objetivos del mes. |
| **Finanzas** | Ingresos y gastos por mes, con ahorro, gasto por categoría y categorías libres. |
| **Stats** | Calendario de cumplimiento, % semanal de las últimas 12 semanas, hábitos y práctica por semana, perfil semanal, distribución de entrenamientos y peso. |

## Stack

**Backend:** Python 3.13 · FastAPI · SQLAlchemy 2 · Alembic · MySQL · pandas · Pydantic · JWT + Argon2 · uv · pytest · ruff · mypy (strict)

**Frontend:** React 18 · Vite · Tailwind CSS · React Router · Zustand · Recharts · framer-motion · @hello-pangea/dnd · PWA (Workbox)

**Deploy:** backend y base de datos en Railway (Docker), frontend en Vercel.

## Arquitectura

```
backend/    API FastAPI
frontend/   App React (PWA)
database/   Script para crear la base MySQL local
```

### Backend: módulos con capas MVC

La API está dividida en 8 módulos de negocio: `rutina`, `dashboard`, `fisico`, `mental`, `negocio`, `finanzas`, `analytics` y `auth`. Cada uno tiene sus capas separadas, con un archivo por tema:

```
app/
  core/                    configuración, base de datos, seguridad y utilidades compartidas
  modules/
    fisico/
      controllers/         endpoints HTTP (sesiones_controller.py, peso_controller.py…)
      schemas/             validación de entrada y salida con Pydantic
      services/            reglas de negocio
      repositories/        consultas a la base
      models/              tablas de SQLAlchemy
      __init__.py          fachada: lo único que pueden importar los otros módulos
```

- **El flujo siempre es** controller → service → repository. Los controllers no tienen lógica y los repositories no tienen reglas.
- **Los módulos se hablan solo por su fachada** (`__init__.py`). Por ejemplo, Físico y Mental marcan el hábito vinculado de Rutina con `rutina.mark_linked_habit`, sin tocar sus tablas.
- **Los cálculos viven en el backend.** La racha, el cumplimiento semanal y las estadísticas se calculan con pandas. El frontend no calcula nada: muestra lo que devuelve la API.

### Frontend: features y shared

```
src/
  app/                     arranque, rutas y layout (barra lateral, barra de abajo en el celu)
  features/
    fisico/
      pages/               la pantalla (FisicoPage.jsx)
      components/          un componente por archivo
      api/                 pedidos al backend, un archivo por controller (sesiones.api.js…)
      lib/                 helpers propios de la sección
  shared/                  componentes de UI, formularios, calendario, hooks y cliente HTTP
```

Ninguna sección importa de otra. Lo que usan varias está en `shared/`.

## Decisiones técnicas

- **Fechas sin zona horaria del servidor.** El frontend manda `today` cuando un cálculo depende del día actual, así la racha y la agenda no se corren por la zona horaria del servidor. Los timestamps se guardan en UTC.
- **Datos, no listas fijas.** Las categorías de gastos, los tipos de entrenamiento con sus campos y los tipos de skill los crea el usuario; en el código solo quedan las reglas.
- **Actualización optimista.** Al arrastrar una tarea o tachar un ítem, la pantalla cambia al instante y se guarda atrás; si el backend falla, vuelve a lo que había.
- **Respuestas viejas descartadas.** El hook `useAsync` numera cada pedido e ignora las respuestas que llegan tarde, para que un mes no muestre los números de otro.
- **Offline.** Como PWA, se instala en el celu y muestra lo último cargado cuando no hay conexión.

## Seguridad

- Un solo usuario, sin registro público: se crea desde la terminal (`python -m app.cli create-user`).
- Contraseñas con Argon2id; sesiones con JWT firmado que se pueden invalidar todas de una vez al cambiar la contraseña.
- Límite de 5 intentos de login por IP, tomando la IP real detrás del proxy de Railway.
- Toda la API exige sesión, salvo el login y `/health`. En producción no se publican `/docs` ni el esquema OpenAPI.
- CORS cerrado al dominio del frontend; Content-Security-Policy estricta en Vercel; validación de toda entrada con Pydantic (por ejemplo, los links solo aceptan `http(s)`).

## Calidad

- **115 tests** de backend con **98 % de cobertura** (pytest), incluyendo los endpoints, las reglas de racha y las estadísticas.
- **mypy en modo strict**, ruff para lint y formato.
- **Migraciones probadas** en MySQL: suben desde una base vacía, bajan hasta el principio y vuelven a subir. `alembic check` confirma que los modelos y la base coinciden.

```bash
cd backend
uv run ruff check . && uv run mypy app tests && uv run pytest -q && uv run alembic check
```

## Correrlo en local

Requisitos: Python 3.13 con [uv](https://docs.astral.sh/uv/), Node 20+ y MySQL 8.

```bash
# 1. Base de datos: crea la base, el usuario y backend/.env
python3 database/setup_mysql.py

# 2. Backend (http://localhost:8000, documentación en /docs)
cd backend
uv sync
uv run alembic upgrade head
uv run python -m app.cli create-user
uv run uvicorn app.main:app --reload

# 3. Frontend (http://localhost:5173)
cd frontend
cp .env.example .env
npm install
npm run dev
```

Más detalle del backend (migraciones, autenticación y deploy en Railway) en [`backend/README.md`](backend/README.md).
