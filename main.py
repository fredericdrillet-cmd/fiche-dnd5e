#!/usr/bin/env python3
"""
Point d'entrée : générateur et fiche de personnage Donjons & Dragons 5e (PyQt6).

    python main.py                 # utilise le dossier ./data
    python main.py --data /chemin  # dossier de données alternatif
    python main.py --check         # vérifie le chargement des JSON sans ouvrir l'interface
    Fiche_Personnage_DnD5E.exe --check --check-file verif.txt   # même vérification depuis l'exécutable
"""
import argparse
import sys
from pathlib import Path

# Exécutable PyInstaller (--onefile) : les modules sont dans l'archive, pas besoin de corriger le chemin d'import.
# Spyder / IPython : la console garde en mémoire les modules d'un autre projet ouvert avant (un autre dossier
# « core » ou « ui », une ancienne version de l'appli…). On place CE dossier en tête du chemin d'import et on
# oublie les paquets « core » / « ui » qui ne viennent pas d'ici, pour toujours charger les bons fichiers.
_HERE = Path(__file__).resolve().parent
if str(_HERE) in sys.path:
    sys.path.remove(str(_HERE))
sys.path.insert(0, str(_HERE))
for _name in list(sys.modules) if not getattr(sys, "frozen", False) else []:
    if _name.split(".")[0] in ("core", "ui", "tools"):
        _file = getattr(sys.modules[_name], "__file__", None) or ""
        if not _file or not Path(_file).resolve().is_relative_to(_HERE):
            del sys.modules[_name]

from core.data_loader import Database  # noqa: E402
from core.paths import get_resource_path  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fiche de personnage D&D 5e")
    parser.add_argument("--data", default=get_resource_path("data"),
                        help="dossier contenant les fichiers JSON (par défaut : données embarquées)")
    parser.add_argument("--check", action="store_true", help="affiche un résumé de la base et quitte")
    parser.add_argument("--check-file", default="", help="écrit le résumé de --check dans ce fichier "
                        "(utile pour l'exécutable sans console)")
    args = parser.parse_args()

    db = Database(args.data)
    if args.check:
        lines = ["{} classes, {} races, {} historiques, {} sorts, {} armes, {} dons".format(
            len(db.classes), len(db.races), len(db.backgrounds), len(db.spells), len(db.weapons), len(db.feats))]
        lines += ["  ! " + w for w in db.warnings]
        if args.check_file:
            Path(args.check_file).write_text("\n".join(lines) + "\n", encoding="utf-8")
        if sys.stdout is not None:                       # exécutable --windowed : pas de console
            print("\n".join(lines))
        return 0
    try:
        from ui.main_window import run
    except ModuleNotFoundError as exc:
        print("Dépendance manquante :", exc, "\nInstallez-la avec :  pip install -r requirements.txt")
        return 1
    return run(db)


if __name__ == "__main__":
    sys.exit(main())
