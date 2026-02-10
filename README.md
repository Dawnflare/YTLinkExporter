# YTLinkExporter

A Windows desktop application for archiving YouTube playlists and channels without downloading video files. Built with **Python**, **CustomTkinter**, and **yt-dlp**.

## Features

- **Multi-Format Export**
  - **Windows Shortcuts (`.url`)** — one file per video, opens in your default browser.
  - **Offline HTML Catalog (`.html`)** — responsive grid with embedded Base64 thumbnails for fully offline viewing.
  - **Plain Text List (`.txt`)** — one URL per line for use with other tools.
- **Smart Filtering & High Performance**
  - **Dynamic Extraction**: Choose between **Flat Mode** (instant loading of titles/URLs) and **Full Mode** (deep crawl for upload dates and channel info).
  - **Date Range Filters**: Filter by upload date with a dedicated toggle to optimize extraction speed.
  - **Quick-Select Presets**: Buttons for 1W, 1M, 6M, 1Y, and "Today" to instantly set date ranges.
  - **Keyword matching**: Case-insensitive substring matching (include or exclude).
- **Automated Organization**
  - **Export to Subfolder**: Automatically organizes files into a folder named after the playlist or channel.
  - **Filename Sanitization**: Handles illegal characters and reserved Windows names automatically.
- **Batch Processing** — handles playlists and channels with thousands of videos.
- **Cookie Support** — access age-gated or restricted content via a `cookies.txt` file.
- **Persistent Settings** — remembers your default save folder, cookies path, and theme.
- **Modern UI** — dark/light theme support with a responsive layout optimized for long status logs.

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

## Configuration

The application stores preferences in a `settings.json` file in the project root. This file is created automatically on first launch.

### Settings that auto-save from the GUI

| Setting | How it's set |
|---------|-------------|
| **Save Location** | Click "Browse…" next to Save Location — your choice is remembered for next launch |
| **Cookies File** | Click "Browse…" next to Cookies File — used for age-gated or restricted content |

### Manual editing

You can also edit `settings.json` directly:

```json
{
  "default_save_path": "C:\\Users\\YourName\\Downloads\\MyYTArchive",
  "cookies_path": "C:\\Users\\YourName\\cookies.txt",
  "theme": "dark"
}
```

| Key | Values | Description |
|-----|--------|-------------|
| `default_save_path` | Any valid folder path | Where exports are saved |
| `cookies_path` | Path to a `cookies.txt` file, or `""` | Enables access to restricted videos |
| `theme` | `"system"`, `"dark"`, or `"light"` | Application color theme |

*Note: Use double backslashes `\\` for Windows paths in JSON.*

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
