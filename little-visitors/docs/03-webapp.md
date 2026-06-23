# 03 — Webapp (dashboard)

Le dashboard reprend l'esprit de [bird.onethreenine.net](https://bird.onethreenine.net/) :
afficher en continu la **collection des oiseaux détectés**, chacun avec son illustration,
le nombre d'observations et l'horodatage de la dernière détection.

**Stack : PHP + JavaScript vanilla** (sans framework) — simple à héberger directement sur
le Pi à côté de BirdNET-Pi, et léger pour une tablette / liseuse / petit écran.

## Architecture

```
webapp/
├── index.php                 # page du dashboard (HTML servi par PHP)
├── api/
│   └── detections.php        # endpoint JSON : lit birds.db (SQLite) → renvoie les détections
└── assets/
    ├── css/style.css         # mise en page du collage / grille
    ├── js/app.js             # fetch périodique de l'API + rendu des cartes
    └── illustrations/        # images d'oiseaux (voir docs/04)
```

### Flux de données

1. `api/detections.php` ouvre la base SQLite de BirdNET-Pi (`BIRDNET_DB_PATH` du `.env`),
   agrège par espèce (nb de détections, dernière vue) et renvoie du **JSON**.
2. `app.js` interroge cet endpoint à intervalle régulier (polling) et met à jour la grille.
3. Chaque espèce affiche son **illustration** depuis `assets/illustrations/` si elle existe.

## Lancer en local (dev)

Sur une machine de dev (avec une base `birds.db` de test) :

```bash
cd webapp
php -S localhost:8000        # serveur PHP intégré
# → http://localhost:8000
```

## Déploiement sur le Pi

Deux options :

1. **Servir avec PHP intégré** (simple) — un service systemd qui lance `php -S 0.0.0.0:8000`.
2. **Via le serveur web de BirdNET-Pi** (Caddy) — exposer `webapp/` comme site additionnel.

Détails de configuration à compléter une fois le hardware choisi (voir `scripts/install.sh`).

## Affichage sur tablette / liseuse / écran

- Ouvrir l'URL du dashboard dans le navigateur de l'appareil, en **plein écran (kiosk)**.
- Pour une **liseuse e-ink** : privilégier un thème clair, contraste élevé, peu d'animations
  (le rafraîchissement e-ink est lent) → un mode `?display=eink` peut être ajouté dans le CSS.
- Pour une **tablette** : mode kiosque + empêcher la mise en veille.

## Personnalisation

- **Disposition** : grille de cartes vs collage façon mosaïque → `assets/css/style.css`.
- **Intervalle de rafraîchissement** : constante en haut de `assets/js/app.js`.
- **Filtrage** : limiter aux espèces plausibles via l'API eBird (voir docs/02).

> Le code dans `webapp/` est un **squelette de départ** : il pose la structure et le flux,
> à étoffer au fil du projet.
