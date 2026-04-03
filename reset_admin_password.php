<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once __DIR__ . '/core/Database.php';

echo "<h1>🔑 重置管理员密码</h1>";
echo "<hr>";

$db = Database::getInstance();

// 生成新密码hash
$newPassword = 'admin123';
$hashedPassword = password_hash($newPassword, PASSWORD_DEFAULT);

echo "<p>用户名: <b>admin</b></p>";
echo "<p>新密码: <b>{$newPassword}</b></p>";
echo "<p>密码Hash: " . htmlspecialchars($hashedPassword) . "</p>";

// 直接用SQL更新
$sql = "UPDATE users SET password = ? WHERE username = ?";
$stmt = $db->getConnection()->prepare($sql);
$result = $stmt->execute([$hashedPassword, 'admin']);

if ($result) {
    echo "<p style='color:green; font-size:20px;'>✅ 密码重置成功！</p>";
    echo "<p>现在可以用 <b>admin / admin123</b> 登录了！</p>";
    
    // 验证一下
    $user = $db->fetchOne("SELECT * FROM users WHERE username = ?", ['admin']);
    if (password_verify($newPassword, $user['password'])) {
        echo "<p style='color:green;'>✅ 密码验证测试通过！</p>";
    }
} else {
    echo "<p style='color:red;'>❌ 密码重置失败！</p>";
    echo "<pre>";
    print_r($stmt->errorInfo());
    echo "</pre>";
}

echo "<hr>";
echo "<p><a href='login.php'>👉 去登录页面</a></p>";
?>
