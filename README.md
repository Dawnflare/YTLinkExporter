# YTLinkExporter

A Windows desktop application for archiving YouTube playlists and channels without downloading video files. Built with **Python**, **CustomTkinter**, and **yt-dlp**.

## Features

- **Multi-Format Export**
  - **Windows Shortcuts (`.url`)** — one file per video, opens in your default browser.
  - **Offline HTML Catalog (`.html`)** — responsive grid with embedded Base64 thumbnails for fully offline viewing.
  - **Plain Text List (`.txt`)** — one URL per line for use with other tools.
- **Smart Filtering** — filter by date range, keyword include/exclude, or video count limit.
- **Batch Processing** — handles playlists and channels with thousands of videos.
- **Cookie Support** — access age-gated or restricted content via a `cookies.txt` file.
- **Persistent Settings** — remembers your default save folder and theme preference.
- **Dark / Light / System Theme** — powered by CustomTkinter.

## Quick Start

### Using Batch Files (recommended)

1. **First-time setup** — double-click **`setup.bat`** to create the virtual environment and install dependencies.
2. **Launch the app** — double-click **`launch.bat`**. If the venv doesn't exist yet, it runs setup automatically.

### Using the Command Line

```bash
# 1. Clone the repository
git clone https://github.com/Dawnflare/YTLinkExporter.git
cd YTLinkExporter

# 2. Create a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt

# 3. Launch the app
.venv\Scripts\python.exe src/main.py
```

## Project Structure

```
src/
├── main.py                  # Entry point
├── config/settings.py       # Persistent JSON settings
├── core/
│   ├── extractor.py         # yt-dlp flat extraction → VideoMeta
│   ├── filters.py           # Date, keyword, and count filters
│   ├── thumbnail.py         # Download → resize → Base64 encode
│   └── sanitizer.py         # Windows-safe filename cleaning
├── exporters/
│   ├── shortcut.py          # .url file writer
│   ├── html_catalog.py      # Self-contained HTML generator
│   └── text_list.py         # Plain-text URL list
├── gui/
│   ├── app.py               # Root window + export pipeline
│   ├── header.py            # URL input + Load Metadata
│   ├── filters.py           # Collapsible filter panel
│   ├── export_opts.py       # Format checkboxes + path selector
│   └── status.py            # Progress bar + scrolling log
└── utils/threading.py       # Background-thread helper
```

## Running Tests

```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```

## Architecture

The project follows a **3-Layer Architecture**:

| Layer | Purpose | Location |
|-------|---------|----------|
| **Directive** | High-level task intent and planning | `directives/` |
| **Orchestration** | Coordination and context management | `Gemini.md` |
| **Execution** | Deterministic scripts and automation | `execution/`, `src/` |

All non-trivial changes require an approved directive before modifying source code.

## Dependencies

| Package | Purpose |
|---------|---------|
| `customtkinter` | Modern themed Tkinter GUI |
| `yt-dlp` | YouTube metadata extraction |
| `Pillow` | Thumbnail resizing and compression |
| `requests` | HTTP thumbnail downloads |
| `tkcalendar` | Date picker widgets |

## License

This project is licensed under the MIT License — see [LICENSE.md](LICENSE.md) for details.
