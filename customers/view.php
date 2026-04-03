<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$id = (int)($_GET['id'] ?? 0);
$customer = $db->fetchOne("SELECT * FROM customers WHERE id = ?", [$id]);

if (!$customer) {
    Helper::redirect('index.php');
}

$vehicles = $db->fetchAll("SELECT * FROM customer_vehicles WHERE customer_id = ? ORDER BY is_default DESC, id DESC", [$id]);
$orders = $db->fetchAll("SELECT wo.*, cv.plate_number FROM work_orders wo LEFT JOIN customer_vehicles cv ON wo.vehicle_id = cv.id WHERE wo.customer_id = ? ORDER BY wo.created_at DESC LIMIT 10", [$id]);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>客户详情 - 汽车4S店维修业务管理系统</title>
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
        .info-label {
            color: #6c757d;
            font-size: 14px;
        }
        .info-value {
            font-weight: 500;
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
                            <a href="/logout.php" class="btn btn-outline-danger"><i class="bi bi-box-arrow-left"></i> 退出</a>
                        </div>
                    </div>
                </nav>

                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <a href="index.php" class="btn btn-outline-secondary btn-sm me-2"><i class="bi bi-arrow-left"></i> 返回</a>
                            <span class="h3">客户详情</span>
                        </div>
                        <div class="gap-2">
                            <a href="edit.php?id=<?php echo $customer['id']; ?>" class="btn btn-primary"><i class="bi bi-pencil"></i> 编辑</a>
                            <a href="/workorders/add.php?customer_id=<?php echo $customer['id']; ?>" class="btn btn-success"><i class="bi bi-plus-lg"></i> 创建工单</a>
                        </div>
                    </div>

                    <div class="card mb-4">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">基本信息</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3 mb-3">
                                    <div class="info-label">客户编号</div>
                                    <div class="info-value"><?php echo htmlspecialchars($customer['customer_no'] ?? '-'); ?></div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="info-label">姓名</div>
                                    <div class="info-value"><?php echo htmlspecialchars($customer['name']); ?></div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="info-label">手机号</div>
                                    <div class="info-value"><?php echo htmlspecialchars($customer['phone']); ?></div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="info-label">会员等级</div>
                                    <div class="info-value">
                                        <?php
                                        $levels = [1 => '普通', 2 => '银卡', 3 => '金卡', 4 => '钻石'];
                                        echo $levels[$customer['member_level']];
                                        ?>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3 mb-3">
                                    <div class="info-label">会员积分</div>
                                    <div class="info-value"><?php echo number_format($customer['member_points']); ?></div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="info-label">账户余额</div>
                                    <div class="info-value text-primary fw-bold">¥<?php echo Helper::formatMoney($customer['balance']); ?></div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="info-label">状态</div>
                                    <div class="info-value">
                                        <span class="badge <?php echo $customer['status'] ? 'bg-success' : 'bg-danger'; ?>">
                                            <?php echo $customer['status'] ? '正常' : '禁用'; ?>
                                        </span>
                                    </div>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <div class="info-label">创建时间</div>
                                    <div class="info-value"><?php echo Helper::formatDateTime($customer['created_at']); ?></div>
                                </div>
                            </div>
                            <?php if ($customer['address'] || $customer['email']): ?>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <div class="info-label">邮箱</div>
                                        <div class="info-value"><?php echo htmlspecialchars($customer['email'] ?? '-'); ?></div>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <div class="info-label">地址</div>
                                        <div class="info-value"><?php echo htmlspecialchars($customer['address'] ?? '-'); ?></div>
                                    </div>
                                </div>
                            <?php endif; ?>
                            <?php if ($customer['remark']): ?>
                                <div class="mt-3">
                                    <div class="info-label">备注</div>
                                    <div class="info-value"><?php echo htmlspecialchars($customer['remark']); ?></div>
                                </div>
                            <?php endif; ?>
                        </div>
                    </div>

                    <div class="card mb-4">
                        <div class="card-header bg-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">车辆档案</h5>
                            <a href="vehicles/add.php?customer_id=<?php echo $customer['id']; ?>" class="btn btn-sm btn-outline-primary"><i class="bi bi-plus"></i> 添加车辆</a>
                        </div>
                        <div class="card-body p-0">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>车牌号</th>
                                        <th>品牌车型</th>
                                        <th>车架号</th>
                                        <th>颜色</th>
                                        <th>当前里程</th>
                                        <th>购车日期</th>
                                        <th>默认</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (count($vehicles) > 0): ?>
                                        <?php foreach ($vehicles as $v): ?>
                                            <tr>
                                                <td class="fw-bold"><?php echo htmlspecialchars($v['plate_number']); ?></td>
                                                <td><?php echo htmlspecialchars($v['brand'] . ' ' . $v['model']); ?></td>
                                                <td><?php echo htmlspecialchars($v['vin'] ?? '-'); ?></td>
                                                <td><?php echo htmlspecialchars($v['color'] ?? '-'); ?></td>
                                                <td><?php echo number_format($v['mileage']); ?> km</td>
                                                <td><?php echo $v['purchase_date'] ? Helper::formatDate($v['purchase_date']) : '-'; ?></td>
                                                <td><?php echo $v['is_default'] ? '<span class="badge bg-success">是</span>' : ''; ?></td>
                                                <td>
                                                    <a href="vehicles/edit.php?id=<?php echo $v['id']; ?>" class="btn btn-sm btn-outline-secondary"><i class="bi bi-pencil"></i></a>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="8" class="text-center py-4 text-muted">暂无车辆档案</td>
                                        </tr>
                                    <?php endif; ?>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">历史工单</h5>
                        </div>
                        <div class="card-body p-0">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>工单编号</th>
                                        <th>车牌</th>
                                        <th>类型</th>
                                        <th>状态</th>
                                        <th>金额</th>
                                        <th>创建时间</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (count($orders) > 0): ?>
                                        <?php foreach ($orders as $o): ?>
                                            <tr>
                                                <td><a href="/workorders/view.php?id=<?php echo $o['id']; ?>"><?php echo htmlspecialchars($o['order_no']); ?></a></td>
                                                <td><?php echo htmlspecialchars($o['plate_number'] ?? '-'); ?></td>
                                                <td><?php $types = ['1' => '保养', '2' => '维修', '3' => '事故', '4' => '索赔']; echo $types[$o['order_type']] ?? '-'; ?></td>
                                                <td>
                                                    <?php
                                                    $statuses = ['1' => '待派工', '2' => '维修中', '3' => '待质检', '4' => '已完成', '5' => '已结算', '6' => '已关闭'];
                                                    echo $statuses[$o['status']] ?? '未知';
                                                    ?>
                                                </td>
                                                <td>¥<?php echo Helper::formatMoney($o['final_amount']); ?></td>
                                                <td><?php echo Helper::formatDateTime($o['created_at']); ?></td>
                                                <td><a href="/workorders/view.php?id=<?php echo $o['id']; ?>" class="btn btn-sm btn-outline-primary">查看</a></td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="7" class="text-center py-4 text-muted">暂无历史工单</td>
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
</body>
</html>
