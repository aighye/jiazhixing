# 🔧 修复重定向循环 - ERR_TOO_MANY_REDIRECTS

## 问题原因
1. **数据库还没导入** - Auth::check() 想查询数据库但失败了
2. **Session配置问题**

---

## ✅ 分步修复

### 第1步：创建一个简单的测试页面，绕过登录

在服务器上执行：
```bash
cd /var/www/html
```

创建一个临时测试页面：
```bash
sudo nano /var/www/html/test_login.php
```

复制粘贴以下内容：
```php
<?php
require_once __DIR__ . '/bootstrap.php';

echo "<h1>系统测试页面</h1>";
echo "<h2>1. 测试数据库连接</h2>";

try {
    $db = Database::getInstance();
    echo "<p style='color:green;'>✅ 数据库连接成功！</p>";
    
    echo "<h2>2. 测试查询用户表</h2>";
    $users = $db->fetchAll("SELECT * FROM users");
    echo "<p style='color:green;'>✅ 用户表查询成功！找到 " . count($users) . " 个用户</p>";
    
    echo "<h2>3. 用户列表</h2>";
    echo "<ul>";
    foreach ($users as $u) {
        echo "<li>ID: {$u['id']}, 用户名: {$u['username']}, 真实姓名: {$u['real_name']}</li>";
    }
    echo "</ul>";
    
} catch (Exception $e) {
    echo "<p style='color:red;'>❌ 错误: " . $e->getMessage() . "</p>";
    echo "<p style='color:orange;'>💡 提示：您可能还没有导入数据库！</p>";
}

echo "<hr>";
echo "<h2>快速链接</h2>";
echo "<p><a href='login.php'>👉 去登录页面</a></p>";
echo "<p><a href='test_login.php?skip_login=1'>👉 直接进后台（临时测试）</a></p>";

// 临时跳过登录的功能
if (isset($_GET['skip_login']) && $_GET['skip_login'] == 1) {
    echo "<hr>";
    echo "<h2 style='color:orange;'>⚠️  临时登录模式</h2>";
    
    // 创建一个临时会话
    session_start();
    $_SESSION['user_id'] = 1;
    $_SESSION['username'] = 'admin';
    $_SESSION['real_name'] = '临时管理员';
    $_SESSION['role_id'] = 1;
    $_SESSION['role_name'] = '超级管理员';
    
    echo "<p style='color:green;'>✅ 临时会话已创建！</p>";
    echo "<p><a href='dashboard.php'>👉 进入仪表盘</a></p>";
}
?>
```

按 `Ctrl+O` 保存，`Enter` 确认，`Ctrl+X` 退出。

---

### 第2步：访问测试页面

在浏览器打开：
```
http://1.14.43.118/test_login.php
```

---

### 第3步：根据测试结果处理

#### 情况A：看到数据库连接失败
**说明还没导入数据库！**

👉 立即去导入数据库，参照 `IMPORT_DATABASE.md`

快速导入命令：
```bash
cd /var/www/html

sudo mysql <<EOF
CREATE DATABASE IF NOT EXISTS auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'auto_4s_user'@'localhost' IDENTIFIED BY 'Auto4s@2024';
GRANT ALL PRIVILEGES ON auto_4s_system.* TO 'auto_4s_user'@'localhost';
FLUSH PRIVILEGES;
EOF

mysql -u auto_4s_user -pAuto4s@2024 auto_4s_system < /var/www/html/database/install.sql
```

#### 情况B：看到用户列表
**说明数据库正常！**

点击页面上的 "👉 去登录页面"

---

### 第4步：修改index.php，临时绕过循环

如果导入数据库后还是有问题，临时修改index.php：

```bash
sudo nano /var/www/html/index.php
```

先备份一下：
```bash
sudo cp /var/www/html/index.php /var/www/html/index.php.bak
```

然后把内容改为：
```php
<?php
require_once __DIR__ . '/bootstrap.php';

// 临时：直接去登录页，不检查
header('Location: /login.php');
exit;
?>
```

---

### 第5步：检查Session保存路径

```bash
ls -la /var/lib/php/sessions/
```

如果权限不对，修复：
```bash
sudo chown -R www-data:www-data /var/lib/php/sessions
sudo chmod 733 /var/lib/php/sessions
sudo systemctl restart apache2
```

---

## 🚀 快速修复（按顺序执行）

```bash
# 1. 进入目录
cd /var/www/html

# 2. 确保数据库已导入（如果还没导入）
sudo mysql <<EOF
CREATE DATABASE IF NOT EXISTS auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'auto_4s_user'@'localhost' IDENTIFIED BY 'Auto4s@2024';
GRANT ALL PRIVILEGES ON auto_4s_system.* TO 'auto_4s_user'@'localhost';
FLUSH PRIVILEGES;
EOF

mysql -u auto_4s_user -pAuto4s@2024 auto_4s_system < /var/www/html/database/install.sql

# 3. 修复Session权限
sudo chown -R www-data:www-data /var/lib/php/sessions
sudo chmod 733 /var/lib/php/sessions

# 4. 重启Apache
sudo systemctl restart apache2

# 5. 创建测试页面
echo '<?php require_once __DIR__ . "/bootstrap.php"; header("Location: login.php"); ?>' > /var/www/html/index.tmp.php
sudo mv /var/www/html/index.tmp.php /var/www/html/index.php
```

---

## ✅ 验证修复

访问测试页面：
```
http://1.14.43.118/test_login.php
```

看到数据库连接成功和用户列表后，访问：
```
http://1.14.43.118/login.php
```

用账号登录：
- 用户名：`admin`
- 密码：`admin123`

---

## 📋 检查清单

- [ ] 数据库已导入
- [ ] test_login.php 能看到用户列表
- [ ] Session 目录权限正确
- [ ] Apache 已重启
- [ ] 能访问 login.php
- [ ] 能使用 admin/admin123 登录
