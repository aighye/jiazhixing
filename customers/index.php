<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$limit = 15;
$offset = ($page - 1) * $limit;
$keyword = trim($_GET['keyword'] ?? '');

$where = 'WHERE 1=1';
$params = [];

if ($keyword) {
    $where .= ' AND (name LIKE ? OR phone LIKE ? OR customer_no LIKE ?)';
    $likeKeyword = "%{$keyword}%";
    $params = [$likeKeyword, $likeKeyword, $likeKeyword];
}

$total = $db->fetchOne("SELECT COUNT(*) as count FROM customers {$where}", $params)['count'];
$customers = $db->fetchAll("SELECT * FROM customers {$where} ORDER BY created_at DESC LIMIT {$limit} OFFSET {$offset}", $params);
$pagination = Helper::pagination($total, $page, $limit);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>客户管理 - 汽车4S店维修业务管理系统</title>
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
        .member-badge {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
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
                    <a class="nav-link active" href="/customers/index.php"><i class="bi bi-people"></i> 客户管理</a>
                    <a class="nav-link" href="/parts/index.php"><i class="bi bi-box-seam"></i> 配件管理</a>
                    <a class="nav-link" href="/settlements/index.php"><i class="bi bi-cash-coin"></i> 财务结算</a>
                    <a class="nav-link" href="/reports/index.php"><i class="bi bi-bar-chart"></i> 统计报表</a>
                    <hr class="my-3 text-secondary mx-3">
                    <a class="nav-link" href="/system/users.php"><i class="bi bi-gear"></i> 系统设置</a>
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
                            <div class="dropdown">
                                <button class="btn btn-light dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown">
                                    <i class="bi bi-person-circle"></i> <?php echo htmlspecialchars(Auth::user()['real_name'] ?? Auth::user()['username']); ?>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-end">
                                    <li><a class="dropdown-item" href="/logout.php"><i class="bi bi-box-arrow-left"></i> 退出登录</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </nav>

                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h3>客户管理</h3>
                        <a href="add.php" class="btn btn-primary"><i class="bi bi-plus-lg"></i> 新增客户</a>
                    </div>

                    <div class="card mb-4">
                        <div class="card-body">
                            <form method="GET" class="row g-3">
                                <div class="col-md-4">
                                <input type="text" name="keyword" class="form-control" placeholder="搜索客户姓名、手机号或客户编号" value="<?php echo htmlspecialchars($keyword); ?>">
                                </div>
                                <div class="col-md-2">
                                    <button type="submit" class="btn btn-primary w-100"><i class="bi bi-search"></i> 搜索</button>
                                </div>
                                <div class="col-md-2">
                                    <a href="index.php" class="btn btn-outline-secondary w-100"><i class="bi bi-x-circle"></i> 重置</a>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-body p-0">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>客户编号</th>
                                        <th>姓名</th>
                                        <th>手机号</th>
                                        <th>会员等级</th>
                                        <th>积分</th>
                                        <th>余额</th>
                                        <th>状态</th>
                                        <th>创建时间</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (count($customers) > 0): ?>
                                        <?php foreach ($customers as $customer): ?>
                                            <tr>
                                                <td><?php echo htmlspecialchars($customer['customer_no'] ?? '-'); ?></td>
                                                <td><?php echo htmlspecialchars($customer['name']); ?></td>
                                                <td><?php echo htmlspecialchars($customer['phone']); ?></td>
                                                <td>
                                                    <?php
                                                    $levels = [1 => '普通', 2 => '银卡', 3 => '金卡', 4 => '钻石'];
                                                    $levelClasses = [1 => 'bg-secondary', 2 => 'bg-info', 3 => 'bg-warning', 4 => 'bg-primary'];
                                                    ?>
                                                    <span class="member-badge <?php echo $levelClasses[$customer['member_level']] ?? 'bg-secondary'; ?> text-white">
                                                        <?php echo $levels[$customer['member_level']] ?? '普通'; ?>
                                                    </span>
                                                </td>
                                                <td><?php echo number_format($customer['member_points']); ?></td>
                                                <td>¥<?php echo Helper::formatMoney($customer['balance']); ?></td>
                                                <td>
                                                    <span class="badge <?php echo $customer['status'] ? 'bg-success' : 'bg-danger'; ?>">
                                                        <?php echo $customer['status'] ? '正常' : '禁用'; ?>
                                                    </span>
                                                </td>
                                                <td><?php echo Helper::formatDateTime($customer['created_at']); ?></td>
                                                <td>
                                                    <a href="view.php?id=<?php echo $customer['id']; ?>" class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i></a>
                                                    <a href="edit.php?id=<?php echo $customer['id']; ?>" class="btn btn-sm btn-outline-secondary"><i class="bi bi-pencil"></i></a>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="9" class="text-center py-4 text-muted">暂无客户数据</td>
                                        </tr>
                                    <?php endif; ?>
                                </tbody>
                            </table>
                        </div>
                        <?php if ($pagination['total_pages'] > 1): ?>
                            <div class="card-footer">
                                <nav>
                                    <ul class="pagination justify-content-center mb-0">
                                        <?php if ($pagination['has_prev']): ?>
                                            <li class="page-item"><a class="page-link" href="?page=<?php echo $page - 1; ?>&keyword=<?php echo urlencode($keyword); ?>">上一页</a></li>
                                        <?php endif; ?>
                                        <?php for ($i = max(1, $page - 2); $i <= min($pagination['total_pages'], $page + 2); $i++): ?>
                                            <li class="page-item <?php echo $i == $page ? 'active' : ''; ?>">
                                                <a class="page-link" href="?page=<?php echo $i; ?>&keyword=<?php echo urlencode($keyword); ?>"><?php echo $i; ?></a>
                                            </li>
                                        <?php endfor; ?>
                                        <?php if ($pagination['has_next']): ?>
                                            <li class="page-item"><a class="page-link" href="?page=<?php echo $page + 1; ?>&keyword=<?php echo urlencode($keyword); ?>">下一页</a></li>
                                        <?php endif; ?>
                                    </ul>
                                </nav>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
