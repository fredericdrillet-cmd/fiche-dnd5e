"""
Application web Flask — fiche de personnage D&D 5e.

Routes :
  GET  /                      interface mobile (web/static/index.html)
  GET  /api/catalog           listes de choix (classes, espèces, sorts, objets, thèmes…)
  POST /api/character         {"character": {...} | null, "ops": [...]} -> personnage + fiche calculée
  POST /api/levelup          assistant de montée de niveau (rejoué à chaque requête, confirm=true pour valider)
  POST /api/export/text       {"character": {...}} -> fiche lisible (.txt / Markdown)
  POST /api/spell             {"nom": "...", "character": {...}?} -> détail d'un sort
  POST /api/roll              {"expression": "2d6+3"} -> lancer de dés
  GET  /api/race-image?race=…&sous_race=…   illustration de l'espèce (data/images/races)
  GET  /healthz               sonde de santé (hébergeur)
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request, send_file, send_from_directory

from core import race_images
from . import levelup as LU
from . import service as S

STATIC = Path(__file__).resolve().parent / "static"
MAX_BODY = 4 * 1024 * 1024          # 4 Mo : un personnage avec portrait tient largement

app = Flask(__name__, static_folder=str(STATIC), static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = MAX_BODY
app.json.ensure_ascii = False
app.json.sort_keys = False


# ------------------------------------------------------------------------------------------ compression gzip
@app.after_request
def _compress(resp: Response) -> Response:
    """Réponses JSON / texte compressées (réseau mobile) — sans dépendance supplémentaire."""
    if (resp.status_code < 200 or resp.status_code >= 300 or resp.direct_passthrough
            or "gzip" not in request.headers.get("Accept-Encoding", "")
            or "Content-Encoding" in resp.headers
            or not (resp.mimetype or "").startswith(("application/json", "text/", "application/javascript"))):
        return resp
    data = resp.get_data()
    if len(data) < 1024:
        return resp
    resp.set_data(gzip.compress(data, compresslevel=6))
    resp.headers["Content-Encoding"] = "gzip"
    resp.headers["Vary"] = "Accept-Encoding"
    resp.headers["Content-Length"] = str(len(resp.get_data()))
    return resp


def _body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, "Requête JSON attendue.")
    return data


@app.errorhandler(400)
@app.errorhandler(413)
def _bad_request(err):
    msg = getattr(err, "description", "") or "Requête invalide."
    if getattr(err, "code", 400) == 413:
        msg = "Fichier trop volumineux (4 Mo maximum)."
    return jsonify({"error": msg}), getattr(err, "code", 400)


# ------------------------------------------------------------------------------------------ pages
@app.get("/")
def index():
    resp = send_from_directory(STATIC, "index.html")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/manifest.webmanifest")
def manifest():
    return send_from_directory(STATIC, "manifest.webmanifest", mimetype="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    resp = send_from_directory(STATIC, "sw.js", mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/healthz")
def healthz():
    S.get_db()
    return {"ok": True}


# ------------------------------------------------------------------------------------------ API
_CATALOG_ETAG: str | None = None


@app.get("/api/catalog")
def api_catalog():
    global _CATALOG_ETAG
    cat = S.catalog()
    if _CATALOG_ETAG is None:
        _CATALOG_ETAG = hashlib.sha1(json.dumps(cat, sort_keys=True).encode()).hexdigest()[:16]
    if request.headers.get("If-None-Match") == _CATALOG_ETAG:
        return Response(status=304)
    resp = jsonify(cat)
    resp.headers["ETag"] = _CATALOG_ETAG
    resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp


@app.post("/api/character")
def api_character():
    data = _body()
    ops = data.get("ops") or []
    if not isinstance(ops, list) or len(ops) > 200:
        abort(400, "Liste d'opérations invalide.")
    try:
        return jsonify(S.apply(data.get("character"), ops))
    except S.ActionError as exc:
        return jsonify({"error": str(exc)}), 422


@app.post("/api/levelup")
def api_levelup():
    """Assistant de montée de niveau : {"character", "classe", "ops": [...], "confirm": bool}."""
    data = _body()
    ops = data.get("ops") or []
    if not isinstance(ops, list) or len(ops) > 300:
        abort(400, "Liste de choix invalide.")
    try:
        return jsonify(LU.wizard(data.get("character") or {}, str(data.get("classe") or ""), ops,
                                 bool(data.get("confirm"))))
    except S.ActionError as exc:
        return jsonify({"error": str(exc)}), 422


@app.post("/api/export/text")
def api_export_text():
    data = _body()
    try:
        text = S.text_sheet(data.get("character") or {})
    except S.ActionError as exc:
        return jsonify({"error": str(exc)}), 422
    return Response(text, mimetype="text/plain; charset=utf-8")


@app.post("/api/spell")
def api_spell():
    data = _body()
    try:
        return jsonify(S.spell_details(str(data.get("nom", "")), data.get("character")))
    except S.ActionError as exc:
        return jsonify({"error": str(exc)}), 404


@app.post("/api/roll")
def api_roll():
    try:
        return jsonify(S.roll_expression(str(_body().get("expression", ""))[:60]))
    except S.ActionError as exc:
        return jsonify({"error": str(exc)}), 422


@app.get("/api/race-image")
def api_race_image():
    path = race_images.find_race_image(request.args.get("race", ""), request.args.get("sous_race", ""))
    if not path:
        abort(404)
    resp = send_file(path, max_age=7 * 24 * 3600)
    return resp


if __name__ == "__main__":                      # développement : python -m web.app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
