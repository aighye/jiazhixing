<?php
require_once __DIR__ . '/bootstrap.php';

if (Auth::check()) {
    Helper::redirect('/dashboard.php');
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';
    $remember = isset($_POST['remember']) ? true : false;

    if (empty($username) || empty($password)) {
        $error = '请输入用户名和密码';
    } else {
        $db = Database::getInstance();
        $user = $db->fetchOne("SELECT u.*, r.role_name, r.role_code FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.username = ? AND u.status = 1", [$username]);

        if ($user && password_verify($password, $user['password'])) {
            Logger::loginLog($username, 1, $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1');

            $db->update('users', [
                'last_login_at' => date('Y-m-d H:i:s'),
                'last_login_ip' => $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1'
            ], 'id = ?', [$user['id']]);

            Auth::login($user);
            Logger::log('登录', '用户登录系统', 'auth');

            Helper::redirect('/dashboard.php');
        } else {
            Logger::loginLog($username, 0, $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1');
            $error = '用户名或密码错误';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>汽车4S店维修业务管理系统 - 登录</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-card {
            width: 100%;
            max-width: 420px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px 12px 0 0;
            padding: 30px;
            color: white;
            text-align: center;
        }
        .login-header h1 {
            font-size: 24px;
            margin: 0;
        }
        .login-body {
            padding: 30px;
        }
        .form-floating > label {
            padding-left: 1rem;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, #5a6fd6 0%, #6a4190 100%);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="card login-card">
                    <div class="login-header">
                        <h1><i class="bi bi-gear-wide-connected"></i> 汽车4S店维修业务管理系统</h1>
                        <p class="mb-0 mt-2 opacity-75">请登录您的账户</p>
                    </div>
                    <div class="login-body">
                        <?php if ($error): ?>
                            <div class="alert alert-danger" role="alert">
                                <?php echo htmlspecialchars($error); ?>
                            </div>
                        <?php endif; ?>

                        <form method="POST" action="">
                            <div class="form-floating mb-3">
                                <input type="text" class="form-control" id="username" name="username" placeholder="用户名" required autofocus>
                                <label for="username">用户名</label>
                            </div>
                            <div class="form-floating mb-3">
                                <input type="password" class="form-control" id="password" name="password" placeholder="密码" required>
                                <label for="password">密码</label>
                            </div>
                            <div class="form-check mb-3">
                                <input class="form-check-input" type="checkbox" id="remember" name="remember">
                                <label class="form-check-label" for="remember">记住我</label>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 py-3">登 录</button>
                        </form>

                        <div class="text-center mt-4 text-muted small">
                            <p class="mb-0">默认账号: admin / admin123</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
</body>
</html>
