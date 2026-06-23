#!/usr/bin/env bash
# little-visitors — script d'installation (squelette).
#
# À exécuter SUR le Raspberry Pi, après avoir installé BirdNET-Pi
# (voir docs/02-raspberry-pi.md). Met en place la webapp dashboard.
#
# Usage : bash scripts/install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> little-visitors : installation depuis ${REPO_DIR}"

# 1. Vérifier les prérequis -----------------------------------------------------
command -v php >/dev/null 2>&1 || {
  echo "PHP requis. Installe-le : sudo apt install -y php-cli php-sqlite3" >&2
  exit 1
}

# 2. Configuration --------------------------------------------------------------
if [[ ! -f "${REPO_DIR}/.env" ]]; then
  echo "==> Création de .env depuis .env.example (à compléter ensuite)"
  cp "${REPO_DIR}/.env.example" "${REPO_DIR}/.env"
fi

# 3. Servir la webapp -----------------------------------------------------------
# Option simple : serveur PHP intégré. Pour un déploiement durable, créer un
# service systemd ou exposer webapp/ via le Caddy de BirdNET-Pi (voir docs/03).
echo "==> Pour lancer le dashboard en local :"
echo "    cd ${REPO_DIR}/webapp && php -S 0.0.0.0:8000"
echo
echo "Installation terminée. Complète .env puis consulte docs/03-webapp.md."
