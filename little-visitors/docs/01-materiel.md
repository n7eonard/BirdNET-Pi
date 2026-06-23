# 01 — Matériel & montage hardware

Cette partie couvre **ce qu'il faut acheter** et **comment l'assembler**. Je commande les
composants moi-même ; ce document sert de référence d'achat et de guide de montage.

## Bill of Materials

| Qté | Description | Prix indicatif | Notes |
|-----|-------------|----------------|-------|
| 1 | **Raspberry Pi** 4B / 5 / Zero 2W | ~35–80 $ | Le Zero 2W suffit pour BirdNET-Pi mais le 4B/5 est plus confortable (CPU pour l'inférence). |
| 1 | **Carte micro SD** ≥ 32 Go | ~10 $ | Classe A1/A2, marque fiable (SanDisk, Samsung). 64 Go conseillé si on garde beaucoup d'extraits audio. |
| 1 | **Micro-cravate USB** (lavalier) | 16,95 $ | Un micro USB omnidirectionnel fonctionne aussi. Évite les micros analogiques (le Pi n'a pas d'entrée). |
| 1 | **Alimentation** officielle Pi | ~10 $ | 5 V / 3 A (USB-C pour 4B/5, micro-USB pour Zero). Une alim sous-dimensionnée = instabilités. |
| 1 | **Écran** (tablette / liseuse / cadre e-ink) — *optionnel* | variable | Affiche le dashboard. Voir [docs/03-webapp.md](03-webapp.md) pour le mode d'affichage. |

## Choix du Raspberry Pi

| Modèle | Avantages | Inconvénients |
|--------|-----------|---------------|
| **Pi 5** | Le plus rapide, idéal si on ajoute du traitement | Plus cher, chauffe (prévoir refroidissement) |
| **Pi 4B** | Bon équilibre perf/prix, très répandu | — |
| **Pi Zero 2W** | Compact, faible conso, parfait en extérieur | Inférence plus lente, 1 seul port USB (prévoir hub/adaptateur OTG) |

> Pour une station de fenêtre discrète et économe : **Zero 2W**.
> Pour itérer confortablement sur le software : **4B** ou **5**.

## Placement & captation audio

- Placer le **micro près de la fenêtre / mangeoire**, à l'abri de la pluie directe.
- Une **bonnette anti-vent** (mousse) améliore nettement la détection en extérieur.
- Éviter les sources de bruit constant (ventilation, route) qui dégradent l'identification.

## Boîtier (optionnel)

- Boîtier imprimé en 3D ou boîtier du commerce pour protéger le Pi.
- Prévoir le passage du câble micro et la dissipation thermique (grille d'aération).

## Checklist montage

- [ ] Carte SD flashée (voir [docs/02-raspberry-pi.md](02-raspberry-pi.md))
- [ ] Micro USB branché et testé (`arecord -l` doit le lister)
- [ ] Pi alimenté par une alim 5 V / 3 A stable
- [ ] Micro positionné côté fenêtre, bonnette en place
- [ ] (Optionnel) Écran d'affichage connecté au réseau
