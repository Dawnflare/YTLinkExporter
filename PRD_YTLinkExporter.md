# Product Requirements Document (PRD): YTLinkExporter

## 1. Overview

**Product Name:** YTLinkExporter

**Version:** 1.0

**Status:** Draft

**Platform:** Windows Desktop Application

**YTLinkExporter** is a specialized archiving tool designed to extract, organize, and export metadata and links from YouTube playlists and channels. It leverages the power of `yt-dlp` in a user-friendly GUI to generate offline archives in multiple formats (Shortcuts, Offline Visual HTML Catalogs, and Text Lists).

## 2. Problem Statement

Users frequently wish to "back up" or organize playlists and channels for future reference but do not have the storage space or bandwidth to download terabytes of video files. Existing tools often require online connectivity to view thumbnails or are difficult to use. Users need a completely offline, fast way to generate accessible indexes of their favorite content.

## 3. Key Features

### 3.1 Core Functionality

- **Multi-Format Export:**
  - **Windows Shortcuts (`.url`):** Individual files for each video that launch the default browser. Useful for organizing into folders.
  - **Offline Visual HTML Catalog (`.html`):** A single, self-contained file containing a table/grid of video thumbnails, titles, upload dates, and direct links. **Thumbnails are embedded directly into the file** for offline viewing.
  - **Plain Text List (`.txt`):** A simple line-by-line list of URLs for use in other tools.
- **Batch Processing:** Capable of handling individual channels or playlists containing thousands of videos.
- **Metadata Extraction:** Retrieves Title, URL, Thumbnail (Binary Data), and Upload Date.

### 3.2 Filtering & Scope

- **Date Range:** Ability to export videos only within a specific start and end date.
- **Quantity Limit:** Option to export only the "Last X" videos (e.g., the 10 most recent).
- **Keyword Filtering:** Include or exclude videos based on specific text in the title (e.g., "Review", "Tutorial").

### 3.3 Configuration

- **Cookie Support:** Integrated support for a `cookies.txt` file to access age-gated content or bypass "403 Forbidden" errors.
- **Custom Save Locations:**
  - Persistent default save folder (stored in settings).
  - Option to override save folder per export.

## 4. User Interface (GUI) Requirements

### 4.1 Design Philosophy

- **Framework:** `CustomTkinter` (Python).
- **Aesthetics:** Modern, clean, distinct from standard "gray" Windows forms. Support for System Theme (Dark/Light).

### 4.2 Layout Specification

- **Header Section:**
  - **Input Field:** Large text entry for `Playlist/Channel URL`.
  - **"Load Metadata" Button:** Fetches the playlist title/thumbnail to verify the link validity before processing.
- **Filter Section (Collapsible/Grouped):**
  - **Date Pickers:** Start Date / End Date.
  - **Count Limit:** Numeric input (Default: All).
  - **Keyword Filter:** Text input.
- **Export Options Section:**
  - **Checkboxes:**
    - `[ ] Generate Shortcut Files (.url)`
    - `[ ] Generate Offline HTML Catalog (.html)`
    - `[ ] Generate Text List (.txt)`
  - **Path Selection:** Text field showing current path + "Browse" button.
- **Action Section:**
  - **"Export" Button:** Primary call-to-action (Disabled until URL is valid).
  - **Progress Bar:** Visual indicator of extraction and thumbnail downloading progress.
  - **Status Log:** A scrolling text area showing current operations (e.g., "Downloading thumbnail for video 15/50...").

## 5. Technical Requirements

### 5.1 Backend Architecture

- **Engine:** Python 3.10+ using the `yt_dlp` library wrapper.
- **Extraction Method:** `extract_flat=True`.
- **Sanitization:** Strict filename sanitization logic to strip Windows-illegal characters (`< > : " / \ | ? *`) from video titles before creating `.url` files.

### 5.2 Data Handling (Offline Thumbnails)

- **Image Processing:**
  - The app must download the thumbnail image for every video (using `requests` or `yt-dlp`).
  - Images must be resized/compressed (max width 320px) to prevent the HTML file from becoming hundreds of megabytes in size.
  - Images must be converted to **Base64 strings** and embedded into the HTML `<img>` tags.
- **HTML Structure:** A responsive table layout using embedded CSS.

### 5.3 Performance

- **Threading:** The `yt-dlp` extraction and thumbnail downloading must run on background threads to keep the GUI responsive.

## 6. Output Format Specifications

### 6.1 Windows Shortcut (`.url`)

**Filename:** `{UploadDate} - {SanitizedTitle}.url`

**Content:**

```
[InternetShortcut]
URL=[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=){VideoID}
```

### 6.2 Offline HTML Catalog (`.html`)

**Filename:** `{PlaylistName}.html`

**Structure:**

- Single file (no external folders).
- **Grid Layout:**
  - **Image:** Base64 encoded JPEG/WEBP.
  - **Metadata:** Title (Link), Date, Duration.

### 6.3 Text List (`.txt`)

**Filename:** `{PlaylistName}_links.txt`

**Content:**

```
[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=){VideoID_1}
[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=){VideoID_2}
...
```

## 7. Edge Cases & Error Handling

- **Invalid URL:** App must detect non-YouTube URLs and display a red error label.
- **Private/Deleted Videos:** The extractor must skip "Deleted Video" entries without crashing.
- **Network Failure:** If internet cuts out, show a "Connection Failed" popup.
- **Permission Error:** If the app cannot write to the selected folder, prompt user to choose a different location.

## 8. Future Roadmap (Post-v1.0)

- **CSV Export:** For importing into spreadsheets/databases.
- **Auto-Scheduler:** Run silently in the background to archive new links from a channel daily.