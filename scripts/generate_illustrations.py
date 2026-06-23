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

# Poses disponibles. La pose par défaut ("perched") produit le fichier {slug}.png
# attendu par la webapp ; "in flight" peut être généré en complément.
POSES = ("perched", "in flight")
DEFAULT_POSE = "perched"

# Prompt maître pour la génération des illustrations (style kachō-e woodblock).
# Placeholders : {pose}, {com_name}, {sci_name}, {anti_ref_line}.
# La génération attend TROIS images de référence :
#   IMAGE 1 = anatomie/couleurs de l'espèce (photo type guide ornitho)
#   IMAGE 2 = technique de peinture (très peu de marques, aplats)
#   IMAGE 3 = un vrai kachō-e d'époque Edo (style uniquement, autre espèce)
ILLUSTRATION_PROMPT_TEMPLATE = """\
Generate a {pose} {com_name} ({sci_name}) in the style of an Edo-period Japanese kachō-e woodblock print, matching the painting technique of IMAGE 2 closely.

Look at IMAGE 2: the bird is rendered with VERY FEW MARKS. The body is essentially 2-4 flat color zones with sharp boundaries. There is almost no internal texture on the body - no feather-by-feather rendering, no pen-line stippling, no gradient shading. The bird in IMAGE 2 looks like it was painted with maybe 30 brush strokes total. YOUR output should look the same: a few flat color zones, a few confident outline strokes, an accent stroke or two for major wing or tail markings, and that's it.

Confident sumi-e ink linework with soft watercolor washes. Earthy, restrained palette: burnt umber, ochre, indigo, vermillion, muted greens. The body should look like flat painted paper - not a textured surface, not shaded volume. If the species has subtle plumage variation (streaking, mottling, fine barring), ABSTRACT it into 2-3 broad zones rather than rendering it literally. Eye, beak, and feet drawn with crisp ink - these are the only places where confident dark line is appropriate.

The bird sits on a CONSISTENT WARM CREAM tonal background - like aged Japanese mulberry paper, a soft warm buff cream color. The cream ground fills the entire frame as the background and is identical across every print for visual consistency. This is the only background element: NO branch, NO twig, NO perch, NO leaves, NO foliage, NO substrate, NO scenery, NO sky, NO moon, NO water - only the bird floating against the cream paper ground. The perch is purely implied by toe posture - it is NEVER rendered. NO border or frame, NO text or signature.

Composition: the bird occupies one-third to one-half of the frame. Leave generous negative space (just the cream ground) around it. The image should feel sparse and confident, not packed with detail.

The ENTIRE bird must fit within the image frame: head, both wings (fully extended for flight pose), full tail, both legs, both feet, beak. Do NOT crop the wings, tail, legs, or any body part at the edge of the frame. Leave generous padding on all sides.

IMAGE 1 (positive, anatomy) IS {com_name}. Match its proportions, head color, throat, wing pattern, back color, tail pattern, leg color. If the reference shows non-breeding or worn plumage, render the brightest BREEDING (adult-summer) plumage instead - render the most diagnostic, recognizable version of the species.

{anti_ref_line}

IMAGE 3 (positive, style) is a real Edo-period kachō-e woodblock print. The bird in IMAGE 3 is a DIFFERENT species - IGNORE its species, only borrow its painting style. Render the bird in IMAGE 3's painting style. DO NOT copy any compositional elements from IMAGE 3 (branches, leaves, water, moon, scenery).

Treat IMAGE 1 for anatomy and color information ONLY. Treat IMAGE 3 for style ONLY. The output should look like an Edo-period woodblock print of the species in IMAGE 1, painted by the artist of IMAGE 3.

EXACTLY TWO wings (no more, no less - count them: one left, one right). EXACTLY TWO legs. EXACTLY ONE head. EXACTLY ONE beak. EXACTLY ONE tail.

Posture, color, markings, and body proportions match IMAGE 1 / {com_name} field-guide references.

Pay particular attention to species-specific patterns. Do NOT default to generic markings: if the reference shows a uniformly dark head, do NOT add a white face mask. If the reference shows solid wings, do NOT add white wingbars. If the reference has no crest, do NOT add a crest.

For close-relative species (multiple goldfinch, multiple jay, multiple sparrow species in the library), render the diagnostic differences clearly so the species are visibly distinguishable from each other.

BOTH FEET visible at the bottom of the body.

Songbird feet are SMALL relative to the body. Tarsi (legs below the feathers) are roughly 10-15% of body height for finches/sparrows/warblers/chickadees, 15-20% for jays/thrushes/mockingbirds. For larger birds (ducks, hawks, owls), match the proportion in the reference photo - typically still under 25%.

Draw slim tarsi, small delicate toes. Do NOT exaggerate feet or claws; the bird is not a chicken or a crab.

Match foot proportion to the attached reference photo.
PERCHED (pose 1): one wing folded against the body, the other tucked behind. Both feet visible at the bottom, toes curled gently forward as if grasping a thin perch - but the perch itself is NOT drawn. The bird floats in space, posture suggesting it's perched.

IN FLIGHT (pose 2): both wings fully extended in a natural flapping position. Legs and feet either (a) tucked tight against the belly with toes folded out of sight, or (b) extended straight back along the line of the tail. Do NOT dangle the feet below the body with toes splayed.

Render at high resolution on a fully transparent background. Cut the bird out cleanly. No shadow, no paper texture, no caption.\
"""


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


def build_prompt(
    common: str,
    scientific: str,
    pose: str = DEFAULT_POSE,
    anti_ref_line: str = "",
) -> str:
    """Construit le prompt kachō-e pour une espèce et une pose données.

    `anti_ref_line` est une ligne optionnelle de référence négative, utile pour
    distinguer une espèce proche (ex. : "IMAGE 4 (negative) is the Lesser
    Goldfinch - do NOT copy its markings"). Laissée vide par défaut.
    """
    return (
        ILLUSTRATION_PROMPT_TEMPLATE
        .replace("{pose}", pose)
        .replace("{com_name}", common)
        .replace("{sci_name}", scientific)
        .replace("{anti_ref_line}", anti_ref_line)
    )


def generate_image(prompt: str, out_path: Path) -> bool:
    """Point d'intégration du fournisseur d'images.

    À brancher sur l'API choisie (Google Gemini par défaut). Doit écrire l'image
    dans `out_path` et renvoyer True en cas de succès.

    Le prompt kachō-e référence TROIS images : il faut donc transmettre au
    modèle, en plus du texte, les références IMAGE 1 (anatomie de l'espèce),
    IMAGE 2 (technique de peinture) et IMAGE 3 (style kachō-e). Gemini accepte
    des images en entrée aux côtés du texte.
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
