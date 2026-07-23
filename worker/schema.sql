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
