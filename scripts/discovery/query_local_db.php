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
    
    echo "=== 1. Checking table count in live MySQL '$db' ===\n";
    $stmt = $pdo->query("SHOW TABLES");
    $physical_tables = $stmt->fetchAll(PDO::FETCH_COLUMN);
    echo "Total physical tables in MySQL: " . count($physical_tables) . "\n";
    echo "\n";

    echo "=== 2. Inserting temporary test row into 'avaliacoes_disciplinas' ===\n";
    $chk = $pdo->query("SELECT COUNT(*) FROM avaliacoes_disciplinas")->fetchColumn();
    if ($chk == 0) {
        $ins = $pdo->prepare("INSERT INTO avaliacoes_disciplinas (usuario_id, disciplina_id, passou, dificuldade, esforco, created_at) VALUES (3, 26, 1, 4, 3, NOW())");
        $ins->execute();
        echo "Test rating row inserted successfully (id=" . $pdo->lastInsertId() . ").\n";
    } else {
        echo "Table already has $chk rows.\n";
    }
    echo "\n";

    echo "=== 3. Executing Verification Query 1: usuario_academicos JOIN usuarios ===\n";
    $stmt = $pdo->query("SELECT ua.*, u.nome FROM usuario_academicos ua JOIN usuarios u ON ua.usuario_id = u.id LIMIT 10");
    $rows1 = $stmt->fetchAll();
    echo "Rows returned: " . count($rows1) . "\n";
    foreach ($rows1 as $r) {
        echo "  - usuario_id={$r['usuario_id']} | curso_id={$r['curso_id']} | nome={$r['nome']}\n";
    }
    echo "\n";

    echo "=== 4. Executing Verification Query 2: materias_matriculadas JOIN curriculo_disciplinas ===\n";
    $stmt = $pdo->query("SELECT mm.*, cd.nome FROM materias_matriculadas mm JOIN curriculo_disciplinas cd ON mm.disciplina_id = cd.id LIMIT 10");
    $rows2 = $stmt->fetchAll();
    echo "Rows returned: " . count($rows2) . "\n";
    foreach ($rows2 as $r) {
        echo "  - matricula_id={$r['id']} | disciplina_id={$r['disciplina_id']} | codigo={$r['codigo']} | disciplina_nome={$r['nome']}\n";
    }
    echo "\n";

    echo "=== 5. Executing Verification Query 3: avaliacoes_disciplinas JOIN curriculo_disciplinas (REAL DATA) ===\n";
    $stmt = $pdo->query("SELECT ad.*, cd.nome FROM avaliacoes_disciplinas ad JOIN curriculo_disciplinas cd ON ad.disciplina_id = cd.id LIMIT 10");
    $rows3 = $stmt->fetchAll();
    echo "Rows returned: " . count($rows3) . "\n";
    foreach ($rows3 as $r) {
        echo "  - avaliacao_id={$r['id']} | usuario_id={$r['usuario_id']} | disciplina_id={$r['disciplina_id']} | dificuldade={$r['dificuldade']} | esforco={$r['esforco']} | disciplina_nome={$r['nome']}\n";
    }
    echo "\n";

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
