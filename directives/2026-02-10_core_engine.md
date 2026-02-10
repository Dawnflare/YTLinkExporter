# Directive: Core Extraction Engine

## 1. Objective
Build the yt-dlp extraction wrapper, video filtering logic, and thumbnail download/encode pipeline.

## 2. Context & Research (Context-First)
- `src/core/sanitizer.py` already exists from Directive 1.
- PRD §5.1: use `extract_flat=True`, skip deleted/private, support cookies.txt.
- PRD §5.2: thumbnails resized to 320px max width, Base64-encoded.

## 3. Planning & Risk Assessment
- **Risk Level:** MEDIUM — depends on yt-dlp API behaviour and network I/O.

## 4. Execution Steps (Scripts)
1. Create `src/core/extractor.py` with `extract_playlist()`.
2. Create `src/core/filters.py` with `apply_filters()`.
3. Create `src/core/thumbnail.py` with `download_and_encode()`.

## 5. Validation Standard
- Unit tests in `tests/test_sanitizer.py` and `tests/test_filters.py` pass.
- `extractor.py` can be imported without errors.

## 6. Expected Deliverables
- Three new modules in `src/core/`.
- Test files in `tests/`.

## 7. Failure Handling
- Network-dependent tests are skipped by default (use `@pytest.mark.network`).
