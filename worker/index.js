// defiant-leads — homebrew lead + subscriber capture for defiant.to (no third parties)
// POST /lead        : store a lead (honeypot + time-trap + per-IP rate limit)
// GET  /leads       : read leads (Bearer LEADS_TOKEN or ?token=), ?format=html
// POST /subscribe   : add a newsletter subscriber (same anti-bot; dedupes on email)
// GET  /subscribers : read the list (token), ?format=csv to export for a sender
// Deploy steps are in the repo README (wrangler d1 create → schema → secret → deploy).

const ALLOW = [
  "https://defiant.to",
  "https://www.defiant.to",
  "http://defiant.to",       // interim: before GitHub's TLS cert lands / Enforce HTTPS is on
  "http://www.defiant.to",
  "http://localhost:8899",
  "http://127.0.0.1:8899",
];

function cors(origin) {
  return {
    "Access-Control-Allow-Origin": ALLOW.includes(origin) ? origin : ALLOW[0],
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };
}

function json(data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...extra },
  });
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get("Origin") || "";

    if (req.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(origin) });
    }

    if (url.pathname === "/lead" && req.method === "POST") {
      let b;
      try { b = await req.json(); } catch { return json({ ok: false, error: "bad json" }, 400, cors(origin)); }

      // Honeypot: humans never fill "website". Swallow silently so bots learn nothing.
      if (b.website) return json({ ok: true }, 200, cors(origin));
      // Time-trap: form open >3s and <24h.
      const elapsed = Date.now() - Number(b.t0 || 0);
      if (!(elapsed > 3000 && elapsed < 86_400_000)) return json({ ok: true }, 200, cors(origin));

      const name = String(b.name || "").slice(0, 200).trim();
      const contact = String(b.contact || "").slice(0, 300).trim();
      const message = String(b.message || "").slice(0, 5000).trim();
      if (!contact || !message) return json({ ok: false, error: "contact and message required" }, 400, cors(origin));

      const ip = req.headers.get("CF-Connecting-IP") || "";
      const hourAgo = Date.now() - 3_600_000;
      const { results } = await env.DB
        .prepare("SELECT COUNT(*) AS n FROM leads WHERE ip = ?1 AND ts > ?2")
        .bind(ip, hourAgo).all();
      if (results[0].n >= 5) return json({ ok: false, error: "slow down" }, 429, cors(origin));

      await env.DB
        .prepare("INSERT INTO leads (ts, name, contact, message, ip, ua, referer) VALUES (?1,?2,?3,?4,?5,?6,?7)")
        .bind(Date.now(), name, contact, message, ip,
              (req.headers.get("User-Agent") || "").slice(0, 300),
              (req.headers.get("Referer") || "").slice(0, 300))
        .run();
      return json({ ok: true }, 200, cors(origin));
    }

    if (url.pathname === "/leads" && req.method === "GET") {
      const tok = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "")
        || url.searchParams.get("token") || "";
      if (!env.LEADS_TOKEN || tok !== env.LEADS_TOKEN) return json({ ok: false, error: "nope" }, 403);

      const { results } = await env.DB
        .prepare("SELECT id, ts, name, contact, message, referer FROM leads ORDER BY ts DESC LIMIT 500")
        .all();

      if (url.searchParams.get("format") === "html") {
        const rows = results.map((r) =>
          `<tr><td>${new Date(r.ts).toISOString().slice(0, 16).replace("T", " ")}</td>` +
          `<td>${esc(r.name)}</td><td>${esc(r.contact)}</td><td>${esc(r.message)}</td></tr>`).join("");
        const html = `<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">
<title>Defiant leads (${results.length})</title>
<style>body{font:18px/1.6 ui-monospace,monospace;margin:2rem;background:#FBF7EF;color:#191919}
table{border-collapse:collapse;width:100%}td,th{border:2px solid #191919;padding:.6rem;text-align:left;vertical-align:top}
th{background:#191919;color:#FBF7EF}h1{font-size:1.6rem}</style>
<h1>✊ Defiant leads — ${results.length}</h1>
<table><tr><th>When (UTC)</th><th>Name</th><th>Contact</th><th>Message</th></tr>${rows}</table>`;
        return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
      }
      return json({ ok: true, count: results.length, leads: results });
    }

    if (url.pathname === "/subscribe" && req.method === "POST") {
      let b;
      try { b = await req.json(); } catch { return json({ ok: false, error: "bad json" }, 400, cors(origin)); }

      if (b.website) return json({ ok: true }, 200, cors(origin));            // honeypot
      const elapsed = Date.now() - Number(b.t0 || 0);
      if (!(elapsed > 3000 && elapsed < 86_400_000)) return json({ ok: true }, 200, cors(origin));

      const email = String(b.email || "").slice(0, 300).trim().toLowerCase();
      const name = String(b.name || "").slice(0, 200).trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
        return json({ ok: false, error: "valid email required" }, 400, cors(origin));

      const ip = req.headers.get("CF-Connecting-IP") || "";
      const hourAgo = Date.now() - 3_600_000;
      const { results } = await env.DB
        .prepare("SELECT COUNT(*) AS n FROM subscribers WHERE ip = ?1 AND ts > ?2")
        .bind(ip, hourAgo).all();
      if (results[0].n >= 5) return json({ ok: false, error: "slow down" }, 429, cors(origin));

      // INSERT OR IGNORE: re-subscribing with the same email is a silent no-op (UNIQUE email).
      await env.DB
        .prepare("INSERT OR IGNORE INTO subscribers (ts, email, name, source, ip, ua, referer, status) VALUES (?1,?2,?3,?4,?5,?6,?7,'active')")
        .bind(Date.now(), email, name, String(b.source || "site").slice(0, 60), ip,
              (req.headers.get("User-Agent") || "").slice(0, 300),
              (req.headers.get("Referer") || "").slice(0, 300))
        .run();
      return json({ ok: true }, 200, cors(origin));
    }

    if (url.pathname === "/subscribers" && req.method === "GET") {
      const tok = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "")
        || url.searchParams.get("token") || "";
      if (!env.LEADS_TOKEN || tok !== env.LEADS_TOKEN) return json({ ok: false, error: "nope" }, 403);

      const { results } = await env.DB
        .prepare("SELECT id, ts, email, name, source, status FROM subscribers WHERE status = 'active' ORDER BY ts DESC LIMIT 10000")
        .all();

      if (url.searchParams.get("format") === "csv") {
        const q = (s) => `"${String(s ?? "").replace(/"/g, '""')}"`;
        const csv = "email,name,subscribed_utc,source\n" + results.map((r) =>
          [r.email, q(r.name), new Date(r.ts).toISOString(), r.source || ""].join(",")).join("\n");
        return new Response(csv + "\n", {
          headers: {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition": "attachment; filename=defiant-subscribers.csv",
          },
        });
      }
      return json({ ok: true, count: results.length, subscribers: results });
    }

    return json({ ok: false, error: "not found" }, 404);
  },
};
