<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once __DIR__ . '/bootstrap.php';

echo "<h1>🔍 汽车4S店管理系统 - 全面检查</h1>";
echo "<hr>";

$allPassed = true;

echo "<h2>1. 核心文件检查</h2>";
$coreFiles = [
    'bootstrap.php',
    'core/Database.php',
    'core/Auth.php',
    'core/Config.php',
    'core/Helper.php',
    'core/Logger.php',
    'config/app.php'
];

echo "<ul>";
foreach ($coreFiles as $file) {
    if (file_exists($file)) {
        echo "<li style='color:green;'>✅ {$file}</li>";
    } else {
        echo "<li style='color:red;'>❌ {$file} - 缺失</li>";
        $allPassed = false;
    }
}
echo "</ul>";

echo "<h2>2. 数据库连接检查</h2>";
try {
    $db = Database::getInstance();
    echo "<p style='color:green;'>✅ 数据库连接成功</p>";
    
    echo "<h3>数据库表检查</h3>";
    $requiredTables = [
        'users', 'roles', 'permissions', 'role_permissions',
        'customers', 'customer_vehicles',
        'parts', 'parts_categories', 'suppliers',
        'work_orders', 'work_order_services', 'work_order_parts',
        'settlements', 'payment_records',
        'system_config', 'system_logs', 'login_logs'
    ];
    
    $tables = $db->fetchAll("SHOW TABLES");
    $tableNames = array_column($tables, array_keys($tables[0])[0]);
    
    echo "<ul>";
    foreach ($requiredTables as $table) {
        if (in_array($table, $tableNames)) {
            echo "<li style='color:green;'>✅ {$table}</li>";
        } else {
            echo "<li style='color:red;'>❌ {$table} - 表不存在</li>";
            $allPassed = false;
        }
    }
    echo "</ul>";
    
} catch (Exception $e) {
    echo "<p style='color:red;'>❌ 数据库连接失败: " . $e->getMessage() . "</p>";
    $allPassed = false;
}

echo "<h2>3. 用户认证检查</h2>";
if (Auth::check()) {
    $user = Auth::user();
    echo "<p style='color:green;'>✅ 已登录</p>";
    echo "<p>用户: {$user['username']} ({$user['real_name']})</p>";
    echo "<p>角色: " . Auth::role() . "</p>";
} else {
    echo "<p style='color:orange;'>⏸️ 未登录（这是正常的，如果访问此页面时未登录）</p>";
}

echo "<h2>4. 模块页面检查</h2>";
$modules = [
    'dashboard.php' => '仪表盘',
    'customers/index.php' => '客户管理',
    'customers/add.php' => '新增客户',
    'workorders/index.php' => '维修工单',
    'workorders/add.php' => '新增工单',
    'parts/index.php' => '配件管理',
    'settlements/index.php' => '财务结算',
    'reports/index.php' => '统计报表',
    'system/users.php' => '系统管理'
];

echo "<ul>";
foreach ($modules as $file => $name) {
    if (file_exists($file)) {
        echo "<li style='color:green;'>✅ {$name} - <a href='{$file}' target='_blank'>访问</a></li>";
    } else {
        echo "<li style='color:red;'>❌ {$name} - 文件缺失</li>";
        $allPassed = false;
    }
}
echo "</ul>";

echo "<h2>5. 数据检查</h2>";
try {
    $userCount = $db->fetchOne("SELECT COUNT(*) as count FROM users")['count'];
    $customerCount = $db->fetchOne("SELECT COUNT(*) as count FROM customers")['count'];
    $partCount = $db->fetchOne("SELECT COUNT(*) as count FROM parts")['count'];
    $orderCount = $db->fetchOne("SELECT COUNT(*) as count FROM work_orders")['count'];
    
    echo "<ul>";
    echo "<li>用户数: {$userCount}</li>";
    echo "<li>客户数: {$customerCount}</li>";
    echo "<li>配件数: {$partCount}</li>";
    echo "<li>工单数: {$orderCount}</li>";
    echo "</ul>";
} catch (Exception $e) {
    echo "<p style='color:red;'>❌ 数据查询失败: " . $e->getMessage() . "</p>";
}

echo "<h2>6. PHP语法检查</h2>";
$phpFiles = glob('**/*.php', GLOB_BRACE);
$syntaxErrors = [];

foreach ($phpFiles as $file) {
    if ($file === basename(__FILE__)) continue;
    
    $output = [];
    $return = 0;
    exec("php -l " . escapeshellarg($file) . " 2>&1", $output, $return);
    
    if ($return !== 0) {
        $syntaxErrors[$file] = implode("\n", $output);
    }
}

if (empty($syntaxErrors)) {
    echo "<p style='color:green;'>✅ 所有PHP文件语法正确</p>";
} else {
    echo "<p style='color:red;'>❌ 发现语法错误：</p>";
    echo "<ul>";
    foreach ($syntaxErrors as $file => $error) {
        echo "<li><b>{$file}</b>:<br><pre>" . htmlspecialchars($error) . "</pre></li>";
    }
    echo "</ul>";
    $allPassed = false;
}

echo "<hr>";
if ($allPassed) {
    echo "<h2 style='color:green;'>✅ 系统检查通过！</h2>";
} else {
    echo "<h2 style='color:red;'>❌ 发现问题，请修复后重新检查</h2>";
}

echo "<hr>";
echo "<p><a href='login.php'>👉 去登录</a></p>";
echo "<p><a href='dashboard.php'>👉 去仪表盘</a></p>";
?>
