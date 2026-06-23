#!/usr/bin/env python3
"""little-visitors — génération des illustrations d'oiseaux par LLM.

Squelette de départ. Pour chaque espèce détectée sans illustration, appelle un
générateur d'images (Google Gemini par défaut) avec un style cohérent, et
sauvegarde le résultat dans webapp/assets/illustrations/.

Usage :
    python scripts/generate_illustrations.py                 # espèces manquantes
    python scripts/generate_illustrations.py "European Robin" # une espèce précise

Configuration via .env (voir .env.example) :
    GEMINI_API_KEY, ILLUSTRATION_STYLE, BIRDNET_DB_PATH
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ILLUSTRATIONS_DIR = REPO_ROOT / "webapp" / "assets" / "illustrations"

DEFAULT_STYLE = "minimal flat vector illustration, soft pastel colors"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_env() -> None:
    """Charge .env de façon minimale (sans dépendance externe)."""
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def species_from_db() -> list[dict]:
    """Récupère les espèces détectées depuis la base BirdNET-Pi."""
    db_path = os.environ.get("BIRDNET_DB_PATH", "/home/pi/BirdNET-Pi/scripts/birds.db")
    if not Path(db_path).exists():
        print(f"⚠️  Base introuvable : {db_path} (voir BIRDNET_DB_PATH)", file=sys.stderr)
        return []
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    # Adapte les colonnes au schéma réel de ta base BirdNET-Pi.
    rows = con.execute(
        "SELECT DISTINCT Com_Name AS common, Sci_Name AS scientific FROM detections"
    ).fetchall()
    con.close()
    return [{"common": r["common"], "scientific": r["scientific"]} for r in rows]


def build_prompt(common: str, scientific: str) -> str:
    style = os.environ.get("ILLUSTRATION_STYLE", DEFAULT_STYLE)
    return f"{style}, a {common} ({scientific}), centered, plain background, no text"


def generate_image(prompt: str, out_path: Path) -> bool:
    """Point d'intégration du fournisseur d'images.

    À brancher sur l'API choisie (Google Gemini par défaut). Doit écrire l'image
    dans `out_path` et renvoyer True en cas de succès.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GEMINI_API_KEY manquante (voir .env.example)", file=sys.stderr)
        return False

    # TODO : appeler l'API du fournisseur et sauvegarder l'image dans out_path.
    #        Isolé ici pour pouvoir changer de fournisseur sans toucher au reste.
    print(f"   [stub] prompt = {prompt!r}")
    print(f"   [stub] écrirait → {out_path}")
    return False


def main(argv: list[str]) -> int:
    load_env()
    ILLUSTRATIONS_DIR.mkdir(parents=True, exist_ok=True)

    if len(argv) > 1:
        targets = [{"common": argv[1], "scientific": ""}]
    else:
        targets = species_from_db()

    if not targets:
        print("Aucune espèce à traiter.")
        return 0

    generated = skipped = 0
    for sp in targets:
        out_path = ILLUSTRATIONS_DIR / f"{slugify(sp['common'])}.png"
        if out_path.exists():
            skipped += 1
            continue
        prompt = build_prompt(sp["common"], sp["scientific"])
        print(f"→ {sp['common']}")
        if generate_image(prompt, out_path):
            generated += 1

    print(f"\nTerminé : {generated} générée(s), {skipped} déjà présente(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
