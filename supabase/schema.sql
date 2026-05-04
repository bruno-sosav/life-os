-- Life OS — Supabase schema (v2)
-- Idempotente: podés re-ejecutarlo en cualquier momento.

-- ─── Hábitos ────────────────────────────────────────────────
create table if not exists habits (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  color text default '#30D158',
  icon text,
  emoji text,
  active boolean default true,
  start_time time,
  duration_min int default 30,
  days_of_week integer[],   -- null = todos los días. [0..6] 0=lunes
  sort_order int default 0,
  created_at timestamptz default now()
);
alter table habits add column if not exists emoji text;
alter table habits add column if not exists start_time time;
alter table habits add column if not exists duration_min int default 30;
alter table habits add column if not exists days_of_week integer[];
alter table habits add column if not exists sort_order int default 0;

-- ─── Logs de hábitos ────────────────────────────────────────
create table if not exists habit_logs (
  id uuid primary key default gen_random_uuid(),
  habit_id uuid references habits(id) on delete cascade,
  date date not null,
  completed boolean default false,
  note text,
  created_at timestamptz default now(),
  unique(habit_id, date)
);

-- ─── Bloques de rutina semanal ──────────────────────────────
create table if not exists routine_blocks (
  id uuid primary key default gen_random_uuid(),
  day_of_week int,               -- 0=lunes … 6=domingo (null si es specific_date)
  specific_date date,            -- si es un bloque de un día puntual
  repeat_weekly boolean default true,
  hour_start int not null,
  hour_end int not null,
  activity text not null,
  category text,
  emoji text,
  color text
);
alter table routine_blocks add column if not exists repeat_weekly boolean default true;
alter table routine_blocks add column if not exists specific_date date;
alter table routine_blocks add column if not exists emoji text;
alter table routine_blocks add column if not exists hour_min int default 0;

-- ─── Completions de rutina (por día) ────────────────────────
create table if not exists routine_completions (
  id uuid primary key default gen_random_uuid(),
  block_id uuid references routine_blocks(id) on delete cascade,
  date date not null,
  completed boolean default true,
  completed_at timestamptz default now(),
  unique(block_id, date)
);

-- ─── Gym ────────────────────────────────────────────────────
create table if not exists gym_sessions (
  id uuid primary key default gen_random_uuid(),
  date date not null,
  attended boolean default true,
  routine_name text,
  notes text,
  created_at timestamptz default now()
);
create table if not exists gym_exercises (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references gym_sessions(id) on delete cascade,
  exercise_name text not null,
  sets int,
  reps int,
  weight_kg numeric,
  notes text
);

-- ─── MMA ────────────────────────────────────────────────────
create table if not exists mma_sessions (
  id uuid primary key default gen_random_uuid(),
  date date not null,
  attended boolean default true,
  session_type text,
  notes text,
  created_at timestamptz default now()
);

-- ─── Peso / Nutrición ───────────────────────────────────────
create table if not exists weight_logs (
  id uuid primary key default gen_random_uuid(),
  date date not null unique,
  weight_kg numeric not null,
  notes text,
  created_at timestamptz default now()
);
create table if not exists nutrition_logs (
  id uuid primary key default gen_random_uuid(),
  date date not null unique,
  quality_score int check (quality_score between 1 and 5),
  meals_count int,
  water_liters numeric,
  notes text,
  created_at timestamptz default now()
);

-- ─── Proyectos (Negocio) ────────────────────────────────────
create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  color text default '#0A84FF',
  emoji text default '📁',
  description text,
  created_at timestamptz default now()
);

-- ─── Tareas de Negocio ──────────────────────────────────────
create table if not exists stratus_tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  status text default 'pendiente',
  priority text default 'media',
  project text,
  project_id uuid references projects(id) on delete set null,
  due_date date,
  completed_at timestamptz,
  created_at timestamptz default now()
);
alter table stratus_tasks add column if not exists project_id uuid references projects(id) on delete set null;

create table if not exists stratus_ideas (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  body text,
  tags text[],
  created_at timestamptz default now()
);
create table if not exists stratus_goals (
  id uuid primary key default gen_random_uuid(),
  month date not null,
  title text not null,
  progress int default 0 check (progress between 0 and 100),
  completed boolean default false,
  created_at timestamptz default now()
);

-- ─── Libros ─────────────────────────────────────────────────
create table if not exists books (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  author text,
  status text default 'pendiente',
  rating int check (rating between 1 and 5),
  notes text,
  started_at date,
  finished_at date,
  created_at timestamptz default now()
);

-- ─── Mood ───────────────────────────────────────────────────
create table if not exists mood_logs (
  id uuid primary key default gen_random_uuid(),
  date date not null unique,
  mood_score int check (mood_score between 1 and 5),
  sleep_hours numeric,
  energy_score int check (energy_score between 1 and 5),
  notes text,
  created_at timestamptz default now()
);
alter table mood_logs add column if not exists energy_score int check (energy_score between 1 and 5);

-- ─── Diario personal ────────────────────────────────────────
create table if not exists journal_entries (
  id uuid primary key default gen_random_uuid(),
  date date not null,
  content text not null,
  mood_emoji text,
  created_at timestamptz default now()
);

-- ─── Ideas / Frases (Mental) ────────────────────────────────
create table if not exists ideas (
  id uuid primary key default gen_random_uuid(),
  text text not null,
  author text,
  tag text default 'idea',  -- 'frase', 'idea de negocio', 'aprendizaje', 'meta'
  created_at timestamptz default now()
);

-- ─── Listas ─────────────────────────────────────────────────
create table if not exists personal_lists (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  color text default '#30D158',
  icon text,
  created_at timestamptz default now()
);
create table if not exists list_items (
  id uuid primary key default gen_random_uuid(),
  list_id uuid references personal_lists(id) on delete cascade,
  text text not null,
  note text,
  status text default 'pendiente',
  checked boolean default false,
  priority int default 0,
  created_at timestamptz default now()
);

-- ─── Índices ────────────────────────────────────────────────
create index if not exists idx_habit_logs_date on habit_logs(date);
create index if not exists idx_routine_completions_date on routine_completions(date);
create index if not exists idx_gym_sessions_date on gym_sessions(date);
create index if not exists idx_mma_sessions_date on mma_sessions(date);
create index if not exists idx_weight_logs_date on weight_logs(date);
create index if not exists idx_nutrition_logs_date on nutrition_logs(date);
create index if not exists idx_mood_logs_date on mood_logs(date);
create index if not exists idx_journal_entries_date on journal_entries(date);
create index if not exists idx_stratus_tasks_status on stratus_tasks(status);
create index if not exists idx_stratus_tasks_project_id on stratus_tasks(project_id);
