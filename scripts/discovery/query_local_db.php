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
    
    $tables = [];
    $stmt = $pdo->query("SHOW TABLES");
    $table_names = $stmt->fetchAll(PDO::FETCH_COLUMN);
    
    foreach ($table_names as $t) {
        $tables[$t] = [
            'columns' => [],
            'primary_keys' => [],
            'foreign_keys' => [],
            'source_file' => 'Live MySQL (gradment)'
        ];
        
        $col_stmt = $pdo->query("DESCRIBE `$t`");
        $cols = $col_stmt->fetchAll();
        foreach ($cols as $c) {
            $col_name = $c['Field'];
            $tables[$t]['columns'][$col_name] = [
                'type' => strtoupper($c['Type']),
                'nullable' => ($c['Null'] === 'YES'),
                'auto_increment' => (strpos($c['Extra'], 'auto_increment') !== false)
            ];
            if ($c['Key'] === 'PRI') {
                $tables[$t]['primary_keys'][] = $col_name;
            }
        }

        // Query foreign keys from information_schema
        $fk_stmt = $pdo->prepare("
            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table AND REFERENCED_TABLE_NAME IS NOT NULL
        ");
        $fk_stmt->execute(['db' => $db, 'table' => $t]);
        $fks = $fk_stmt->fetchAll();
        foreach ($fks as $fk) {
            $tables[$t]['foreign_keys'][] = [
                'column' => $fk['COLUMN_NAME'],
                'referenced_table' => $fk['REFERENCED_TABLE_NAME'],
                'referenced_column' => $fk['REFERENCED_COLUMN_NAME']
            ];
        }
    }
    
    echo json_encode($tables, JSON_PRETTY_PRINT);
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
