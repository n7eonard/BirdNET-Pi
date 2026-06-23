<?php
// little-visitors — page du dashboard.
// Sert le HTML ; les données sont chargées côté client depuis api/detections.php.
?>
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>little-visitors 🐦</title>
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  <header class="header">
    <h1>little-visitors</h1>
    <p class="subtitle">Les oiseaux détectés à ma fenêtre</p>
  </header>

  <main>
    <!-- Les cartes d'espèces sont injectées ici par assets/js/app.js -->
    <section id="collection" class="collection" aria-live="polite"></section>
    <p id="empty-state" class="empty">En attente de visiteurs…</p>
  </main>

  <footer class="footer">
    <span id="last-update">—</span>
  </footer>

  <script src="assets/js/app.js"></script>
</body>
</html>
