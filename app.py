#!/usr/bin/env python3
"""
Fichier principal de l'application WEB (fiche de personnage D&D 5e).

    Développement :  python app.py                 -> http://localhost:8000
    Production    :  gunicorn app:app              (Render, Railway, Fly.io, Hugging Face Spaces…)

L'application bureau (PyQt6) reste disponible via `python main.py`.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web.app import app  # noqa: E402  (exposé pour gunicorn : « app:app »)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Fiche D&D 5e — http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
