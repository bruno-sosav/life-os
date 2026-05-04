# Life OS

> Segundo cerebro personal — uso individual, web + PWA.

## Stack

- **React 18 + Vite 5** (JSX, sin TypeScript)
- **Tailwind CSS 3** (dark por defecto, toggle a claro)
- **React Router v6** (rutas anidadas en módulos con sub-tabs)
- **Zustand** para estado UI global (theme, sidebar)
- **Supabase JS v2** (auth opcional + Postgres)
- **Recharts** (Line, Bar, Radar)
- **@hello-pangea/dnd** (drag & drop del kanban Stratus)
- **framer-motion** (transiciones suaves de página y modales)
- **date-fns** + locale `es` (zona horaria local)
- **vite-plugin-pwa** (instalable, NetworkFirst para Supabase, CacheFirst para assets)

## Estructura

```
src/
  components/        Componentes UI reutilizables (Button, Card, Modal, Badge, Tabs, Layout, Sidebar, BottomNav, EmptyState, PageHeader)
  modules/
    dashboard/       Hábitos + rutina diaria/semanal
    fisico/          Gym, MMA, Peso & Nutrición (sub-rutas)
    stratus/         Kanban + Ideas + Objetivos del mes
    mental/          Libros + Mood
    listas/          Grid de listas + vista por lista (sub-ruta :id)
    analytics/       Scores, radar, heatmap, barras semanales, peso
  lib/               supabase client, constants, dates helpers
  store/             Zustand stores (uiStore por ahora)
  hooks/             useAsync (queries declarativas con refetch)
  styles/            index.css (Tailwind + utilities + tema claro)
public/              icon.svg, pwa-192x192.png, pwa-512x512.png (placeholder)
supabase/            schema.sql (pegar en Supabase SQL editor)
scripts/             gen-icons.mjs (placeholder PNGs)
```

Cada módulo:
- `index.jsx` orquesta páginas/sub-rutas y carga data.
- `queries.js` encapsula todas las llamadas a Supabase del módulo.
- Componentes internos son pequeños (<200 LOC) y autónomos.

## Convenciones

- **Fechas**: trabajamos con `yyyy-MM-dd` (string ISO sin tiempo) cuando se persiste en Postgres. UI vía `date-fns` con locale español.
- **Colores de acento**: `#7F77DD` púrpura, `#1D9E75` teal, `#D85A30` coral. Categorías de rutina: gym=coral, mma=rojo, estudio=azul, negocio=púrpura, personal=teal.
- **Tipografía**: `DM Sans` (UI) y `Space Grotesk` (números/stats grandes), cargadas desde Google Fonts.
- **Cards**: `bg-ink-900` con borde `rgba(255,255,255,0.06)` y radio `rounded-xl`.
- **Sin sombras fuertes**: shadow-card es 1px sutil.
- **Mobile**: sidebar se reemplaza por bottom nav <768px.

## Setup local

1. Copiar `.env.example` → `.env` y completar con tus credenciales de Supabase.
2. En Supabase, abrir el SQL editor y ejecutar `supabase/schema.sql`.
3. Instalar deps y arrancar:
   ```bash
   npm install
   npm run dev
   ```
4. Build de producción:
   ```bash
   npm run build && npm run preview
   ```

## Estado actual del desarrollo

✅ Scaffolding completo de los 6 módulos con UI funcional.
✅ Schema de Supabase listo (sin RLS — uso de un solo usuario; agregar políticas si se expone).
✅ PWA configurada (íconos PNG son placeholders 1x1, reemplazar por reales).
✅ Build pasa sin errores.

## Decisiones de arquitectura

- **Sin auth todavía**: la app está pensada para un usuario único; Supabase puede usarse con la `anon key` y RLS abierto. Si se quiere proteger, activar RLS y agregar `auth.uid()` checks por tabla.
- **Sin TypeScript**: prioridad a velocidad de iteración; las queries devuelven objetos planos.
- **No hay capa de "service" aparte de `queries.js`**: cada módulo habla directo a Supabase desde su propio archivo de queries para mantener acoplamiento bajo entre módulos.
- **Estado**: data local con `useAsync` (re-fetch on demand). Zustand sólo para UI global. No hay cache invalidation centralizado — cada módulo decide cuándo refetchear (suficiente para escala personal).
- **Heatmap propio**: implementado a mano en CSS grid en vez de depender de una lib extra para una visualización tan específica.

## Próximos pasos sugeridos

- Reemplazar PNGs placeholder por íconos reales (192/512).
- Ajustar `build.rollupOptions.manualChunks` para code-splitting (Recharts es pesado).
- Agregar autenticación email magic link si se quiere acceder desde múltiples dispositivos sin compartir DB pública.
- Persistir filtros (proyecto en Stratus, rango en Peso) en localStorage.
- Realtime subscriptions para sincronizar cambios entre tabs.
