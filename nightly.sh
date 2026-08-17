#!/bin/zsh
# Defiant nightly refresh:
#   crawl OSM facilities → rebuild directory → refresh article data blocks →
#   cards → build → QA gate → local commit → deploy to Cloudflare Pages.
# Resilient: if the crawl mirror is down, it still rebuilds from existing data.
# Git stays LOCAL (standing directive since 2026-08-12) — the deploy lane is
# cloudflare-mirror/deploy.sh, not a push. Private CRM (partners.db, drafts)
# is gitignored and never leaves the machine.
set -o pipefail
REPO="$HOME/Developer/claude code projects/defiant-site"
MIRROR="$HOME/Developer/claude code projects/cloudflare-mirror"
LOG="$HOME/Library/Logs/defiant-nightly.log"
cd "$REPO" || exit 1

echo "───── $(date '+%Y-%m-%d %H:%M') nightly refresh ─────" >> "$LOG"
python3 partners/crawl.py     >> "$LOG" 2>&1 || echo "  crawl: skipped/failed (using existing data)" >> "$LOG"
python3 build_directory.py    >> "$LOG" 2>&1
python3 articles.py refresh   >> "$LOG" 2>&1 || echo "  articles: refresh skipped (a source was down; blocks keep last good data)" >> "$LOG"
python3 make_cards.py         >> "$LOG" 2>&1 || echo "  cards: skipped (Pillow?)" >> "$LOG"
python3 build.py              >> "$LOG" 2>&1 || { echo "  BUILD FAILED — stopping" >> "$LOG"; exit 1; }

# Local commit always — the ledger of what changed, whether or not we deploy.
git add -A >> "$LOG" 2>&1
if git diff --cached --quiet; then
  echo "  no changes" >> "$LOG"
else
  git commit -q -m "Nightly refresh $(date '+%Y-%m-%d')

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" >> "$LOG" 2>&1
  echo "  committed locally ✓ (git stays local; Cloudflare is the deploy)" >> "$LOG"
fi

# The QA gate decides whether tonight's build goes out the door.
if python3 articles.py qa >> "$LOG" 2>&1; then
  if /bin/bash "$MIRROR/deploy.sh" defiant >> "$LOG" 2>&1
  then echo "  deployed ✓ (Cloudflare Pages)" >> "$LOG"
  else echo "  DEPLOY FAILED" >> "$LOG"; fi
else
  echo "  QA gate closed — built + committed, holding the deploy for a human look" >> "$LOG"
fi
