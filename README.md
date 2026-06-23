# 🐦 little-visitors

Une **station de suivi des oiseaux** pour le rebord de fenêtre : un micro détecte les
chants d'oiseaux, une IA les identifie, et un dashboard web affiche en temps réel la
collection des « petits visiteurs » détectés — chacun illustré par un LLM.

Projet personnel fortement inspiré de
[AvianVisitors](https://github.com/Twarner491/AvianVisitors) de Theodore Warner

---

## 🎯 Principe

1. Un **micro USB** branché sur un **Raspberry Pi** écoute en continu.
2. **BirdNET-Pi** (modèle ML basé sur BirdNET / TensorFlow Lite) identifie les espèces
   à partir du son et enregistre chaque détection dans une base SQLite.
3. L'**API eBird** filtre les espèces plausibles selon ma région.
4. Un **LLM** (Google Gemini par défaut) génère une **illustration** pour chaque espèce
   détectée.
5. Une **webapp** (PHP / JS vanilla) lit la base + les illustrations et affiche un
   **dashboard** des oiseaux détectés.
6. Une **tablette / liseuse / petit écran** affiche ce dashboard en permanence.

```
                    ┌──────────────┐
   🎤 micro USB ───▶│ BirdNET-Pi   │  détection ML temps réel
                    │ (Raspberry   │──────────┐
                    │  Pi)         │          ▼
                    └──────────────┘   ┌─────────────┐
                          ▲            │ birds.db    │ (SQLite)
              API eBird ──┘            └─────────────┘
            (filtre région)                  │
                                             ▼
   API LLM ───▶ scripts/ génère       ┌─────────────┐
  (Gemini)     les illustrations ────▶│  webapp      │──▶ 🖥️ tablette /
                                      │ (PHP / JS)   │     liseuse / écran
                                      └─────────────┘
```

---

## 🛒 Matériel (Bill of Materials)

| Qté | Description | Prix indicatif | Lien |
|-----|-------------|----------------|------|
| 1 | Raspberry Pi (4B / 5 / Zero 2W) | ~35–80 $ | Amazon |
| 1 | Carte micro SD (≥ 32 Go) | ~10 $ | Amazon |
| 1 | Micro-cravate USB (lavalier) | 16,95 $ | Amazon |
| 1 | Alimentation Raspberry Pi | ~10 $ | — |
| 1 | Écran d'affichage (tablette / liseuse / cadre e-ink) — *optionnel* | variable | — |
| | **Total (hors écran)** | **~80 $** | |

➡️ Détails, alternatives et conseils d'achat : **[docs/01-materiel.md](docs/01-materiel.md)**

---

## 📚 Documentation

La doc est volontairement découpée par étape :

| # | Partie | Fichier |
|---|--------|---------|
| 1 | **Matériel** — choix des composants, BOM, montage hardware | [docs/01-materiel.md](docs/01-materiel.md) |
| 2 | **Raspberry Pi** — flash de l'OS, config, installation de BirdNET-Pi, eBird | [docs/02-raspberry-pi.md](docs/02-raspberry-pi.md) |
| 3 | **Webapp** — le dashboard PHP/JS, déploiement, personnalisation | [docs/03-webapp.md](docs/03-webapp.md) |
| 4 | **Illustrations (LLM)** — génération des illustrations d'oiseaux | [docs/04-illustrations-llm.md](docs/04-illustrations-llm.md) |

---

## 🚀 Démarrage rapide

```bash
# 1. Cloner le repo
git clone https://github.com/n7eonard/little-visitors.git
cd little-visitors

# 2. Configurer les secrets (clés API eBird & LLM)
cp .env.example .env
$EDITOR .env

# 3. Suivre la doc dans l'ordre :
#    docs/01-materiel.md  →  docs/02-raspberry-pi.md  →  docs/03-webapp.md  →  docs/04-illustrations-llm.md
```

> ⚠️ **Secrets** : les clés API (eBird, Gemini) vont dans `.env`, **jamais** committé
> (voir `.gitignore`). Si une clé a fuité, régénère-la depuis le portail concerné.

---

## 🗂️ Structure du dépôt

```
little-visitors/
├── README.md                 # ce fichier (vue d'ensemble + index)
├── .env.example              # gabarit des variables d'environnement
├── docs/                     # documentation détaillée, une partie par fichier
│   ├── 01-materiel.md
│   ├── 02-raspberry-pi.md
│   ├── 03-webapp.md
│   └── 04-illustrations-llm.md
├── webapp/                   # le dashboard (PHP / JS vanilla)
│   ├── index.php
│   ├── api/detections.php
│   └── assets/{css,js,illustrations}/
└── scripts/                  # outillage (install, génération d'illustrations)
    ├── install.sh
    └── generate_illustrations.py
```

---

## 🙏 Crédits & licences

- **[BirdNET-Pi](https://github.com/Nachtzuster/BirdNET-Pi)** — détection sonore (GPL-3.0).
- **[BirdNET](https://github.com/kahst/BirdNET-Analyzer)** — modèle d'identification (K. Lisa Yang Center for Conservation Bioacoustics, Cornell Lab).
- **[AvianVisitors](https://github.com/Twarner491/AvianVisitors)** — inspiration directe.
- **[eBird](https://ebird.org/)** — données d'espèces régionales.

> ⚖️ BirdNET-Pi étant sous GPL-3.0, toute redistribution intégrant son code doit
> respecter cette licence. Voir [docs/02-raspberry-pi.md](docs/02-raspberry-pi.md).
