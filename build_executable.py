#!/usr/bin/env python3
"""
Compilation de l'exécutable Windows autonome : dist/Fiche_Personnage_DnD5E.exe

À lancer SOUS WINDOWS (PyInstaller ne fabrique un .exe que sur Windows) :

    python build_executable.py              # tests, compilation, vérification, journal
    python build_executable.py --sans-tests # compilation directe
    python build_executable.py --installer  # installe d'abord PyInstaller et PyQt6 (pip)
    python build_executable.py --simulation # affiche la commande PyInstaller sans compiler (toute plateforme)

Étapes :
  1. vérifications (Windows, Python, PyInstaller, PyQt6, dossier data/, icône) ;
  2. tests unitaires (interface simulée) — la compilation est annulée s'ils échouent ;
  3. PyInstaller --onefile --windowed, avec les données (data/) et les ressources (assets/) embarquées et l'icône ;
  4. placement : l'exécutable généré remplace celui de dist/ ;
  5. vérification : l'exécutable est lancé avec --check (lecture des données embarquées) ;
  6. journal : dist/journal_build.txt (date, version, taille, durée, résultat).

Les données embarquées sont en lecture seule ; les réglages de l'utilisateur sont écrits hors de l'exécutable
(dossier personnel), et toute donnée modifiable passe par core.paths.working_copy() (copie de travail locale).
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "Fiche_Personnage_DnD5E"
DIST = ROOT / "dist"
WORK = ROOT / "build"
DATA_DIRS = ["data", "assets"]                      # embarqués avec --add-data
ICON = ROOT / "assets" / "app_icon.ico"
LOG = DIST / "journal_build.txt"


class Journal:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def __call__(self, msg: str) -> None:
        stamp = dt.datetime.now().strftime("%H:%M:%S")
        line = "[{}] {}".format(stamp, msg)
        self.lines.append(line)
        print(line, flush=True)

    def save(self) -> None:
        DIST.mkdir(exist_ok=True)
        LOG.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


log = Journal()


def app_version() -> str:
    """Dernière version listée dans le README (« ## Nouveautés vNN »)."""
    import re
    try:
        nums = [int(n) for n in re.findall(r"^## Nouveautés v(\d+)", (ROOT / "README.md").read_text(encoding="utf-8"),
                                           re.M)]
    except OSError:
        nums = []
    return "v{}".format(max(nums)) if nums else "inconnue"


def pip_install(packages: list[str]) -> None:
    log("Installation : " + ", ".join(packages))
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + packages)


def check_prerequisites(simulation: bool) -> list[str]:
    problems = []
    log("Python {} — {} {}".format(platform.python_version(), platform.system(), platform.release()))
    if platform.system() != "Windows" and not simulation:
        problems.append("Ce script doit être lancé sous Windows : PyInstaller produit un exécutable pour le système "
                        "sur lequel il tourne (un .exe ne se fabrique que sous Windows).")
    for mod, pkg in (("PyInstaller", "pyinstaller"), ("PyQt6", "PyQt6")):
        try:
            __import__(mod)
            log("✔ {} présent".format(pkg))
        except ImportError:
            msg = "{} manquant : python -m pip install {} (ou relancez avec --installer)".format(pkg, pkg)
            (log if simulation else problems.append)(("⚠ " if simulation else "") + msg)
    for d in DATA_DIRS:
        if not (ROOT / d).is_dir():
            problems.append("Dossier introuvable : {}".format(d))
    log("Icône : {}".format(ICON.name if ICON.exists() else "absente (icône par défaut de Windows)"))
    return problems


def run_tests() -> bool:
    log("Tests unitaires…")
    t0 = time.time()
    res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (res.stderr or res.stdout).strip().splitlines()[-3:]
    for line in tail:
        log("   " + line)
    log("Tests {} en {:.0f} s".format("réussis" if res.returncode == 0 else "EN ÉCHEC", time.time() - t0))
    return res.returncode == 0


def pyinstaller_args() -> list[str]:
    sep = ";" if os.name == "nt" else ":"              # séparateur de --add-data (Windows : « ; »)
    args = ["--noconfirm", "--clean", "--onefile", "--windowed", "--name", APP_NAME,
            "--distpath", str(WORK / "sortie"), "--workpath", str(WORK / "travail"), "--specpath", str(WORK)]
    for d in DATA_DIRS:
        args += ["--add-data", "{}{}{}".format(ROOT / d, sep, d)]
    if ICON.exists():
        args += ["--icon", str(ICON)]
    # modules de test et outils de développement : hors de l'exécutable
    for mod in ("tests", "qt_stub", "tkinter", "unittest", "pydoc"):
        args += ["--exclude-module", mod]
    args.append(str(ROOT / "main.py"))
    return args


def build() -> Path:
    import PyInstaller.__main__  # noqa: N813
    log("Compilation PyInstaller (--onefile --windowed)…")
    t0 = time.time()
    PyInstaller.__main__.run(pyinstaller_args())
    built = WORK / "sortie" / (APP_NAME + (".exe" if os.name == "nt" else ""))
    if not built.exists():
        raise RuntimeError("Exécutable non généré : {}".format(built))
    DIST.mkdir(exist_ok=True)
    target = DIST / built.name
    if target.exists():
        target.unlink()                                  # l'ancienne version est écrasée
    shutil.move(str(built), str(target))
    log("✔ Exécutable : {} ({:.1f} Mo) en {:.0f} s".format(target.relative_to(ROOT), target.stat().st_size / 1e6,
                                                         time.time() - t0))
    return target


def verify(exe: Path) -> bool:
    """Lance l'exécutable en mode --check : prouve que les données embarquées sont lisibles."""
    out = WORK / "verification.txt"
    if out.exists():
        out.unlink()
    log("Vérification : {} --check".format(exe.name))
    try:
        subprocess.run([str(exe), "--check", "--check-file", str(out)], timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        log("✖ Lancement impossible : {}".format(exc))
        return False
    if not out.exists():
        log("✖ Aucun résultat de vérification (données embarquées illisibles ?)")
        return False
    for line in out.read_text(encoding="utf-8").splitlines():
        log("   " + line)
    return True


def main() -> int:
    for stream in (sys.stdout, sys.stderr):              # console Windows (cp1252) : accents et ✔ ✖ sans erreur
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Compilation de l'exécutable Windows de la fiche D&D 5e")
    parser.add_argument("--sans-tests", action="store_true", help="ne lance pas les tests avant la compilation")
    parser.add_argument("--installer", action="store_true", help="installe PyInstaller et PyQt6 avant de compiler")
    parser.add_argument("--simulation", action="store_true", help="affiche la commande sans compiler")
    args = parser.parse_args()

    log("=== Build {} — version {} — {} ===".format(APP_NAME, app_version(), dt.datetime.now().strftime("%d/%m/%Y")))
    if args.installer:
        pip_install(["pyinstaller", "PyQt6"])
    problems = check_prerequisites(args.simulation)
    if args.simulation:
        log("Commande : pyinstaller " + " ".join('"{}"'.format(a) if " " in a else a for a in pyinstaller_args()))
        log("Simulation terminée : aucun fichier généré.")
        return 0
    if problems:
        for p in problems:
            log("✖ " + p)
        log("BUILD ANNULÉ")
        log.save()
        return 1
    if not args.sans_tests and not run_tests():
        log("BUILD ANNULÉ : corrigez les tests ou relancez avec --sans-tests")
        log.save()
        return 1
    try:
        exe = build()
    except Exception as exc:                            # noqa: BLE001 - journalisé puis code d'erreur
        log("✖ Échec de la compilation : {}".format(exc))
        log("BUILD EN ÉCHEC")
        log.save()
        return 1
    ok = verify(exe)
    log("BUILD RÉUSSI : {}".format(exe.relative_to(ROOT)) if ok else "BUILD TERMINÉ, VÉRIFICATION EN ÉCHEC")
    log.save()
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
