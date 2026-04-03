<?php
class Logger {
    private static $db;

    public static function init() {
        self::$db = Database::getInstance();
    }

    public static function log($action, $description, $module = 'system') {
        if (!isset(self::$db)) {
            self::init();
        }

        $userId = Auth::id() ?? 0;
        $username = Auth::user()['username'] ?? 'system';
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        $userAgent = $_SERVER['HTTP_USER_AGENT'] ?? '';

        self::$db->insert('system_logs', [
            'user_id' => $userId,
            'username' => $username,
            'action' => $action,
            'description' => $description,
            'module' => $module,
            'ip_address' => $ip,
            'user_agent' => $userAgent,
            'created_at' => date('Y-m-d H:i:s')
        ]);
    }

    public static function loginLog($username, $status, $ip) {
        if (!isset(self::$db)) {
            self::init();
        }

        self::$db->insert('login_logs', [
            'username' => $username,
            'status' => $status,
            'ip_address' => $ip,
            'created_at' => date('Y-m-d H:i:s')
        ]);
    }
}