#!/bin/zsh
# Defiant nightly directory refresh:
#   crawl OSM facilities → rebuild public directory → rebuild site → push.
# Resilient: if the crawl mirror is down, it still rebuilds from existing data.
# Only commits when something actually changed. Private CRM (partners.db, drafts)
# is gitignored and never pushed.
set -o pipefail
REPO="$HOME/Developer/claude code projects/defiant-site"
LOG="$HOME/Library/Logs/defiant-nightly.log"
cd "$REPO" || exit 1

echo "───── $(date '+%Y-%m-%d %H:%M') nightly refresh ─────" >> "$LOG"
python3 partners/crawl.py     >> "$LOG" 2>&1 || echo "  crawl: skipped/failed (using existing data)" >> "$LOG"
python3 build_directory.py    >> "$LOG" 2>&1
python3 build.py              >> "$LOG" 2>&1 || { echo "  BUILD FAILED — not pushing" >> "$LOG"; exit 1; }

git add -A >> "$LOG" 2>&1
if git diff --cached --quiet; then
  echo "  no changes" >> "$LOG"
else
  git commit -q -m "Nightly directory refresh $(date '+%Y-%m-%d')

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" >> "$LOG" 2>&1
  if git push -q >> "$LOG" 2>&1; then echo "  pushed ✓" >> "$LOG"; else echo "  PUSH FAILED" >> "$LOG"; fi
fi
