# HymnFlow v2.8.0 — Live-Operation Reliability, Service Workflow Overhaul & Schedule Files

**Release date**: 2026-07-05

This release came out of a full-plugin review through two lenses — media practitioner and UX specialist — followed by a fix-everything pass. The theme: **the dock must never misrepresent what's on the projector**, and the service workflow should be as calm at 9am Sunday as it is on Tuesday afternoon.

---

## 🚨 Reliability fixes (the "wrong thing on screen" class)

- **Display toggle can't lie anymore.** Clicking Display with nothing selected used to leave the switch ON over an empty screen. It now snaps back OFF with "Nothing to display — select a hymn first."
- **Overlay hide→show race fixed.** Hiding and then pushing the next slide within the 600 ms animation window could blank the fresh content (a stale hide timer fired late). Any show now cancels the pending hide. With animation set to *none*, hide is instant.
- **Dividers clear the screen.** Advancing to "— SERMON —" takes down both overlay channels instead of leaving the last hymn verse hanging.
- **Service editor rendered wrong for everyone**: a CSS rule overrode the `hidden` attribute, so the Add Hymn picker *and* the Add Item form were permanently open — the editor looked like a wall of inputs. One counter-rule restores the intended clean flow.

## 📄 Service schedules as text files

- **Export** any service to a hand-editable `.txt` (per-service **⋯ → Export .txt**):

  ```
  Service: Sunday Morning

  1. Hymn: 234 - Amazing Grace
     Notes: pianist starts soft
  2. Scripture: John 3:16-18
  3. Announce: Youth meeting Wednesday 5pm
  4. Divider: — SERMON —
  ```

- **Import** (Service tab → Import) is forgiving: item numbers and type prefixes are optional — bare lines resolve as **hymn** (by number/title) → **scripture reference** → **announcement**. Unknown hymns become clearly-labelled placeholders and are reported in a warning summary. Round-trips are lossless.
- **Save where you choose** — exports (schedules and the hymn-library JSON) open a native *Save As* dialog where the browser supports it (Chrome/Edge and OBS docks on recent OBS). Where it doesn't, they land in Downloads and the status bar tells you so.

## 🎛️ Service editor overhaul

- **Cue notes on hymns** — ✎ now works on hymn items ("verses 1, 2, 4 only")
- **Draft autosave** — a dock reload mid-edit (OBS scene change, crash, F5) restores the editor exactly where you were
- **Unsaved-changes dot** on the Save button; **Escape** closes item form → picker → editor in order; the hymn picker gains **↑/↓/Enter** keyboard selection
- New services prefill a dated name; the editor opens above the list; per-service actions declutter into **Load / Edit / ⋯**

## 🎬 Live operation

- **Blank Screen** button beside Emergency Clear — pause the output without losing your place (Emergency Clear remains the full reset)
- **Auto-display planned scripture** (opt-in, Style → Scripture Display) for rehearsed services
- **OBS hotkey alerts** — connection drops announced once ("reconnecting…", retry count on the badge), reconnection confirmed
- **Operator hints**: "Display is OFF" when selecting a hymn with the switch down, "Chorus next" in the verse info, "shrinks to fit" warning for over-long verses, and a status bar that pulses on each new message
- **Lines per display** now goes down to 1; the Text Slide tool moved to the Live tab as a collapsible panel

## 🌍 Under the hood

- **i18n fallback fixed** — raw translation keys no longer leak into the UI, console warning flood eliminated
- Single-digit hymn-number search ("5" finds hymn 5); search-highlight regex built once per render
- obs-websocket password storage documented in SECURITY.md with hardening guidance

---

## Artifacts

| File | Contents |
|---|---|
| `hymnflow-v2.8.0-lite.zip` | plugin + default KJV + default hymnal (nnbh) |
| `hymnflow-v2.8.0-full.zip` | plugin + all Bibles (incl. six curated translations) + all hymn collections |
| `hymnflow-v2.8.0-data.zip` | importable Bibles + hymn collections only |

## Upgrade notes

- No breaking changes. Settings, services, and imported Bibles are preserved.
- New settings (`scriptureAutoDisplay`, panel states) default to prior behavior.
- The Text Slide tool moved from the Service tab to the Live tab.
