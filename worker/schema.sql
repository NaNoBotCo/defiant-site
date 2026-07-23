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
  ip           TEXT,
  ua           TEXT,
  referer      TEXT,
  status       TEXT DEFAULT 'active',   -- active | unsubscribed
  confirm_token TEXT,
  confirmed_ts INTEGER,
  unsub_ts     INTEGER
);
CREATE INDEX IF NOT EXISTS idx_subscribers_ts ON subscribers (ts);
