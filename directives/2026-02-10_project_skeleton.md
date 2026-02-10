# Directive: Project Skeleton & Dependencies

## 1. Objective
Establish the foundational project structure, dependency manifest, virtual environment, and the first two utility modules (`settings.py`, `sanitizer.py`).

## 2. Context & Research (Context-First)
- `src/` is currently empty. No prior code exists.
- PRD specifies: Python 3.10+, CustomTkinter GUI, yt-dlp backend, Pillow for images.
- Gemini.md mandates files only in `src/`, `directives/`, `execution/`, `.tmp/`.

## 3. Planning & Risk Assessment
- **Risk Level:** LOW — new files only, no modifications to existing code.

## 4. Execution Steps (Scripts)
1. Create `requirements.txt` at project root.
2. Create virtual environment (`.venv`).
3. Install dependencies.
4. Create package tree under `src/` with `__init__.py` files.
5. Create `src/main.py` (stub entry point).
6. Create `src/config/settings.py`.
7. Create `src/core/sanitizer.py`.

## 5. Validation Standard
- `python -c "import customtkinter; import yt_dlp; import PIL; print('OK')"` succeeds in venv.
- `python src/main.py --help` or a dry import succeeds without errors.

## 6. Expected Deliverables
- `requirements.txt`
- Full `src/` package tree (all `__init__.py`)
- `src/main.py`, `src/config/settings.py`, `src/core/sanitizer.py`
- Venv created and deps installed

## 7. Failure Handling
- If `pip install` fails, check network or version constraints.
