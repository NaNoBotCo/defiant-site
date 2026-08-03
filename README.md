# defiant-site — the machinery behind defiant.to

**Vault-first.** The Obsidian vault at `~/Vaults/Defiant` is the single source
of truth. Edit notes there (Obsidian is the CMS); everything else is compilation.

```
~/Vaults/Defiant  (Obsidian vault — CANONICAL)
        │
        ├── Obsidian Publish  →  publish.obsidian.md/defiant   (the Notebook — push from Obsidian)
        │
        └── build.py          →  docs/  →  GitHub Pages  →  defiant.to   (the money site)
```

## Commands

| What | How |
|---|---|
| Regenerate directory stubs (never overwrites edits) | `python3 gen_vault_notes.py` |
| Compile vault → `docs/` (link-checked) | `python3 build.py` |
| Preview locally | `python3 -m http.server 8899 -d docs` |
| Read leads | `python3 leads.py` (or the Desktop launcher) |

## The lead Worker (homebrew form backend — replaces Tally)

One-time deploy from `worker/`:

```
cd worker
wrangler d1 create defiant-leads          # paste the printed database_id into wrangler.toml
wrangler d1 execute defiant-leads --file schema.sql --remote
wrangler secret put LEADS_TOKEN           # invent a long random string; it's your inbox key
wrangler deploy
```

If the deployed URL differs from `https://defiant-leads.wichaa.workers.dev`,
update `WORKER_URL` in `build.py` and rebuild. Anti-bot: honeypot field,
3-second time trap, 5/hour/IP rate limit. Reading leads: `leads.py`, or
`<worker-url>/leads?format=html&token=…` in a browser.

## Rules of the road

- **The encrypted email address never appears in any note or any emitted HTML.**
  It exists only as char codes in `build.py`; the site assembles it client-side
  behind reveal buttons. The build hard-fails if it ever leaks in plaintext.
- Price tables live inside `<!-- defiant:auto:* -->` markers — future crawlers
  (`crawl/`) refresh those blocks without touching hand-written prose.
- All indicative prices are 2026 ranges from published aggregators/hospital
  lists; the site says "indicative, confirmed in writing at intake" everywhere.
- `docs/` is generated; fix the generator or the vault, never `docs/`.

## Phase 2 — self-updating rails (open doors, no backlog)

- `crawl/refresh_prices.py` — re-scrape aggregator ranges → rewrite auto blocks.
- `crawl/refresh_jci.py` — verify JCI accreditation list annually.
- Per-page OG share cards (masters + generator, like wichaa's `make_card.py`).
- FX line (USD/THB) on price tables.
