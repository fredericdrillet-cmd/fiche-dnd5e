#!/usr/bin/env python3
"""Aperçu : affiche chaque description d'un module class_texts annotée par core/formulas (personnage fictif)."""
import importlib, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]
from core.formulas import FormulaContext, annotate
mod = importlib.import_module("class_texts." + sys.argv[1])
cls = {"Rodeur": "Rôdeur"}.get(mod.CLASSE, mod.CLASSE)
ctx = FormulaContext(mods={"Force": 3, "Dextérité": 2, "Constitution": 2, "Intelligence": 1, "Sagesse": 1, "Charisme": 0},
                     prof=3, levels={cls: 7}, current_class=cls, spell_mod=3)
for k, v in mod.BASE.items():
    print(f"[{k}] {annotate(v, ctx)}\n")
for s, t in mod.SUB.items():
    for k, v in t.items():
        print(f"[{s} / {k}] {annotate(v, ctx)}\n")
print(len(mod.AUDIT), "remarques d'audit")
