# Directive: Export Modules

## 1. Objective
Create the three output generators: `.url` shortcut files, self-contained offline HTML catalog, and plain-text link list.

## 2. Context & Research (Context-First)
- PRD §6 defines all three output formats precisely.
- `src/core/sanitizer.py` provides `sanitize_filename()` for `.url` filenames.
- `src/core/thumbnail.py` provides `download_and_encode()` for HTML thumbnails.

## 3. Planning & Risk Assessment
- **Risk Level:** MEDIUM — HTML generation involves embedded CSS and Base64 images.

## 4. Execution Steps (Scripts)
1. Create `src/exporters/shortcut.py`.
2. Create `src/exporters/html_catalog.py`.
3. Create `src/exporters/text_list.py`.
4. Write unit tests in `tests/test_exporters.py`.

## 5. Validation Standard
- Unit tests verify file content and structure.
- `.url` files follow the `[InternetShortcut]` format.
- HTML file is self-contained with embedded CSS and Base64 images.

## 6. Expected Deliverables
- Three new modules in `src/exporters/`.
- `tests/test_exporters.py`.

## 7. Failure Handling
- Export errors surface descriptive messages to the GUI status log.
