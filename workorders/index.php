<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$limit = 15;
$offset = ($page - 1) * $limit;
$keyword = trim($_GET['keyword'] ?? '');
$status = isset($_GET['status']) ? (int)$_GET['status'] : 0;

$where = 'WHERE 1=1';
$params = [];

if ($keyword) {
    $where .= ' AND (wo.order_no LIKE ? OR c.name LIKE ? OR cv.plate_number LIKE ?)';
    $likeKeyword = "%{$keyword}%";
    $params = [$likeKeyword, $likeKeyword, $likeKeyword];
}
if ($status) {
    $where .= ' AND wo.status = ?';
    $params[] = $status;
}

$total = $db->fetchOne("SELECT COUNT(*) as count FROM work_orders wo LEFT JOIN customers c ON wo.customer_id = c.id LEFT JOIN customer_vehicles cv ON wo.vehicle_id = cv.id {$where}", $params)['count'];
$orders = $db->fetchAll("SELECT wo.*, c.name as customer_name, cv.plate_number FROM work_orders wo LEFT JOIN customers c ON wo.customer_id = c.id LEFT JOIN customer_vehicles cv ON wo.vehicle_id = cv.id {$where} ORDER BY wo.created_at DESC LIMIT {$limit} OFFSET {$offset}", $params);
$pagination = Helper::pagination($total, $page, $limit);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>维修工单 - 汽车4S店维修业务管理系统</title>
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
        .status-badge {
            padding: 4px 10px;
            border-radius: 20px;
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
                    <a class="nav-link active" href="/workorders/index.php"><i class="bi bi-tools"></i> 维修工单</a>
                    <a class="nav-link" href="/customers/index.php"><i class="bi bi-people"></i> 客户管理</a>
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
                            <a href="/logout.php" class="btn btn-outline-danger"><i class="bi bi-box-arrow-left"></i> 退出</a>
                        </div>
                    </div>
                </nav>

                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h3>维修工单</h3>
                        <a href="add.php" class="btn btn-primary"><i class="bi bi-plus-lg"></i> 新建工单</a>
                    </div>

                    <div class="card mb-4">
                        <div class="card-body">
                            <form method="GET" class="row g-3">
                                <div class="col-md-4">
                                    <input type="text" name="keyword" class="form-control" placeholder="搜索工单编号、客户姓名或车牌" value="<?php echo htmlspecialchars($keyword); ?>">
                                </div>
                                <div class="col-md-3">
                                    <select name="status" class="form-select">
                                        <option value="0">全部状态</option>
                                        <option value="1" <?php echo $status == 1 ? 'selected' : ''; ?>>待派工</option>
                                        <option value="2" <?php echo $status == 2 ? 'selected' : ''; ?>>维修中</option>
                                        <option value="3" <?php echo $status == 3 ? 'selected' : ''; ?>>待质检</option>
                                        <option value="4" <?php echo $status == 4 ? 'selected' : ''; ?>>已完成</option>
                                        <option value="5" <?php echo $status == 5 ? 'selected' : ''; ?>>已结算</option>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <button type="submit" class="btn btn-primary w-100"><i class="bi bi-search"></i> 搜索</button>
                                </div>
                                <div class="col-md-3">
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
                                        <th>工单编号</th>
                                        <th>客户</th>
                                        <th>车牌</th>
                                        <th>类型</th>
                                        <th>预估金额</th>
                                        <th>状态</th>
                                        <th>创建时间</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (count($orders) > 0): ?>
                                        <?php foreach ($orders as $order): ?>
                                            <tr>
                                                <td><a href="view.php?id=<?php echo $order['id']; ?>" class="fw-bold"><?php echo htmlspecialchars($order['order_no']); ?></a></td>
                                                <td><?php echo htmlspecialchars($order['customer_name'] ?? '-'); ?></td>
                                                <td><?php echo htmlspecialchars($order['plate_number'] ?? '-'); ?></td>
                                                <td><?php $types = ['1' => '保养', '2' => '维修', '3' => '事故', '4' => '索赔']; echo $types[$order['order_type']] ?? '-'; ?></td>
                                                <td>¥<?php echo Helper::formatMoney($order['estimated_amount']); ?></td>
                                                <td>
                                                    <?php
                                                    $statuses = [
                                                        '1' => ['text' => '待派工', 'class' => 'bg-warning'],
                                                        '2' => ['text' => '维修中', 'class' => 'bg-primary'],
                                                        '3' => ['text' => '待质检', 'class' => 'bg-info'],
                                                        '4' => ['text' => '已完成', 'class' => 'bg-success'],
                                                        '5' => ['text' => '已结算', 'class' => 'bg-secondary'],
                                                        '6' => ['text' => '已关闭', 'class' => 'bg-dark']
                                                    ];
                                                    $s = $statuses[$order['status']] ?? ['text' => '未知', 'class' => 'bg-secondary'];
                                                    ?>
                                                    <span class="status-badge <?php echo $s['class']; ?> text-white"><?php echo $s['text']; ?></span>
                                                </td>
                                                <td><?php echo Helper::formatDateTime($order['created_at']); ?></td>
                                                <td>
                                                    <a href="view.php?id=<?php echo $order['id']; ?>" class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i></a>
                                                    <?php if ($order['status'] < 4): ?>
                                                        <a href="edit.php?id=<?php echo $order['id']; ?>" class="btn btn-sm btn-outline-secondary"><i class="bi bi-pencil"></i></a>
                                                    <?php endif; ?>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="8" class="text-center py-4 text-muted">暂无工单</td>
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
                                            <li class="page-item"><a class="page-link" href="?page=<?php echo $page - 1; ?>&keyword=<?php echo urlencode($keyword); ?>&status=<?php echo $status; ?>">上一页</a></li>
                                        <?php endif; ?>
                                        <?php for ($i = max(1, $page - 2); $i <= min($pagination['total_pages'], $page + 2); $i++): ?>
                                            <li class="page-item <?php echo $i == $page ? 'active' : ''; ?>">
                                                <a class="page-link" href="?page=<?php echo $i; ?>&keyword=<?php echo urlencode($keyword); ?>&status=<?php echo $status; ?>"><?php echo $i; ?></a>
                                            </li>
                                        <?php endfor; ?>
                                        <?php if ($pagination['has_next']): ?>
                                            <li class="page-item"><a class="page-link" href="?page=<?php echo $page + 1; ?>&keyword=<?php echo urlencode($keyword); ?>&status=<?php echo $status; ?>">下一页</a></li>
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
