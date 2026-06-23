// little-visitors — logique du dashboard.
// Interroge l'API de détections à intervalle régulier et met à jour la grille.

const REFRESH_MS = 30_000; // intervalle de rafraîchissement (30 s)
const API_URL = "api/detections.php";

const collectionEl = document.getElementById("collection");
const emptyEl = document.getElementById("empty-state");
const lastUpdateEl = document.getElementById("last-update");

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso.replace(" ", "T")).toLocaleString("fr-FR");
  } catch {
    return iso;
  }
}

function renderSpecies(species) {
  collectionEl.innerHTML = "";

  if (!species || species.length === 0) {
    emptyEl.hidden = false;
    return;
  }
  emptyEl.hidden = true;

  for (const s of species) {
    const card = document.createElement("article");
    card.className = "card";

    const img = document.createElement("div");
    img.className = "card__image";
    if (s.illustration) {
      img.style.backgroundImage = `url("${s.illustration}")`;
    } else {
      img.classList.add("card__image--placeholder");
      img.textContent = "🐦";
    }

    const body = document.createElement("div");
    body.className = "card__body";
    body.innerHTML = `
      <h2 class="card__name">${s.common_name ?? "Inconnu"}</h2>
      <p class="card__sci">${s.scientific_name ?? ""}</p>
      <p class="card__meta">
        <span class="card__count">${s.count ?? 0}×</span>
        <span class="card__seen">vu ${formatDate(s.last_seen)}</span>
      </p>
    `;

    card.append(img, body);
    collectionEl.append(card);
  }
}

async function refresh() {
  try {
    const res = await fetch(API_URL, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderSpecies(data.species);
    lastUpdateEl.textContent = `Mis à jour : ${formatDate(data.updated_at)}`;
  } catch (err) {
    lastUpdateEl.textContent = `Erreur de mise à jour (${err.message})`;
  }
}

refresh();
setInterval(refresh, REFRESH_MS);
