# HymnFlow v2.7.0 — Scripture Lookup Reliability, Display Customization & Curated Translations

**Release date**: 2026-07-03

This release makes live scripture projection dependable and configurable: the Quick Scripture search now works every time (a write-back bug made it appear dead after the first lookup), the scripture overlay look is fully operator-customizable, the Style tab is decluttered with collapsible panels, and the full/data bundles gain **six accuracy-audited public-domain Bible translations**.

---

## 🔎 Fixed: Quick Scripture search going unresponsive

Two related parser bugs made the Live tab's scripture search appear to stop responding:

1. **After the first successful lookup**, the search box was refilled with `John 3:16 (KJV)` — and the `(KJV)` suffix made every subsequent parse fail silently. The parser now tolerates the suffix, and the box gets the bare reference back, so re-searching and in-place edits just work.
2. **Space-separated ranges** like `Romans 8:28 30`, `Romans 8 28 30`, and `John 3 16 18` now parse as verse ranges. The reference parser was restructured (book name + numeric tail) and covers colons, spaces, and dashes interchangeably.

Also fixed: overlay pushes within 300ms of a style change carried stale settings (snapshot cache now invalidates synchronously).

## 🎨 New: Scripture Display customization

A new **Scripture Display** panel in the Style tab controls how projected scripture looks:

| Control | Default | Effect |
|---|---|---|
| Scripture font | Classic Serif | Georgia, Times New Roman, Inter, Segoe UI, Roboto, Montserrat, or *Same as lyrics* |
| Italic text | on | the classic prose look |
| Show reference | on | hides the 📖 reference header entirely when off |
| Translation badge | on | hides just the translation badge |
| Custom size | off | 24–96px slider overriding the lyric font size for scripture only |

Changes apply **live** — a verse already on screen re-renders immediately, and the dock preview mirrors the overlay. All fields are additive to the v2 payload: older overlays ignore them; untouched settings render exactly the classic look.

## 📁 Style tab declutter

**OBS Connection** and **Scripture Display** are now collapsible panels (native `<details>`), collapsed by default. The OBS connection status dot stays visible in the collapsed header, and panel states persist across sessions.

## 📚 Curated Bible translations (full/data bundles)

`hymnflow-v2.7.0-full.zip` and `hymnflow-v2.7.0-data.zip` now include six public-domain translations that passed a systematic accuracy audit (canonical verse counts vs the KJV-1769 standard, footnote-contamination scan, truncation scan, cross-source text verification):

- **KJV 1769** — `bible-en-kjv.js` — clean text: 5,844 inline marginal notes stripped, pilcrows removed (unlike the legacy `bible-kjv.js`, which keeps `{…}` italics markers)
- **Revised Version 1885** — `bible-en-rv.js` — 5 upstream Selah-truncated verses patched from verified RV text
- **Literal Standard Version** — `bible-en-lsv.js` — modern literal translation; `[brackets]` and `||` line marks are authentic LSV notation
- **Geneva Bible 1599** — `bible-en-gnv.js` — original Early-Modern spelling and authentic 1599 versification
- **Douay-Rheims** — `bible-en-dra.js` — ⚠️ uses Vulgate Psalm numbering (Psalm N ≈ Hebrew Psalm N+1)
- **JPS 1917 Tanakh** — `bible-en-ojps.js` — Old Testament only

Import any of them via **Library → Bible → Import JSON**. Seventeen additional scraped translations were **rejected** for upstream data defects (footnotes fused mid-verse, poetry lines truncated) — the new `scripts/scrape_bible_api.py` documents the audit rules and verified patches so the data is reproducible.

---

## Artifacts

| File | Contents |
|---|---|
| `hymnflow-v2.7.0-lite.zip` | plugin + default KJV + default hymnal (nnbh) |
| `hymnflow-v2.7.0-full.zip` | plugin + all Bibles (incl. curated six) + all hymn collections |
| `hymnflow-v2.7.0-data.zip` | importable Bibles + hymn collections only |

## Upgrade notes

- No breaking changes. Settings, services, and imported Bibles are preserved.
- The overlay payload remains v2; the new `scripture*` settings fields are additive.
- Existing installs can drop the `-data` bundle contents into `data/` and import the curated translations from the Library tab.
