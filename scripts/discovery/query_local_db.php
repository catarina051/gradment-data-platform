<?php
$host = '127.0.0.1';
$db = 'gradment';
$user = 'root';
$pass = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
    
    echo "=== Registered Migrations in Local Database '$db' ===\n";
    $stmt = $pdo->query("SELECT * FROM migrations ORDER BY id ASC");
    $migrations = $stmt->fetchAll();
    foreach ($migrations as $m) {
        echo " - [Batch {$m['batch']}] {$m['name']} (version: {$m['version']})\n";
    }
    echo "\n";

    echo "=== Executing Verification Query 1: usuario_academicos JOIN usuarios ===\n";
    $stmt = $pdo->query("SELECT ua.*, u.nome FROM usuario_academicos ua JOIN usuarios u ON ua.usuario_id = u.id LIMIT 10");
    $rows1 = $stmt->fetchAll();
    echo "Rows returned: " . count($rows1) . "\n";
    print_r($rows1);
    echo "\n";

    echo "=== Executing Verification Query 2: materias_matriculadas JOIN curriculo_disciplinas ===\n";
    $stmt = $pdo->query("SELECT mm.*, cd.nome FROM materias_matriculadas mm JOIN curriculo_disciplinas cd ON mm.disciplina_id = cd.id LIMIT 10");
    $rows2 = $stmt->fetchAll();
    echo "Rows returned: " . count($rows2) . "\n";
    print_r($rows2);
    echo "\n";

    echo "=== Executing Verification Query 3: avaliacoes_disciplinas JOIN curriculo_disciplinas ===\n";
    $stmt = $pdo->query("SELECT ad.*, cd.nome FROM avaliacoes_disciplinas ad JOIN curriculo_disciplinas cd ON ad.disciplina_id = cd.id LIMIT 10");
    $rows3 = $stmt->fetchAll();
    echo "Rows returned: " . count($rows3) . "\n";
    print_r($rows3);
    echo "\n";

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
