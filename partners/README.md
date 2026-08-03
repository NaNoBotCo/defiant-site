# Defiant clinic-partners pipeline

Crawl Chiang Mai clinics → review → dossiers + **bilingual (Thai-first) intro
letters** → export batches for your translators → track who replied. Builds
relationships across **gyn, aesthetic/glow-up, longevity, and geriatric** care.

**Nothing here ever sends anything.** Drafts are files; humans send, one clinic
at a time. `partners.db`, letter drafts, and the vault `Partners/` folder are all
**private** — gitignored, and the vault dossiers live outside `Public Links/` so
they never reach the site or Obsidian Publish.

## Use it

Double-click **Desktop → "Defiant Partners.command"**, or:

```
cd partners && python3 board.py
```

Menu: review NEW clinics into shortlist/pass → work the shortlist (each promote
writes a vault dossier + a letter draft) → export drafted letters to a dated
Desktop batch for your translators → mark statuses as they reply.

## Data sources

- **cm-womens-health** (sibling project): 258 verified CM facilities, OB-GYN
  pre-tagged → seeds the `gyn` vertical. `python3 import_cmwh.py`
- **OpenStreetMap / Overpass**: clinics, doctors, nursing homes across greater
  Chiang Mai (bbox). `python3 crawl.py` (falls back across mirrors). Re-running
  refreshes `last_seen` and fills gaps; never clobbers your statuses or notes.

Classification into verticals is Thai+English keyword matching — deliberately
rough. The big `other` bucket is expected; the review board is where you sort it
(`[v] change vertical` on any clinic).

## The letters

Thai first (written in NaN's voice, ค่ะ), English mirror below, then a private
translator-notes block (honorifics, ครับ/ค่ะ, channel choice) that is NOT part of
the email. Tone is fixed: สุภาพ อ่อนน้อม ไม่เร่งรัด — guests asking for a
relationship, dharmically. Offer: free English profile on defiant.to, screened
referrals, interpreter support, terms at the clinic's discretion.

The public landing the letters point to is `/partners/` (bilingual), built from
`~/Vaults/Defiant/Public Links/=Partners.md`.

## Pipeline statuses

`new → shortlist | pass → drafted → translated → sent → replied → meeting → partner`
