# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

D&D 5e character sheet & generator, entirely in French (code comments, UI strings, data, docs, commit messages). Two front-ends share one rules engine: a PyQt6 desktop app and a Flask mobile web app (PWA).

## Commands

```bash
pip install -r requirements.txt           # web (Flask, gunicorn)
pip install -r requirements-desktop.txt   # desktop (PyQt6)
python app.py                             # web app on http://localhost:8000 (FLASK_DEBUG=1 for debug)
python main.py                            # desktop app
python main.py --check                    # load/validate all JSON in data/ without opening the UI
python -m unittest discover tests         # full suite (~640 tests, ~90 s); no PyQt6 or display needed
python -m unittest tests.test_web         # one module
python -m unittest tests.test_web.ServiceTests.test_new_character   # one test
python build_executable.py --simulation   # show the PyInstaller command (real build is Windows-only)
```

Production: `gunicorn app:app` (Procfile, render.yaml with `/healthz`, Dockerfile). CI (`.github/workflows/build-exe.yml`) runs `build_executable.py` on Windows on every push: it runs the tests, then builds `dist/Fiche_Personnage_DnD5E.exe` — failing tests block the build.

## Architecture

- **`core/`** — pure rules logic, **no UI dependency**. `Database` (`data_loader.py`) loads, repairs (e.g. missing commas between objects) and cross-links every JSON in `data/`. `Character` (`character.py`) is a plain dataclass holding only user state + JSON save/load — no rule calculations. `Engine(db, char)` (`engine.py`) computes all derived values and exposes business commands; it is assembled from many mixins (`class_actions`, `combat_flow`, `levelup`, `turn`, `equipment`, `invocations`, `spell_swap`, `magic_gear`, …), so a feature usually lives in its own `core/*.py` mixin. `@memo` methods cache only inside `with engine.batch():`. `Engine.normalize()` migrates old saves (renamed races/subclasses, see `NAME_MIGRATIONS`/`RACE_RENAMED`) and must keep old saves loadable.
- **`ui/`** — PyQt6 desktop, roughly one file per tab, `main_window.py` wires them. Only the visible tab is recalculated. `ui/theme.py` is pure Python (no Qt import) and also supplies the 10 themes to the web app; theme colors are `Theme` fields injected into one stylesheet, and tests audit WCAG AA contrast (≥ 4.5:1) of every theme.
- **Desktop-only v48–v51 features** (`core/creation.py`, `core/class_guide.py`, `ui/creation_wizard.py`, `ui/class_guide_panel.py`, `ui/spell_inspector.py`): BG3-style level-1 creation wizard, class guide, and a *Mode guidé* (default; locks class/level/name edits, changes go through « Niveau supérieur ») vs *Mode libre* (Options). The web app does not expose the wizard but shares `core/levelup.py`, so changes there must keep `web/levelup.py` working (`tests/test_web.py`).
- **Editions & table rules (v52)** — `core/editions.py` (modes `2014` / `2024` / `libre`, `filter_items`, `badge`, `EditionCatalog` over `data/editions/*.json`, cross-edition multiclass spell slots) and `core/house_rules.py` (registry `RULES`, per-mode defaults). State lives in the character: `edition_mode`, `regles_optionnelles`, `edition` on each class entry; old saves get `HR.LEGACY` (pre-v52 behaviour). Gate optional mechanics with `Engine.rule_active(key)`. `data/editions/` is NOT read by the main loader (`data/*.json` only); it is the 2014+2024 reference set, accessed via `Database.editions`. See `ARCHITECTURE_EDITIONS_v52.md`.
- **`web/`** — stateless server. The character lives in the browser (localStorage) in the **same JSON format as the desktop save**; each request sends `{"character": …, "ops": [...]}` to `/api/character`. `web/service.apply()` rebuilds `Engine`, runs each op, normalizes, and returns the character plus a computed `sheet` (`build_sheet`). Ops are `Controller.op_<name>` methods auto-registered into `OPS`; raise `ActionError` for user-facing errors. Adding a web feature = new `op_*` in `web/service.py` + sheet fields in `build_sheet` + UI in `web/static/app.js` (vanilla JS, no build step). `web/levelup.py` replays `core/levelup.py` on every request (`confirm=true` commits). Keep desktop and web behavior in sync: web ops mirror the handlers in `ui/*.py`.
- **`data/`** — editable JSON database. Files are recognised by **content**, not filename. `Sorts_Listes.json` and `Bonus_Raciaux.json` are project additions (spell class lists, racial bonuses/subraces). Images in `data/images/`.
- **`tools/`** — one-off/idempotent data generators and fixers that rewrite `data/*.json` (e.g. `apply_class_texts.py` applies `tools/class_texts/<classe>.py` descriptions; `build_spell_lists.py`, `split_magic_items.py`, `audit_regles.py`). Many support `--check`.
- **Paths** — always go through `core/paths.py`: `get_resource_path()` for read-only resources (works from source and from the PyInstaller `_MEIPASS` bundle), `user_data_dir()` / `working_copy()` for anything written (settings go to `%APPDATA%\Fiche_DnD5E` or `~/.dnd5e_fiche`). Never write next to bundled data.

## Tests

- `tests/qt_stub.py` installs a fake PyQt6 so UI code (construction, refreshes, handlers) runs headless; it checks Python logic, not the real Qt API. UI tests call `qt_stub.install()` before importing `ui.*`.
- `tests/test_web.py` skips Flask route tests when Flask isn't installed.
- Tests are grouped by release (`test_vNN_*.py`); the project version history is documented in `RAPPORT_*_vNN.md` reports and `README.md` ("Nouveautés vN"). `AUDIT_REGLES.md` lists known structural deviations from official rules.
