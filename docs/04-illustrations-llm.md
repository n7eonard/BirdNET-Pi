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
ILLUSTRATION_STYLE=minimal flat vector illustration, soft pastel colors
```

> 🔑 La clé du LLM est un secret → `.env` uniquement, jamais committée.

## Génération

```bash
python scripts/generate_illustrations.py            # toutes les espèces manquantes
python scripts/generate_illustrations.py "European Robin"   # une espèce précise
```

Le script (`scripts/generate_illustrations.py`) est un **squelette** :
- il lit la config depuis `.env` ;
- il évite de régénérer une illustration déjà présente (idempotent) ;
- le point d'appel au fournisseur est isolé dans une fonction `generate_image()` à brancher
  sur l'API choisie.

## Conseils de prompt

- Garder un **style identique** pour toutes les espèces → collection visuellement cohérente.
- Inclure le **nom scientifique** en plus du nom commun pour de meilleurs résultats.
- Demander un **fond transparent ou uni** pour un rendu propre en grille.
- Exemple de gabarit de prompt :

  ```
  {ILLUSTRATION_STYLE}, a {common_name} ({scientific_name}),
  centered, plain background, no text
  ```

## Alternatives de fournisseur

Le pipeline est agnostique : on peut brancher un autre générateur d'images à la place de
Gemini en ne modifiant que la fonction `generate_image()` dans le script. À choisir selon
disponibilité, coût et qualité.

## Bonnes pratiques

- Les illustrations générées sont **régénérables** → le dossier `generated/` est dans
  `.gitignore` pour ne pas alourdir le dépôt. Garde éventuellement un petit set d'exemples.
- Vérifie les **conditions d'utilisation** du fournisseur pour un usage personnel/public.
