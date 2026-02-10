# Implementation Plan — YTLinkExporter v1.0

> Build a Python/CustomTkinter Windows desktop app that uses `yt-dlp` to extract YouTube playlist/channel metadata and export it as `.url` shortcuts, offline HTML catalogs (Base64-embedded thumbnails), and plain-text link lists.

## User Review Required

> [!IMPORTANT]
> **Dependency choice**: The plan uses `Pillow` for thumbnail resizing and `customtkinter` for the GUI. Confirm these are acceptable, or suggest alternatives.

> [!IMPORTANT]
> **Cookie workflow**: The PRD calls for a `cookies.txt` file. The plan implements a "Browse for cookies.txt" button in Settings. Please confirm this UX is sufficient.

> [!WARNING]
> **`yt-dlp` bundling**: For end-user distribution the app will call `yt-dlp` as a Python library (`import yt_dlp`). It will **not** shell out to a binary. Confirm this approach.

---

## Module Map

```
src/
├── main.py              # Entry point — creates App window
├── gui/
│   ├── __init__.py
│   ├── app.py           # Root CTk window, theme, layout frames
│   ├── header.py        # URL input + "Load Metadata" button
│   ├── filters.py       # Collapsible filter panel (dates, count, keyword)
│   ├── export_opts.py   # Export-format checkboxes + path selector
│   └── status.py        # Progress bar + scrolling status log
├── core/
│   ├── __init__.py
│   ├── extractor.py     # yt-dlp wrapper (flat extraction, metadata)
│   ├── filters.py       # Date-range, count-limit, keyword logic
│   ├── thumbnail.py     # Download, resize (320 px), Base64 encode
│   └── sanitizer.py     # Windows-safe filename sanitization
├── exporters/
│   ├── __init__.py
│   ├── shortcut.py      # .url file writer
│   ├── html_catalog.py  # Self-contained HTML generator
│   └── text_list.py     # Plain-text URL list writer
├── config/
│   ├── __init__.py
│   └── settings.py      # Persistent settings (JSON): default path, cookies, theme
└── utils/
    ├── __init__.py
    └── threading.py      # Background-thread helper for GUI responsiveness
```

---

## Proposed Changes

Each component below will be a separate directive when we begin execution.

---

### Component 1 — Project Skeleton & Dependencies

#### [NEW] [requirements.txt](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/requirements.txt)
- `customtkinter`, `yt-dlp`, `Pillow`, `requests`, `tkcalendar` (date pickers)

#### [NEW] [src/main.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/main.py)
- Entry point: instantiate `App`, call `mainloop()`.

---

### Component 2 — Core Extraction Engine (`src/core/`)

#### [NEW] [extractor.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/core/extractor.py)
- `extract_playlist(url, cookies_path) → list[VideoMeta]`
- Uses `yt_dlp.YoutubeDL` with `extract_flat=True`, `ignoreerrors=True`.
- Returns a list of dataclass objects: `VideoMeta(title, url, video_id, thumbnail_url, upload_date)`.
- Skips deleted/private entries gracefully.

#### [NEW] [filters.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/core/filters.py)
- `apply_filters(videos, date_start, date_end, limit, keyword) → list[VideoMeta]`
- Pure function, no side effects.

#### [NEW] [thumbnail.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/core/thumbnail.py)
- `download_and_encode(url, max_width=320) → str` (Base64 data-URI string).
- Uses `requests` + `Pillow` for resize/compress.
- Returns a placeholder on failure.

#### [NEW] [sanitizer.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/core/sanitizer.py)
- `sanitize_filename(name) → str` — strips `< > : " / \ | ? *` and trailing dots/spaces.

---

### Component 3 — Exporters (`src/exporters/`)

#### [NEW] [shortcut.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/exporters/shortcut.py)
- Writes one `.url` file per video: `{YYYY-MM-DD} - {SanitizedTitle}.url`.

#### [NEW] [html_catalog.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/exporters/html_catalog.py)
- Generates a single self-contained HTML file with responsive CSS grid, embedded Base64 thumbnails, and clickable titles.

#### [NEW] [text_list.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/exporters/text_list.py)
- Writes one URL per line to `{PlaylistName}_links.txt`.

---

### Component 4 — GUI (`src/gui/`)

#### [NEW] [app.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/gui/app.py)
- Root `CTk` window. Assembles Header → Filters → Export Options → Status frames.
- Binds the **Export** button to a background-thread pipeline: extract → filter → export.

#### [NEW] [header.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/gui/header.py)
- URL text entry + "Load Metadata" button.
- On load: calls `extractor.extract_playlist` in flat mode for just the playlist title/thumbnail, enables the Export button.

#### [NEW] [filters.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/gui/filters.py)
- Collapsible frame: date pickers, count spinner, keyword text entry.

#### [NEW] [export_opts.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/gui/export_opts.py)
- Three checkboxes + path field + Browse button.

#### [NEW] [status.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/gui/status.py)
- `CTkProgressBar` + scrolling `CTkTextbox` log.
- Exposes `log(msg)` and `set_progress(pct)` called from background threads via `after()`.

---

### Component 5 — Config & Threading

#### [NEW] [settings.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/config/settings.py)
- Reads/writes a JSON file at `~/.ytlinkexporter/settings.json`.
- Keys: `default_save_path`, `cookies_path`, `theme` (system/dark/light).

#### [NEW] [threading.py](file:///c:/Users/jwoud/OneDrive/Projects/YTLinkExporter/src/utils/threading.py)
- `run_in_background(fn, callback, error_callback)` — wraps `threading.Thread`.

---

## Execution Strategy

Because this is a greenfield project with **15+ new files**, the work will be split into **four directives** executed in order:

| # | Directive | Risk | Files | Depends On |
|---|-----------|------|-------|------------|
| 1 | `2026-02-10_project_skeleton` | LOW | `requirements.txt`, `main.py`, all `__init__.py`, `settings.py`, `sanitizer.py` | — |
| 2 | `2026-02-10_core_engine` | MEDIUM | `extractor.py`, `filters.py`, `thumbnail.py` | Directive 1 |
| 3 | `2026-02-10_exporters` | MEDIUM | `shortcut.py`, `html_catalog.py`, `text_list.py` | Directive 2 |
| 4 | `2026-02-10_gui_shell` | MEDIUM | `app.py`, `header.py`, `gui/filters.py`, `export_opts.py`, `status.py`, `threading.py` | Directives 1-3 |

---

## Verification Plan

### Automated Tests

Since the project is brand-new, I will create a `tests/` directory with `pytest` tests for the pure-logic modules:

| Test File | Covers | Command |
|-----------|--------|---------|
| `tests/test_sanitizer.py` | Illegal chars, edge cases (all-dot names, Unicode) | `python -m pytest tests/test_sanitizer.py -v` |
| `tests/test_filters.py` | Date range, count limit, keyword include/exclude | `python -m pytest tests/test_filters.py -v` |
| `tests/test_exporters.py` | `.url` content, `.txt` content, HTML structure | `python -m pytest tests/test_exporters.py -v` |

Full suite: `python -m pytest tests/ -v`

### Manual Verification

> [!NOTE]
> The following manual tests require a working internet connection and a real YouTube playlist URL.

1. **Launch the app**: `python src/main.py` — verify the CustomTkinter window opens without errors.
2. **Load Metadata**: Paste a public YouTube playlist URL → click "Load Metadata" → confirm the playlist title appears and the Export button becomes enabled.
3. **Export all three formats**: Check all three export checkboxes → click Export → verify:
   - `.url` files open the correct video in a browser when double-clicked.
   - The `.html` file displays thumbnails **offline** (disconnect Wi-Fi, then open it).
   - The `.txt` file contains one URL per line.
4. **Filters**: Set a date range and count limit → export → confirm the output respects the filters.
5. **Error handling**: Enter an invalid URL → confirm a red error label appears and Export stays disabled.

> I'd appreciate your suggestions on any additional manual test scenarios (e.g., a specific large playlist to stress-test, or cookie-based access).
