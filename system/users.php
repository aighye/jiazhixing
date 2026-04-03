<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$limit = 15;
$offset = ($page - 1) * $limit;

$total = $db->fetchOne("SELECT COUNT(*) as count FROM users")['count'];
$users = $db->fetchAll("SELECT u.*, r.role_name FROM users u LEFT JOIN roles r ON u.role_id = r.id ORDER BY u.created_at DESC LIMIT {$limit} OFFSET {$offset}", []);
$roles = $db->fetchAll("SELECT * FROM roles WHERE status = 1 ORDER BY sort, id");
$pagination = Helper::pagination($total, $page, $limit);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用户管理 - 汽车4S店维修业务管理系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        .sidebar {
            min-height: 100vh;
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        }
        .sidebar .nav-link {
            color: #94a3b8;
            padding: 12px 20px;
            border-radius: 8px;
            margin: 4px 10px;
        }
        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            color: white;
            background: #334155;
        }
        .sidebar .nav-link i {
            width: 24px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 sidebar d-none d-md-block">
                <div class="p-4 text-white text-center border-bottom border-secondary">
                    <h4><i class="bi bi-gear-wide-connected"></i></h4>
                    <h5 class="mb-0">4S店维修系统</h5>
                </div>
                <nav class="nav flex-column mt-3">
                    <a class="nav-link" href="/dashboard.php"><i class="bi bi-speedometer2"></i> 仪表盘</a>
                    <a class="nav-link" href="/workorders/index.php"><i class="bi bi-tools"></i> 维修工单</a>
                    <a class="nav-link" href="/customers/index.php"><i class="bi bi-people"></i> 客户管理</a>
                    <a class="nav-link" href="/parts/index.php"><i class="bi bi-box-seam"></i> 配件管理</a>
                    <a class="nav-link" href="/settlements/index.php"><i class="bi bi-cash-coin"></i> 财务结算</a>
                    <a class="nav-link" href="/reports/index.php"><i class="bi bi-bar-chart"></i> 统计报表</a>
                    <hr class="my-3 text-secondary mx-3">
                    <a class="nav-link active" href="/system/users.php"><i class="bi bi-gear"></i> 系统设置</a>
                </nav>
            </div>

            <div class="col-md-10 main-content">
                <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom sticky-top">
                    <div class="container-fluid">
                        <a class="navbar-brand d-md-none" href="#"><i class="bi bi-gear-wide-connected"></i> 4S店维修系统</a>
                        <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebarOffcanvas">
                            <span class="navbar-toggler-icon"></span>
                        </button>
                        <div class="d-flex ms-auto align-items-center">
                            <span class="me-3 text-muted"><i class="bi bi-calendar3"></i> <?php echo date('Y-m-d'); ?></span>
                            <a href="/logout.php" class="btn btn-outline-danger"><i class="bi bi-box-arrow-left"></i> 退出</a>
                        </div>
                    </div>
                </nav>

                <div class="p-4">
                    <ul class="nav nav-tabs mb-4">
                        <li class="nav-item">
                            <a class="nav-link active" href="users.php">用户管理</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="roles.php">角色管理</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="logs.php">操作日志</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="config.php">系统配置</a>
                        </li>
                    </ul>

                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h4>用户管理</h4>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addUserModal"><i class="bi bi-plus-lg"></i> 新增用户</button>
                    </div>

                    <div class="card">
                        <div class="card-body p-0">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>用户名</th>
                                        <th>真实姓名</th>
                                        <th>手机号</th>
                                        <th>角色</th>
                                        <th>状态</th>
                                        <th>最后登录</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (count($users) > 0): ?>
                                        <?php foreach ($users as $user): ?>
                                            <tr>
                                                <td><?php echo htmlspecialchars($user['username']); ?></td>
                                                <td><?php echo htmlspecialchars($user['real_name'] ?? '-'); ?></td>
                                                <td><?php echo htmlspecialchars($user['phone'] ?? '-'); ?></td>
                                                <td><span class="badge bg-secondary"><?php echo htmlspecialchars($user['role_name'] ?? '-'); ?></span></td>
                                                <td>
                                                    <span class="badge <?php echo $user['status'] ? 'bg-success' : 'bg-danger'; ?>">
                                                        <?php echo $user['status'] ? '启用' : '禁用'; ?>
                                                    </span>
                                                </td>
                                                <td><?php echo $user['last_login_at'] ? Helper::formatDateTime($user['last_login_at']) : '-'; ?></td>
                                                <td>
                                                    <button class="btn btn-sm btn-outline-secondary" onclick="editUser(<?php echo htmlspecialchars(json_encode($user)); ?>)"><i class="bi bi-pencil"></i></button>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="7" class="text-center py-4 text-muted">暂无用户</td>
                                        </tr>
                                    <?php endif; ?>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="modal fade" id="addUserModal" tabindex="-1">
                        <div class="modal-dialog">
                            <form method="POST" action="users_save.php">
                                <input type="hidden" name="action" value="add">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">新增用户</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label class="form-label">用户名 <span class="text-danger">*</span></label>
                                            <input type="text" name="username" class="form-control" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">密码 <span class="text-danger">*</span></label>
                                            <input type="password" name="password" class="form-control" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">真实姓名</label>
                                            <input type="text" name="real_name" class="form-control">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">手机号</label>
                                            <input type="text" name="phone" class="form-control">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">角色 <span class="text-danger">*</span></label>
                                            <select name="role_id" class="form-select" required>
                                                <?php foreach ($roles as $r): ?>
                                                    <option value="<?php echo $r['id']; ?>"><?php echo htmlspecialchars($r['role_name']); ?></option>
                                                <?php endforeach; ?>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                        <button type="submit" class="btn btn-primary">保存</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div class="modal fade" id="editUserModal" tabindex="-1">
                        <div class="modal-dialog">
                            <form method="POST" action="users_save.php">
                                <input type="hidden" name="action" value="edit">
                                <input type="hidden" name="id" id="editUserId">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">编辑用户</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label class="form-label">用户名</label>
                                            <input type="text" name="username" id="editUsername" class="form-control" readonly>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">密码（留空不修改）</label>
                                            <input type="password" name="password" class="form-control">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">真实姓名</label>
                                            <input type="text" name="real_name" id="editRealName" class="form-control">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">手机号</label>
                                            <input type="text" name="phone" id="editPhone" class="form-control">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">角色</label>
                                            <select name="role_id" id="editRoleId" class="form-select">
                                                <?php foreach ($roles as $r): ?>
                                                    <option value="<?php echo $r['id']; ?>"><?php echo htmlspecialchars($r['role_name']); ?></option>
                                                <?php endforeach; ?>
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="status" id="editStatus" value="1">
                                                <label class="form-check-label" for="editStatus">启用状态</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                        <button type="submit" class="btn btn-primary">保存</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function editUser(user) {
            document.getElementById('editUserId').value = user.id;
            document.getElementById('editUsername').value = user.username;
            document.getElementById('editRealName').value = user.real_name || '';
            document.getElementById('editPhone').value = user.phone || '';
            document.getElementById('editRoleId').value = user.role_id;
            document.getElementById('editStatus').checked = user.status == 1;
            new bootstrap.Modal(document.getElementById('editUserModal')).show();
        }
    </script>
</body>
</html>
