<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$customerId = (int)($_GET['customer_id'] ?? 0);
$customers = $db->fetchAll("SELECT id, name, phone FROM customers WHERE status = 1 ORDER BY created_at DESC");
$vehicles = [];
$selectedCustomer = null;

if ($customerId) {
    $selectedCustomer = $db->fetchOne("SELECT * FROM customers WHERE id = ?", [$customerId]);
    if ($selectedCustomer) {
        $vehicles = $db->fetchAll("SELECT * FROM customer_vehicles WHERE customer_id = ? ORDER BY is_default DESC, id DESC", [$customerId]);
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $db->beginTransaction();
    try {
        $data = [
            'order_no' => Helper::generateOrderNo('WO'),
            'customer_id' => (int)$_POST['customer_id'],
            'vehicle_id' => (int)$_POST['vehicle_id'],
            'order_type' => (int)$_POST['order_type'],
            'source' => trim($_POST['source']),
            'fault_desc' => trim($_POST['fault_desc']),
            'service_request' => trim($_POST['service_request']),
            'estimated_amount' => (float)$_POST['estimated_amount'],
            'receiver_id' => Auth::id(),
            'status' => 1,
            'urgent' => isset($_POST['urgent']) ? 1 : 0,
            'remark' => trim($_POST['remark'])
        ];

        if (!empty($_POST['promise_date'])) {
            $data['promise_date'] = $_POST['promise_date'];
        }

        $orderId = $db->insert('work_orders', $data);

        if (!empty($_POST['service_names'])) {
            foreach ($_POST['service_names'] as $i => $serviceName) {
                if (!empty($serviceName)) {
                    $service = [
                        'order_id' => $orderId,
                        'service_name' => $serviceName,
                        'service_type' => $_POST['service_types'][$i] ?? '',
                        'hours' => (float)($_POST['service_hours'][$i] ?? 0),
                        'hour_price' => (float)($_POST['service_hour_prices'][$i] ?? 0),
                        'amount' => (float)($_POST['service_amounts'][$i] ?? 0),
                        'sort' => $i
                    ];
                    $db->insert('work_order_services', $service);
                }
            }
        }

        $db->insert('work_order_logs', [
            'order_id' => $orderId,
            'status' => 1,
            'operator_id' => Auth::id(),
            'operator_name' => Auth::user()['real_name'] ?? Auth::user()['username'],
            'content' => '创建工单'
        ]);

        $db->commit();
        Logger::log('创建工单', "创建工单: {$data['order_no']}", 'workorders');
        Helper::redirect('view.php?id=' . $orderId);
    } catch (Exception $e) {
        $db->rollback();
        $error = '创建工单失败: ' . $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新建工单 - 汽车4S店维修业务管理系统</title>
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
        .service-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
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
                            <a href="/logout.php" class="btn btn-outline-danger"><i class="bi bi-box-arrow-left"></i> 退出</a>
                        </div>
                    </div>
                </nav>

                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <a href="index.php" class="btn btn-outline-secondary btn-sm me-2"><i class="bi bi-arrow-left"></i> 返回</a>
                            <span class="h3">新建工单</span>
                        </div>
                    </div>

                    <?php if (isset($error)): ?>
                        <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
                    <?php endif; ?>

                    <form method="POST" id="workOrderForm">
                        <div class="card mb-4">
                            <div class="card-header bg-white">
                                <h5 class="mb-0">客户与车辆信息</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">选择客户 <span class="text-danger">*</span></label>
                                        <select name="customer_id" id="customerSelect" class="form-select" required onchange="loadVehicles()">
                                            <option value="">请选择客户</option>
                                            <?php foreach ($customers as $c): ?>
                                                <option value="<?php echo $c['id']; ?>" <?php echo $selectedCustomer && $selectedCustomer['id'] == $c['id'] ? 'selected' : ''; ?>>
                                                    <?php echo htmlspecialchars($c['name']); ?> - <?php echo htmlspecialchars($c['phone']); ?>
                                                </option>
                                            <?php endforeach; ?>
                                        </select>
                                        <div class="form-text mt-1"><a href="/customers/add.php" target="_blank">+ 新增客户</a></div>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">选择车辆 <span class="text-danger">*</span></label>
                                        <select name="vehicle_id" id="vehicleSelect" class="form-select" required>
                                            <option value="">请先选择客户</option>
                                            <?php foreach ($vehicles as $v): ?>
                                                <option value="<?php echo $v['id']; ?>"><?php echo htmlspecialchars($v['plate_number']); ?> - <?php echo htmlspecialchars($v['brand'] . ' ' . $v['model']); ?></option>
                                            <?php endforeach; ?>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="card mb-4">
                            <div class="card-header bg-white">
                                <h5 class="mb-0">工单信息</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">工单类型 <span class="text-danger">*</span></label>
                                        <select name="order_type" class="form-select" required>
                                            <option value="1">保养</option>
                                            <option value="2" selected>维修</option>
                                            <option value="3">事故</option>
                                            <option value="4">索赔</option>
                                        </select>
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">工单来源</label>
                                        <select name="source" class="form-select">
                                            <option value="到店">到店</option>
                                            <option value="电话">电话</option>
                                            <option value="网络">网络</option>
                                            <option value="救援">救援</option>
                                        </select>
                                    </div>
                                    <div class="col-md-4 mb-3">
                                        <label class="form-label">承诺交车时间</label>
                                        <input type="datetime-local" name="promise_date" class="form-control">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-12 mb-3">
                                        <label class="form-label">故障描述</label>
                                        <textarea name="fault_desc" class="form-control" rows="3" placeholder="请详细描述车辆故障现象..."></textarea>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-12 mb-3">
                                        <label class="form-label">服务要求</label>
                                        <textarea name="service_request" class="form-control" rows="2" placeholder="客户特殊要求..."></textarea>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">预估金额</label>
                                        <input type="number" name="estimated_amount" class="form-control" step="0.01" value="0">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <div class="form-check mt-4">
                                            <input class="form-check-input" type="checkbox" name="urgent" id="urgent">
                                            <label class="form-check-label" for="urgent">加急工单</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="card mb-4">
                            <div class="card-header bg-white d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">维修项目</h5>
                                <button type="button" class="btn btn-sm btn-outline-primary" onclick="addServiceItem()"><i class="bi bi-plus"></i> 添加项目</button>
                            </div>
                            <div class="card-body" id="serviceItemsContainer">
                            </div>
                        </div>

                        <div class="card mb-4">
                            <div class="card-header bg-white">
                                <h5 class="mb-0">备注</h5>
                            </div>
                            <div class="card-body">
                                <textarea name="remark" class="form-control" rows="2" placeholder="内部备注信息..."></textarea>
                            </div>
                        </div>

                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary btn-lg"><i class="bi bi-save"></i> 创建工单</button>
                            <a href="index.php" class="btn btn-outline-secondary btn-lg">取消</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let serviceIndex = 0;

        function loadVehicles() {
            const customerId = document.getElementById('customerSelect').value;
            const vehicleSelect = document.getElementById('vehicleSelect');
            
            if (!customerId) {
                vehicleSelect.innerHTML = '<option value="">请先选择客户</option>';
                return;
            }

            vehicleSelect.innerHTML = '<option value="">加载中...</option>';
            window.location.href = 'add.php?customer_id=' + customerId;
        }

        function addServiceItem() {
            serviceIndex++;
            const container = document.getElementById('serviceItemsContainer');
            const html = `
                <div class="service-item" id="service-item-${serviceIndex}">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">项目 #${serviceIndex}</h6>
                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeServiceItem(${serviceIndex})"><i class="bi bi-trash"></i></button>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-2">
                            <input type="text" name="service_names[]" class="form-control" placeholder="项目名称" required>
                        </div>
                        <div class="col-md-2 mb-2">
                            <input type="text" name="service_types[]" class="form-control" placeholder="类型">
                        </div>
                        <div class="col-md-2 mb-2">
                            <input type="number" name="service_hours[]" class="form-control" placeholder="工时" step="0.5" min="0" onchange="calculateServiceAmount(${serviceIndex})">
                        </div>
                        <div class="col-md-2 mb-2">
                            <input type="number" name="service_hour_prices[]" class="form-control" placeholder="工时单价" step="0.01" min="0" value="150" onchange="calculateServiceAmount(${serviceIndex})">
                        </div>
                        <div class="col-md-2 mb-2">
                            <input type="number" name="service_amounts[]" class="form-control service-amount" placeholder="金额" step="0.01" min="0" readonly>
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        }

        function removeServiceItem(index) {
            document.getElementById(`service-item-${index}`).remove();
        }

        function calculateServiceAmount(index) {
            const container = document.getElementById(`service-item-${index}`);
            const hours = parseFloat(container.querySelector('input[name="service_hours[]"]').value) || 0;
            const price = parseFloat(container.querySelector('input[name="service_hour_prices[]"]').value) || 0;
            container.querySelector('input[name="service_amounts[]"]').value = (hours * price).toFixed(2);
        }

        addServiceItem();
    </script>
</body>
</html>
