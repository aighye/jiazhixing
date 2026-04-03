<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$limit = 15;
$offset = ($page - 1) * $limit;

$total = $db->fetchOne("SELECT COUNT(*) as count FROM settlements")['count'];
$settlements = $db->fetchAll("SELECT s.*, wo.order_no, c.name as customer_name FROM settlements s LEFT JOIN work_orders wo ON s.order_id = wo.id LEFT JOIN customers c ON wo.customer_id = c.id ORDER BY s.created_at DESC LIMIT {$limit} OFFSET {$offset}");
$pagination = Helper::pagination($total, $page, $limit);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>财务结算 - 汽车4S店维修业务管理系统</title>
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
                    <a class="nav-link active" href="/settlements/index.php"><i class="bi bi-cash-coin"></i> 财务结算</a>
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
                        <h3>财务结算</h3>
                    </div>

                    <div class="card">
                        <div class="card-body p-0">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>结算单号</th>
                                        <th>工单编号</th>
                                        <th>客户</th>
                                        <th>总金额</th>
                                        <th>优惠</th>
                                        <th>实付</th>
                                        <th>支付方式</th>
                                        <th>结算时间</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (count($settlements) > 0): ?>
                                        <?php foreach ($settlements as $s): ?>
                                            <tr>
                                                <td><?php echo htmlspecialchars($s['settle_no']); ?></td>
                                                <td><a href="/workorders/view.php?id=<?php echo $s['order_id']; ?>"><?php echo htmlspecialchars($s['order_no'] ?? '-'); ?></a></td>
                                                <td><?php echo htmlspecialchars($s['customer_name'] ?? '-'); ?></td>
                                                <td>¥<?php echo Helper::formatMoney($s['total_amount']); ?></td>
                                                <td>-¥<?php echo Helper::formatMoney($s['discount_amount']); ?></td>
                                                <td class="fw-bold text-primary">¥<?php echo Helper::formatMoney($s['paid_amount']); ?></td>
                                                <td><?php echo htmlspecialchars($s['payment_method'] ?? '-'); ?></td>
                                                <td><?php echo Helper::formatDateTime($s['settle_time']); ?></td>
                                                <td>
                                                    <a href="view.php?id=<?php echo $s['id']; ?>" class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i></a>
                                                    <button class="btn btn-sm btn-outline-secondary"><i class="bi bi-printer"></i></button>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="9" class="text-center py-4 text-muted">暂无结算记录</td>
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
                                            <li class="page-item"><a class="page-link" href="?page=<?php echo $page - 1; ?>">上一页</a></li>
                                        <?php endif; ?>
                                        <?php for ($i = max(1, $page - 2); $i <= min($pagination['total_pages'], $page + 2); $i++): ?>
                                            <li class="page-item <?php echo $i == $page ? 'active' : ''; ?>">
                                                <a class="page-link" href="?page=<?php echo $i; ?>"><?php echo $i; ?></a>
                                            </li>
                                        <?php endfor; ?>
                                        <?php if ($pagination['has_next']): ?>
                                            <li class="page-item"><a class="page-link" href="?page=<?php echo $page + 1; ?>">下一页</a></li>
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
