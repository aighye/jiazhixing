<?php
require_once __DIR__ . '/../../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$customerId = (int)($_GET['customer_id'] ?? 0);
if (!$customerId) {
    Helper::redirect('/customers/index.php');
}

$customer = $db->fetchOne("SELECT id, name FROM customers WHERE id = ?", [$customerId]);
if (!$customer) {
    Helper::redirect('/customers/index.php');
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = [
        'customer_id' => $customerId,
        'plate_number' => trim($_POST['plate_number']),
        'vin' => trim($_POST['vin']),
        'engine_no' => trim($_POST['engine_no']),
        'brand' => trim($_POST['brand']),
        'model' => trim($_POST['model']),
        'color' => trim($_POST['color']),
        'displacement' => trim($_POST['displacement']),
        'purchase_date' => !empty($_POST['purchase_date']) ? $_POST['purchase_date'] : null,
        'registration_date' => !empty($_POST['registration_date']) ? $_POST['registration_date'] : null,
        'insurance_date' => !empty($_POST['insurance_date']) ? $_POST['insurance_date'] : null,
        'inspection_date' => !empty($_POST['inspection_date']) ? $_POST['inspection_date'] : null,
        'mileage' => (int)$_POST['mileage'],
        'remark' => trim($_POST['remark']),
        'is_default' => isset($_POST['is_default']) ? 1 : 0
    ];

    if (empty($data['plate_number'])) {
        $error = '请填写车牌号';
    } else {
        if ($data['is_default']) {
            $db->update('customer_vehicles', ['is_default' => 0], 'customer_id = ?', [$customerId]);
        }
        $db->insert('customer_vehicles', $data);
        Logger::log('新增车辆', "为客户 {$customer['name']} 添加车辆: {$data['plate_number']}", 'customers');
        Helper::redirect('/customers/view.php?id=' . $customerId);
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>添加车辆 - 汽车4S店维修业务管理系统</title>
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
                            <a href="/customers/view.php?id=<?php echo $customerId; ?>" class="btn btn-outline-secondary btn-sm me-2"><i class="bi bi-arrow-left"></i> 返回</a>
                            <span class="h3">添加车辆 - <?php echo htmlspecialchars($customer['name']); ?></span>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-body">
                            <?php if (isset($error)): ?>
                                <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
                            <?php endif; ?>

                            <form method="POST">
                                <div class="row">
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">车牌号 <span class="text-danger">*</span></label>
                                        <input type="text" name="plate_number" class="form-control" required>
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">品牌</label>
                                        <input type="text" name="brand" class="form-control">
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">车型</label>
                                        <input type="text" name="model" class="form-control">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">车架号(VIN)</label>
                                        <input type="text" name="vin" class="form-control">
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">发动机号</label>
                                        <input type="text" name="engine_no" class="form-control">
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">颜色</label>
                                        <input type="text" name="color" class="form-control">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-3 mb-3">
                                        <label class="form-label">排量</label>
                                        <input type="text" name="displacement" class="form-control">
                                    </div>
                                    <div class="col-md-3 mb-3">
                                        <label class="form-label">当前里程(km)</label>
                                        <input type="number" name="mileage" class="form-control" value="0">
                                    </div>
                                    <div class="col-md-3 mb-3">
                                        <label class="form-label">购车日期</label>
                                        <input type="date" name="purchase_date" class="form-control">
                                    </div>
                                    <div class="col-md-3 mb-3">
                                        <label class="form-label">上牌日期</label>
                                        <input type="date" name="registration_date" class="form-control">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">保险到期日</label>
                                        <input type="date" name="insurance_date" class="form-control">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">年检到期日</label>
                                        <input type="date" name="inspection_date" class="form-control">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">备注</label>
                                    <textarea name="remark" class="form-control" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="is_default" id="is_default">
                                        <label class="form-check-label" for="is_default">设为默认车辆</label>
                                    </div>
                                </div>
                                <div class="d-flex gap-2">
                                    <button type="submit" class="btn btn-primary"><i class="bi bi-save"></i> 保存</button>
                                    <a href="/customers/view.php?id=<?php echo $customerId; ?>" class="btn btn-outline-secondary">取消</a>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
