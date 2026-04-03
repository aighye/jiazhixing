#!/bin/bash
# 服务器端修复脚本
# 使用方法: sudo bash fix_on_server.sh

echo "=========================================="
echo "汽车4S店管理系统 - 修复脚本"
echo "=========================================="
echo ""

cd /var/www/html

# 1. 备份原文件
echo "[1/4] 备份原文件..."
sudo cp core/Auth.php core/Auth.php.bak
sudo cp core/Database.php core/Database.php.bak
echo "✅ 备份完成"
echo ""

# 2. 修复 Auth.php - 移除自动重定向
echo "[2/4] 修复 Auth.php..."
sudo cat > core/Auth.php << 'EOF'
<?php
class Auth {
    private static $user = null;
    private static $permissions = [];

    public static function check() {
        self::startSession();
        if (!isset($_SESSION['user_id'])) {
            return false;
        }
        self::$user = $_SESSION;
        self::loadPermissions();
        return true;
    }

    public static function user() {
        if (self::$user === null) {
            self::startSession();
            if (isset($_SESSION['user_id'])) {
                self::$user = $_SESSION;
            }
        }
        return self::$user;
    }

    public static function id() {
        return $_SESSION['user_id'] ?? null;
    }

    public static function role() {
        return $_SESSION['role_name'] ?? null;
    }

    public static function hasPermission($permission) {
        return in_array($permission, self::$permissions) || in_array('*', self::$permissions);
    }

    public static function login($user) {
        self::startSession();
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['real_name'] = $user['real_name'];
        $_SESSION['role_id'] = $user['role_id'];
        $_SESSION['role_name'] = $user['role_name'];
        self::$user = $_SESSION;
        self::loadPermissions();
    }

    public static function logout() {
        self::startSession();
        session_destroy();
        self::$user = null;
        self::$permissions = [];
    }

    private static function loadPermissions() {
        $db = Database::getInstance();
        $roleId = $_SESSION['role_id'] ?? 0;
        $rows = $db->fetchAll("SELECT p.permission_key FROM role_permissions rp JOIN permissions p ON rp.permission_id = p.id WHERE rp.role_id = ?", [$roleId]);
        self::$permissions = array_column($rows, 'permission_key');
    }

    private static function startSession() {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
    }

    public static function generateToken() {
        return bin2hex(random_bytes(32));
    }

    public static function verifyToken($token) {
        return isset($_SESSION['token']) && hash_equals($_SESSION['token'], $token);
    }
}
EOF
echo "✅ Auth.php 修复完成"
echo ""

# 3. 修复 Database.php - 使用127.0.0.1，提示用户输入数据库信息
echo "[3/4] 配置数据库连接..."
echo "请输入宝塔面板创建的数据库信息："
read -p "数据库名: " dbname
read -p "用户名: " dbuser
read -sp "密码: " dbpass
echo ""

sudo cat > core/Database.php <<EOF
<?php
class Database {
    private static \$instance = null;
    private \$pdo;

    private \$host = '127.0.0.1';
    private \$dbname = '$dbname';
    private \$username = '$dbuser';
    private \$password = '$dbpass';

    private function __construct() {
        try {
            \$this->pdo = new PDO(
                "mysql:host={\$this->host};dbname={\$this->dbname};charset=utf8",
                \$this->username,
                \$this->password,
                [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
            );
        } catch (PDOException \$e) {
            die("数据库连接失败: " . \$e->getMessage());
        }
    }

    public static function getInstance() {
        if (self::\$instance === null) {
            self::\$instance = new self();
        }
        return self::\$instance;
    }

    public function getConnection() {
        return \$this->pdo;
    }

    public function query(\$sql, \$params = []) {
        \$stmt = \$this->pdo->prepare(\$sql);
        \$stmt->execute(\$params);
        return \$stmt;
    }

    public function fetchAll(\$sql, \$params = []) {
        \$stmt = \$this->query(\$sql, \$params);
        return \$stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function fetchOne(\$sql, \$params = []) {
        \$stmt = \$this->query(\$sql, \$params);
        return \$stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function insert(\$table, \$data) {
        \$fields = implode(', ', array_keys(\$data));
        \$placeholders = ':' . implode(', :', array_keys(\$data));
        \$sql = "INSERT INTO {\$table} ({\$fields}) VALUES ({\$placeholders})";
        \$this->query(\$sql, \$data);
        return \$this->pdo->lastInsertId();
    }

    public function update(\$table, \$data, \$where, \$whereParams = []) {
        \$set = [];
        foreach (array_keys(\$data) as \$field) {
            \$set[] = "{\$field} = :{\$field}";
        }
        \$sql = "UPDATE {\$table} SET " . implode(', ', \$set) . " WHERE {\$where}";
        \$this->query(\$sql, array_merge(\$data, \$whereParams));
    }

    public function delete(\$table, \$where, \$params = []) {
        \$sql = "DELETE FROM {\$table} WHERE {\$where}";
        \$this->query(\$sql, \$params);
    }

    public function beginTransaction() {
        return \$this->pdo->beginTransaction();
    }

    public function commit() {
        return \$this->pdo->commit();
    }

    public function rollback() {
        return \$this->pdo->rollBack();
    }
}
EOF
echo "✅ Database.php 配置完成"
echo ""

# 4. 修复权限
echo "[4/4] 修复文件权限..."
sudo chown -R www:www /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;
sudo mkdir -p /var/www/html/uploads
sudo chmod 777 /var/www/html/uploads
sudo systemctl restart apache2
echo "✅ 权限修复完成"
echo ""

echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "请访问: http://1.14.43.118/"
echo "登录账号: admin / admin123"
echo ""
