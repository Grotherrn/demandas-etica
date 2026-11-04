-- Esquema compartilhado pela aplicação e pela demonstração SQL do M3.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS demands (
 id INTEGER PRIMARY KEY, title TEXT NOT NULL, client TEXT NOT NULL,
 stage TEXT NOT NULL, due TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS history (
 id INTEGER PRIMARY KEY, demand_id INTEGER NOT NULL REFERENCES demands(id),
 previous_stage TEXT, new_stage TEXT NOT NULL, note TEXT NOT NULL, happened_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS incidents (
 id INTEGER PRIMARY KEY, demand_id INTEGER REFERENCES demands(id), title TEXT NOT NULL,
 category TEXT NOT NULL, description TEXT NOT NULL, impact TEXT NOT NULL,
 action TEXT NOT NULL DEFAULT '', lesson TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);

-- Índices das chaves estrangeiras para consultas de histórico e incidentes.
CREATE INDEX IF NOT EXISTS idx_history_demand ON history(demand_id);
CREATE INDEX IF NOT EXISTS idx_incidents_demand ON incidents(demand_id);
