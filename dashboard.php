<?php
require_once __DIR__ . '/bootstrap.php';
Auth::require();

$db = Database::getInstance();

$today = date('Y-m-d');
$todayStart = $today . ' 00:00:00';
$todayEnd = $today . ' 23:59:59';

$todayOrders = $db->fetchOne("SELECT COUNT(*) as count FROM work_orders WHERE created_at BETWEEN ? AND ?", [$todayStart, $todayEnd]);
$pendingOrders = $db->fetchOne("SELECT COUNT(*) as count FROM work_orders WHERE status IN (1,2,3)");
$todaySettlement = $db->fetchOne("SELECT COALESCE(SUM(paid_amount), 0) as total FROM settlements WHERE settle_time BETWEEN ? AND ?", [$todayStart, $todayEnd]);
$lowStockParts = $db->fetchOne("SELECT COUNT(*) as count FROM parts WHERE stock <= min_stock AND status = 1");

$recentOrders = $db->fetchAll("SELECT wo.*, c.name as customer_name, cv.plate_number FROM work_orders wo LEFT JOIN customers c ON wo.customer_id = c.id LEFT JOIN customer_vehicles cv ON wo.vehicle_id = cv.id ORDER BY wo.created_at DESC LIMIT 10");
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>仪表盘 - 汽车4S店维修业务管理系统</title>
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
        .stat-card {
            border: none;
            border-radius: 12px;
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-4px);
        }
        .stat-card .card-icon {
            width: 60px;
            height: 60px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            color: white;
        }
        .bg-primary-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .bg-success-gradient {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .bg-warning-gradient {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .bg-info-gradient {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .table th {
            border-top: none;
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
                    <a class="nav-link active" href="/dashboard.php"><i class="bi bi-speedometer2"></i> 仪表盘</a>
                    <a class="nav-link" href="/workorders/index.php"><i class="bi bi-tools"></i> 维修工单</a>
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
                            <span class="me-3 text-muted"><i class="bi bi-calendar3"></i> <?php echo date('Y-m-d H:i:s'); ?></span>
                            <div class="dropdown">
                                <button class="btn btn-light dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown">
                                    <i class="bi bi-person-circle"></i> <?php echo htmlspecialchars(Auth::user()['real_name'] ?? Auth::user()['username']); ?>
                                    <span class="badge bg-secondary ms-1"><?php echo htmlspecialchars(Auth::user()['role_name'] ?? ''); ?></span>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-end">
                                    <li><a class="dropdown-item" href="#"><i class="bi bi-person"></i> 个人资料</a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item" href="/logout.php"><i class="bi bi-box-arrow-left"></i> 退出登录</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </nav>

                <div class="offcanvas offcanvas-start d-md-none" tabindex="-1" id="sidebarOffcanvas">
                    <div class="offcanvas-header">
                        <h5 class="offcanvas-title">4S店维修系统</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
                    </div>
                    <div class="offcanvas-body">
                        <nav class="nav flex-column">
                            <a class="nav-link active" href="/dashboard.php"><i class="bi bi-speedometer2"></i> 仪表盘</a>
                            <a class="nav-link" href="/workorders/index.php"><i class="bi bi-tools"></i> 维修工单</a>
                            <a class="nav-link" href="/customers/index.php"><i class="bi bi-people"></i> 客户管理</a>
                            <a class="nav-link" href="/parts/index.php"><i class="bi bi-box-seam"></i> 配件管理</a>
                            <a class="nav-link" href="/settlements/index.php"><i class="bi bi-cash-coin"></i> 财务结算</a>
                            <a class="nav-link" href="/reports/index.php"><i class="bi bi-bar-chart"></i> 统计报表</a>
                            <hr class="my-3">
                            <a class="nav-link" href="/system/users.php"><i class="bi bi-gear"></i> 系统设置</a>
                        </nav>
                    </div>
                </div>

                <div class="p-4">
                    <h3 class="mb-4">仪表盘</h3>

                    <div class="row mb-4">
                        <div class="col-md-3 mb-3">
                            <div class="card stat-card shadow-sm">
                                <div class="card-body d-flex align-items-center">
                                    <div class="card-icon bg-primary-gradient me-3">
                                        <i class="bi bi-file-earmark-text"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0"><?php echo $todayOrders['count']; ?></h5>
                                        <small class="text-muted">今日工单</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card stat-card shadow-sm">
                                <div class="card-body d-flex align-items-center">
                                    <div class="card-icon bg-warning-gradient me-3">
                                        <i class="bi bi-hourglass-split"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0"><?php echo $pendingOrders['count']; ?></h5>
                                        <small class="text-muted">待处理工单</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card stat-card shadow-sm">
                                <div class="card-body d-flex align-items-center">
                                    <div class="card-icon bg-success-gradient me-3">
                                        <i class="bi bi-currency-yuan"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0">¥<?php echo Helper::formatMoney($todaySettlement['total']); ?></h5>
                                        <small class="text-muted">今日营业额</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="card stat-card shadow-sm">
                                <div class="card-body d-flex align-items-center">
                                    <div class="card-icon bg-info-gradient me-3">
                                        <i class="bi bi-exclamation-triangle"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0"><?php echo $lowStockParts['count']; ?></h5>
                                        <small class="text-muted">库存预警</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header d-flex justify-content-between align-items-center bg-white">
                                    <h5 class="mb-0">最新工单</h5>
                                    <a href="/workorders/index.php" class="btn btn-sm btn-outline-primary">查看全部</a>
                                </div>
                                <div class="card-body p-0">
                                    <table class="table table-hover mb-0">
                                        <thead class="table-light">
                                            <tr>
                                                <th>工单编号</th>
                                                <th>客户</th>
                                                <th>车牌</th>
                                                <th>工单类型</th>
                                                <th>状态</th>
                                                <th>创建时间</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <?php if (count($recentOrders) > 0): ?>
                                                <?php foreach ($recentOrders as $order): ?>
                                                    <tr>
                                                        <td><a href="/workorders/view.php?id=<?php echo $order['id']; ?>"><?php echo htmlspecialchars($order['order_no']); ?></a></td>
                                                        <td><?php echo htmlspecialchars($order['customer_name'] ?? '-'); ?></td>
                                                        <td><?php echo htmlspecialchars($order['plate_number'] ?? '-'); ?></td>
                                                        <td>
                                                            <?php
                                                            $types = ['1' => '保养', '2' => '维修', '3' => '事故', '4' => '索赔'];
                                                            echo $types[$order['order_type']] ?? '-';
                                                            ?>
                                                        </td>
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
                                                            $status = $statuses[$order['status']] ?? ['text' => '未知', 'class' => 'bg-secondary'];
                                                            ?>
                                                            <span class="status-badge <?php echo $status['class']; ?> text-white"><?php echo $status['text']; ?></span>
                                                        </td>
                                                        <td><?php echo Helper::formatDateTime($order['created_at']); ?></td>
                                                    </tr>
                                                <?php endforeach; ?>
                                            <?php else: ?>
                                                <tr>
                                                    <td colspan="6" class="text-center py-4 text-muted">暂无工单</td>
                                                </tr>
                                            <?php endif; ?>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
