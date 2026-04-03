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

    public static function require() {
        if (!self::check()) {
            header('Location: /login.php');
            exit;
        }
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