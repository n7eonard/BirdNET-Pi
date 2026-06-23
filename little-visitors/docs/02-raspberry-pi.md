# 02 — Configuration du Raspberry Pi & BirdNET-Pi

Cette partie couvre la mise en route du Pi, l'installation de **BirdNET-Pi** (le moteur de
détection sonore) et la configuration de l'**API eBird**.

## 1. Flasher la carte SD

1. Installer **[Raspberry Pi Imager](https://www.raspberrypi.com/software/)**.
2. Choisir l'OS : **Raspberry Pi OS Lite (64-bit)** — pas besoin de bureau graphique.
3. Dans les réglages avancés (⚙️) de l'Imager, configurer **avant** d'écrire :
   - **Hostname** : `birdnetpi` (le dashboard sera accessible via `http://birdnetpi.local`)
   - **SSH activé** + nom d'utilisateur / mot de passe
   - **Wi-Fi** (SSID + mot de passe + pays)
   - **Locale / fuseau horaire**
4. Écrire l'image, insérer la carte dans le Pi, brancher l'alimentation.

## 2. Première connexion

```bash
ssh pi@birdnetpi.local        # adapte l'utilisateur si besoin
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

Vérifier que le micro est détecté :

```bash
arecord -l                    # doit lister la carte son USB
arecord -d 5 test.wav         # enregistre 5 s pour tester
```

## 3. Installer BirdNET-Pi

[BirdNET-Pi](https://github.com/Nachtzuster/BirdNET-Pi) fait toute la détection (modèle
BirdNET / TensorFlow Lite), stocke les détections dans **SQLite** et expose une interface
web. On le réutilise tel quel — on ne réécrit **pas** la partie ML.

```bash
curl -s https://raw.githubusercontent.com/Nachtzuster/BirdNET-Pi/main/newinstaller.sh | bash
```

> ⏱️ L'installation prend 20–40 min. Le Pi redémarre à la fin.

Une fois installé :

- Interface BirdNET-Pi : **`http://birdnetpi.local`**
- Identifiants par défaut : utilisateur `birdnet`, mot de passe vide (à changer).
- Base de données SQLite : `~/BirdNET-Pi/scripts/birds.db` (chemin à reporter dans `.env`,
  variable `BIRDNET_DB_PATH`).

### Réglages recommandés dans l'UI BirdNET-Pi

- **Latitude / longitude** : améliore la pertinence des espèces.
- **Seuil de confiance** : monter si trop de faux positifs.
- **Localisation / langue** des noms d'espèces.

## 4. Configurer l'API eBird

L'API eBird sert à **filtrer / enrichir** les espèces selon la région.

1. Générer une clé : <https://ebird.org/api/keygen>
2. La renseigner dans `.env` (jamais en clair dans le repo) :

   ```dotenv
   EBIRD_API_KEY=xxxxxxxxxxxx
   EBIRD_REGION=FR          # ou FR-OCC, US-NY, etc.
   ```

3. Exemple d'appel (liste des espèces récentes observées dans la région) :

   ```bash
   curl --location "https://api.ebird.org/v2/data/obs/${EBIRD_REGION}/recent" \
        --header "X-eBirdApiToken: ${EBIRD_API_KEY}"
   ```

> 🔑 **Sécurité** : la clé eBird est un secret. Elle vit dans `.env` (ignoré par git).
> Si elle a été exposée, régénère-la depuis le portail eBird.

## 5. Licence

BirdNET-Pi est sous **GPL-3.0**. Si tu redistribues un dépôt qui **inclut son code**, tu
dois respecter la GPL. Ici on se contente de **l'installer** sur le Pi et de lire sa base ;
le code de `little-visitors` (webapp + scripts) peut rester sous sa propre licence.

## Dépannage rapide

| Symptôme | Piste |
|----------|-------|
| `birdnetpi.local` injoignable | Vérifier le mDNS local, sinon utiliser l'IP du Pi |
| Aucune détection | `arecord -l` ne voit pas le micro / mauvais périphérique d'entrée |
| Trop de faux positifs | Monter le seuil de confiance dans l'UI |
| Pi instable / reboots | Alimentation sous-dimensionnée (utiliser 5 V / 3 A) |
