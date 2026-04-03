<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    if ($action == 'add') {
        $data = [
            'username' => trim($_POST['username']),
            'password' => password_hash($_POST['password'], PASSWORD_DEFAULT),
            'real_name' => trim($_POST['real_name']),
            'phone' => trim($_POST['phone']),
            'role_id' => (int)$_POST['role_id'],
            'status' => 1
        ];

        if (empty($data['username']) || empty($_POST['password'])) {
            Helper::back('请填写用户名和密码');
        }

        $db->insert('users', $data);
        Logger::log('新增用户', "创建用户: {$data['username']}", 'system');
        Helper::redirect('users.php');
    }

    if ($action == 'edit') {
        $id = (int)$_POST['id'];
        $data = [
            'real_name' => trim($_POST['real_name']),
            'phone' => trim($_POST['phone']),
            'role_id' => (int)$_POST['role_id'],
            'status' => isset($_POST['status']) ? 1 : 0
        ];

        if (!empty($_POST['password'])) {
            $data['password'] = password_hash($_POST['password'], PASSWORD_DEFAULT);
        }

        $db->update('users', $data, 'id = ?', [$id]);
        Logger::log('编辑用户', "修改用户ID: {$id}", 'system');
        Helper::redirect('users.php');
    }
}

Helper::redirect('users.php');
