# 04 — Illustrations d'oiseaux générées par LLM

Chaque espèce détectée reçoit une **illustration** générée par un LLM/IA générative
d'images. Par défaut on utilise **Google Gemini** (comme AvianVisitors), mais le script est
pensé pour pouvoir changer de fournisseur.

## Principe

1. On récupère la **liste des espèces détectées** (depuis `birds.db` ou l'UI BirdNET-Pi).
2. Pour chaque espèce **sans illustration**, on appelle l'API du LLM avec un prompt cadré
   par un **style cohérent** (variable `ILLUSTRATION_STYLE` du `.env`).
3. L'image est sauvegardée dans `webapp/assets/illustrations/<nom_espece>.png`.
4. Le dashboard l'affiche automatiquement.

## Configuration

Dans `.env` :

```dotenv
GEMINI_API_KEY=xxxxxxxxxxxx
```

> 🔑 La clé du LLM est un secret → `.env` uniquement, jamais committée.
> Le style n'est plus défini par une variable d'env : il est figé dans le prompt
> maître (`ILLUSTRATION_PROMPT_TEMPLATE`) pour garantir une collection cohérente.

## Génération

```bash
python scripts/generate_illustrations.py            # toutes les espèces manquantes
python scripts/generate_illustrations.py "European Robin"   # une espèce précise
```

Le script (`scripts/generate_illustrations.py`) est un **squelette** :
- il lit la config depuis `.env` ;
- il évite de régénérer une illustration déjà présente (idempotent) ;
- il construit le prompt via `build_prompt(common, scientific, pose, anti_ref_line)` ;
- le point d'appel au fournisseur est isolé dans une fonction `generate_image()` à brancher
  sur l'API choisie.

## Style des illustrations : kachō-e (estampe japonaise)

Le style visé est celui d'une **estampe sur bois japonaise d'époque Edo** (kachō-e) :
linework à l'encre sumi-e, aplats de couleur, palette terreuse (umber, ocre, indigo,
vermillon, verts assourdis), oiseau **détouré sur fond crème** uniforme, **sans décor**
(pas de branche, feuille, eau, lune…), fond **transparent** en sortie.

Le prompt complet vit dans `ILLUSTRATION_PROMPT_TEMPLATE` (dans le script). Ses variables :

| Variable | Rôle |
|----------|------|
| `{pose}` | `perched` (perché) ou `in flight` (en vol) |
| `{com_name}` | nom commun de l'espèce |
| `{sci_name}` | nom scientifique |
| `{anti_ref_line}` | ligne optionnelle de **référence négative** pour distinguer une espèce proche |

### Les TROIS images de référence

Le prompt s'appuie sur trois images à transmettre au modèle **en plus du texte** :

| Image | Rôle | Contenu |
|-------|------|---------|
| **IMAGE 1** | Anatomie & couleurs | Photo de l'espèce (type guide ornitho) — proportions, motifs, couleurs |
| **IMAGE 2** | Technique de peinture | Exemple « très peu de marques » : 2-4 aplats, ~30 coups de pinceau |
| **IMAGE 3** | Style | Un vrai kachō-e d'époque Edo (autre espèce — on n'emprunte que le style) |

> IMAGE 1 sert **uniquement** pour l'anatomie/couleurs, IMAGE 3 **uniquement** pour le
> style. Aucun élément de décor d'IMAGE 3 ne doit être copié.

## Conseils

- Le style est **figé** dans le prompt → collection visuellement cohérente d'office.
- Toujours fournir le **nom scientifique** (désambiguïse les espèces proches).
- Pour deux espèces proches (chardonnerets, geais…), renseigner `anti_ref_line` pour
  forcer le rendu des **différences diagnostiques**.
- Sortie en **fond transparent** (`{slug}.png`) → rendu propre dans la grille du dashboard.

## Alternatives de fournisseur

Le pipeline est agnostique : on peut brancher un autre générateur d'images à la place de
Gemini en ne modifiant que la fonction `generate_image()` dans le script. À choisir selon
disponibilité, coût et qualité.

## Bonnes pratiques

- Les illustrations générées sont **régénérables** → le dossier `generated/` est dans
  `.gitignore` pour ne pas alourdir le dépôt. Garde éventuellement un petit set d'exemples.
- Vérifie les **conditions d'utilisation** du fournisseur pour un usage personnel/public.
