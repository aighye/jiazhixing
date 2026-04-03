<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>统计报表 - 汽车4S店维修业务管理系统</title>
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
        }
        .stat-card .card-icon {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
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
                    <a class="nav-link active" href="/reports/index.php"><i class="bi bi-bar-chart"></i> 统计报表</a>
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
                    <h3 class="mb-4">统计报表</h3>

                    <div class="card mb-4">
                        <div class="card-body">
                            <form method="GET" class="row g-3">
                                <div class="col-md-3">
                                    <label class="form-label">开始日期</label>
                                    <input type="date" name="start_date" class="form-control" value="<?php echo $_GET['start_date'] ?? date('Y-m-01'); ?>">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">结束日期</label>
                                    <input type="date" name="end_date" class="form-control" value="<?php echo $_GET['end_date'] ?? date('Y-m-d'); ?>">
                                </div>
                                <div class="col-md-3 align-self-end">
                                    <button type="submit" class="btn btn-primary w-100"><i class="bi bi-search"></i> 查询</button>
                                </div>
                                <div class="col-md-3 align-self-end">
                                    <button type="button" class="btn btn-outline-success w-100" onclick="exportExcel()"><i class="bi bi-file-earmark-excel"></i> 导出Excel</button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <?php
                    $startDate = $_GET['start_date'] ?? date('Y-m-01');
                    $endDate = $_GET['end_date'] ?? date('Y-m-d');
                    $start = $startDate . ' 00:00:00';
                    $end = $endDate . ' 23:59:59';

                    $stats = [
                        'orders' => $db->fetchOne("SELECT COUNT(*) as count FROM work_orders WHERE created_at BETWEEN ? AND ?", [$start, $end])['count'],
                        'revenue' => $db->fetchOne("SELECT COALESCE(SUM(paid_amount), 0) as total FROM settlements WHERE settle_time BETWEEN ? AND ?", [$start, $end])['total'],
                        'customers' => $db->fetchOne("SELECT COUNT(*) as count FROM customers WHERE created_at BETWEEN ? AND ?", [$start, $end])['count']
                    ];
                    ?>

                    <div class="row mb-4">
                        <div class="col-md-4 mb-3">
                            <div class="card stat-card shadow-sm">
                                <div class="card-body d-flex align-items-center">
                                    <div class="card-icon bg-primary-gradient me-3">
                                        <i class="bi bi-file-earmark-text"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0"><?php echo $stats['orders']; ?></h5>
                                        <small class="text-muted">工单数量</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="card stat-card shadow-sm">
                                <div class="card-body d-flex align-items-center">
                                    <div class="card-icon bg-success-gradient me-3">
                                        <i class="bi bi-currency-yuan"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0">¥<?php echo Helper::formatMoney($stats['revenue']); ?></h5>
                                        <small class="text-muted">营业收入</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="card stat-card shadow-sm">
                                <div class="card-body d-flex align-items-center">
                                    <div class="card-icon bg-info-gradient me-3">
                                        <i class="bi bi-people"></i>
                                    </div>
                                    <div>
                                        <h5 class="mb-0"><?php echo $stats['customers']; ?></h5>
                                        <small class="text-muted">新增客户</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card mb-4">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">营业明细</h5>
                        </div>
                        <div class="card-body p-0">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>日期</th>
                                        <th>工单数量</th>
                                        <th>结算金额</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php
                                    $daily = $db->fetchAll("SELECT DATE(settle_time) as day, COUNT(*) as count, SUM(paid_amount) as total FROM settlements WHERE settle_time BETWEEN ? AND ? GROUP BY DATE(settle_time) ORDER BY day DESC", [$start, $end]);
                                    if (count($daily) > 0):
                                        foreach ($daily as $d):
                                    ?>
                                        <tr>
                                            <td><?php echo $d['day']; ?></td>
                                            <td><?php echo $d['count']; ?></td>
                                            <td class="text-primary fw-bold">¥<?php echo Helper::formatMoney($d['total']); ?></td>
                                        </tr>
                                    <?php
                                        endforeach;
                                    else:
                                    ?>
                                        <tr>
                                            <td colspan="3" class="text-center py-4 text-muted">暂无数据</td>
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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function exportExcel() {
            alert('导出功能开发中...');
        }
    </script>
</body>
</html>
