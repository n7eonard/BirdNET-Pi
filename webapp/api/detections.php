<?php
// little-visitors — endpoint JSON des détections.
//
// Lit la base SQLite de BirdNET-Pi et renvoie les espèces détectées, agrégées
// par espèce (nombre de détections + dernière observation).
//
// ⚠️ Squelette de départ : adapte les noms de tables/colonnes au schéma réel de
//    ta version de BirdNET-Pi (table « detections » dans birds.db).

header('Content-Type: application/json; charset=utf-8');

// --- Configuration -----------------------------------------------------------
// Chemin de la base, idéalement lu depuis l'environnement (.env → BIRDNET_DB_PATH).
$dbPath = getenv('BIRDNET_DB_PATH') ?: '/home/pi/BirdNET-Pi/scripts/birds.db';

if (!file_exists($dbPath)) {
    http_response_code(503);
    echo json_encode([
        'error'   => 'Base BirdNET-Pi introuvable',
        'db_path' => $dbPath,
        'hint'    => 'Renseigne BIRDNET_DB_PATH (voir .env.example).',
    ]);
    exit;
}

try {
    $db = new PDO('sqlite:' . $dbPath);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Agrégation par espèce. Adapte les colonnes (Com_Name, Sci_Name, Date, Time…)
    // au schéma de ta base BirdNET-Pi.
    $sql = "
        SELECT
            Com_Name                     AS common_name,
            Sci_Name                     AS scientific_name,
            COUNT(*)                     AS count,
            MAX(Date || ' ' || Time)     AS last_seen,
            MAX(Confidence)              AS best_confidence
        FROM detections
        GROUP BY Com_Name, Sci_Name
        ORDER BY last_seen DESC
    ";

    $rows = $db->query($sql)->fetchAll(PDO::FETCH_ASSOC);

    // Associe le fichier d'illustration s'il existe.
    foreach ($rows as &$row) {
        $slug  = preg_replace('/[^a-z0-9]+/', '-', strtolower($row['common_name']));
        $file  = "assets/illustrations/{$slug}.png";
        $row['illustration'] = file_exists(__DIR__ . '/../' . $file) ? $file : null;
    }
    unset($row);

    echo json_encode([
        'updated_at' => date('c'),
        'species'    => $rows,
    ]);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Erreur base de données', 'detail' => $e->getMessage()]);
}
