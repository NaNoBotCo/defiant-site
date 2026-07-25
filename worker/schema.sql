CREATE TABLE IF NOT EXISTS leads (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  ts      INTEGER NOT NULL,
  name    TEXT,
  contact TEXT NOT NULL,
  message TEXT NOT NULL,
  ip      TEXT,
  ua      TEXT,
  referer TEXT,
  seen    INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_leads_ts ON leads (ts);

-- Newsletter/list subscribers — YOUR list, in YOUR database. No third party.
-- Single opt-in with consent metadata (ts, ip, source). confirm_token +
-- confirmed_ts are reserved for when a sender is wired for double opt-in.
CREATE TABLE IF NOT EXISTS subscribers (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ts           INTEGER NOT NULL,
  email        TEXT NOT NULL UNIQUE,
  name         TEXT,
  source       TEXT,
  frequency    TEXT DEFAULT 'weekly',    -- weekly (default) | daily
  ip           TEXT,
  ua           TEXT,
  referer      TEXT,
  status       TEXT DEFAULT 'active',   -- active | unsubscribed
  confirm_token TEXT,
  confirmed_ts INTEGER,
  unsub_ts     INTEGER
);
CREATE INDEX IF NOT EXISTS idx_subscribers_ts ON subscribers (ts);
-- Migration for an already-deployed table (run once; harmless if the column exists):
--   wrangler d1 execute defiant-leads --remote --command \
--     "ALTER TABLE subscribers ADD COLUMN frequency TEXT DEFAULT 'weekly'"

-- Clinic self-service submissions — a clinic tells us who they are, what they do,
-- current promotions. Before/after photos come over LINE (how Thai clinics work).
CREATE TABLE IF NOT EXISTS clinic_submissions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  ts          INTEGER NOT NULL,
  name        TEXT NOT NULL,
  services    TEXT,
  area        TEXT,
  phone       TEXT,
  line        TEXT,
  website     TEXT,
  promotions  TEXT,
  pitch       TEXT,
  ip          TEXT,
  ua          TEXT,
  referer     TEXT,
  status      TEXT DEFAULT 'new'
);
CREATE INDEX IF NOT EXISTS idx_clinic_ts ON clinic_submissions (ts);
