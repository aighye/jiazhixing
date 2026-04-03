<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$id = (int)($_GET['id'] ?? 0);
$order = $db->fetchOne("SELECT wo.*, c.name as customer_name, c.phone as customer_phone, cv.plate_number, cv.brand, cv.model, cv.vin FROM work_orders wo LEFT JOIN customers c ON wo.customer_id = c.id LEFT JOIN customer_vehicles cv ON wo.vehicle_id = cv.id WHERE wo.id = ?", [$id]);

if (!$order) {
    Helper::redirect('index.php');
}

$services = $db->fetchAll("SELECT * FROM work_order_services WHERE order_id = ? ORDER BY sort, id", [$id]);
$parts = $db->fetchAll("SELECT * FROM work_order_parts WHERE order_id = ? ORDER BY id", [$id]);
$logs = $db->fetchAll("SELECT * FROM work_order_logs WHERE order_id = ? ORDER BY id DESC", [$id]);
$technicians = $db->fetchAll("SELECT u.id, u.real_name, u.username FROM users u WHERE u.role_id IN (SELECT id FROM roles WHERE role_code = 'technician') AND u.status = 1");

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    $action = $_POST['action'];

    if ($action == 'assign' && $order['status'] == 1) {
        $technicianId = (int)$_POST['technician_id'];
        $db->update('work_orders', ['technician_id' => $technicianId, 'status' => 2], 'id = ?', [$id]);
        $db->insert('work_order_logs', [
            'order_id' => $id,
            'status' => 2,
            'operator_id' => Auth::id(),
            'operator_name' => Auth::user()['real_name'] ?? Auth::user()['username'],
            'content' => '派工给技师'
        ]);
        Logger::log('工单派工', "工单 {$order['order_no']} 派工", 'workorders');
        Helper::redirect('view.php?id=' . $id);
    }

    if ($action == 'start_work' && $order['status'] == 2) {
        $db->insert('work_order_logs', [
            'order_id' => $id,
            'status' => 2,
            'operator_id' => Auth::id(),
            'operator_name' => Auth::user()['real_name'] ?? Auth::user()['username'],
            'content' => '开始维修',
            'remark' => trim($_POST['remark'] ?? '')
        ]);
        Helper::redirect('view.php?id=' . $id);
    }

    if ($action == 'finish_work' && $order['status'] == 2) {
        $db->update('work_orders', ['status' => 3], 'id = ?', [$id]);
        $db->insert('work_order_logs', [
            'order_id' => $id,
            'status' => 3,
            'operator_id' => Auth::id(),
            'operator_name' => Auth::user()['real_name'] ?? Auth::user()['username'],
            'content' => '维修完成，待质检',
            'remark' => trim($_POST['remark'] ?? '')
        ]);
        Logger::log('工单完成', "工单 {$order['order_no']} 维修完成", 'workorders');
        Helper::redirect('view.php?id=' . $id);
    }

    if ($action == 'inspect' && $order['status'] == 3) {
        $result = (int)$_POST['result'];
        if ($result == 1) {
            $db->update('work_orders', ['status' => 4, 'actual_finish_date' => date('Y-m-d H:i:s')], 'id = ?', [$id]);
            $logContent = '质检合格';
        } else {
            $db->update('work_orders', ['status' => 2], 'id = ?', [$id]);
            $logContent = '质检不合格，返回维修';
        }
        $db->insert('inspections', [
            'order_id' => $id,
            'inspector_id' => Auth::id(),
            'result' => $result,
            'check_items' => trim($_POST['check_items'] ?? ''),
            'defect_desc' => trim($_POST['defect_desc'] ?? ''),
            'suggestion' => trim($_POST['suggestion'] ?? ''),
            'remark' => trim($_POST['remark'] ?? '')
        ]);
        $db->insert('work_order_logs', [
            'order_id' => $id,
            'status' => $order['status'],
            'operator_id' => Auth::id(),
            'operator_name' => Auth::user()['real_name'] ?? Auth::user()['username'],
            'content' => $logContent,
            'remark' => trim($_POST['remark'] ?? '')
        ]);
        Logger::log('工单质检', "工单 {$order['order_no']} 质检", 'workorders');
        Helper::redirect('view.php?id=' . $id);
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工单详情 - 汽车4S店维修业务管理系统</title>
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
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
        }
        .timeline-item {
            position: relative;
            padding-left: 30px;
            padding-bottom: 20px;
            border-left: 2px solid #dee2e6;
        }
        .timeline-item:last-child {
            border-left: none;
        }
        .timeline-dot {
            position: absolute;
            left: -8px;
            top: 0;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #6c757d;
            border: 2px solid #fff;
            box-shadow: 0 0 0 2px #6c757d;
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
                            <span class="h3">工单详情</span>
                            <span class="ms-2">
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
                            </span>
                            <?php if ($order['urgent']): ?>
                                <span class="badge bg-danger ms-1">加急</span>
                            <?php endif; ?>
                        </div>
                        <div class="d-flex gap-2">
                            <?php if ($order['status'] == 1): ?>
                                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#assignModal"><i class="bi bi-person-check"></i> 派工</button>
                            <?php endif; ?>
                            <?php if ($order['status'] == 2): ?>
                                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#finishWorkModal"><i class="bi bi-check-circle"></i> 完工</button>
                            <?php endif; ?>
                            <?php if ($order['status'] == 3): ?>
                                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#inspectModal"><i class="bi bi-search"></i> 质检</button>
                            <?php endif; ?>
                            <?php if ($order['status'] == 4): ?>
                                <a href="/settlements/add.php?order_id=<?php echo $order['id']; ?>" class="btn btn-success"><i class="bi bi-cash"></i> 结算</a>
                            <?php endif; ?>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-8">
                            <div class="card mb-4">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">工单信息</h5>
                                </div>
                                <div class="card-body">
                                    <div class="row mb-3">
                                        <div class="col-md-4">
                                            <div class="info-label">工单编号</div>
                                            <div class="info-value fw-bold"><?php echo htmlspecialchars($order['order_no']); ?></div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="info-label">工单类型</div>
                                            <div class="info-value">
                                                <?php $types = ['1' => '保养', '2' => '维修', '3' => '事故', '4' => '索赔']; echo $types[$order['order_type']] ?? '-'; ?>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="info-label">工单来源</div>
                                            <div class="info-value"><?php echo htmlspecialchars($order['source'] ?? '-'); ?></div>
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-4">
                                            <div class="info-label">预估金额</div>
                                            <div class="info-value">¥<?php echo Helper::formatMoney($order['estimated_amount']); ?></div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="info-label">创建时间</div>
                                            <div class="info-value"><?php echo Helper::formatDateTime($order['created_at']); ?></div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="info-label">承诺交车</div>
                                            <div class="info-value"><?php echo $order['promise_date'] ? Helper::formatDateTime($order['promise_date']) : '-'; ?></div>
                                        </div>
                                    </div>
                                    <?php if ($order['fault_desc']): ?>
                                        <div class="mb-3">
                                            <div class="info-label">故障描述</div>
                                            <div class="info-value"><?php echo nl2br(htmlspecialchars($order['fault_desc'])); ?></div>
                                        </div>
                                    <?php endif; ?>
                                    <?php if ($order['service_request']): ?>
                                        <div class="mb-3">
                                            <div class="info-label">服务要求</div>
                                            <div class="info-value"><?php echo nl2br(htmlspecialchars($order['service_request'])); ?></div>
                                        </div>
                                    <?php endif; ?>
                                </div>
                            </div>

                            <div class="card mb-4">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">客户与车辆</h5>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="info-label">客户姓名</div>
                                            <div class="info-value"><a href="/customers/view.php?id=<?php echo $order['customer_id']; ?>"><?php echo htmlspecialchars($order['customer_name'] ?? '-'); ?></a></div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="info-label">联系电话</div>
                                            <div class="info-value"><?php echo htmlspecialchars($order['customer_phone'] ?? '-'); ?></div>
                                        </div>
                                    </div>
                                    <hr>
                                    <div class="row">
                                        <div class="col-md-4">
                                            <div class="info-label">车牌号</div>
                                            <div class="info-value fw-bold"><?php echo htmlspecialchars($order['plate_number'] ?? '-'); ?></div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="info-label">车型</div>
                                            <div class="info-value"><?php echo htmlspecialchars(($order['brand'] ?? '') . ' ' . ($order['model'] ?? '')); ?></div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="info-label">车架号</div>
                                            <div class="info-value"><?php echo htmlspecialchars($order['vin'] ?? '-'); ?></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="card mb-4">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">维修项目</h5>
                                </div>
                                <div class="card-body p-0">
                                    <?php if (count($services) > 0): ?>
                                        <table class="table table-hover mb-0">
                                            <thead class="table-light">
                                                <tr>
                                                    <th>项目名称</th>
                                                    <th>类型</th>
                                                    <th>工时</th>
                                                    <th>工时单价</th>
                                                    <th>金额</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php foreach ($services as $s): ?>
                                                    <tr>
                                                        <td><?php echo htmlspecialchars($s['service_name']); ?></td>
                                                        <td><?php echo htmlspecialchars($s['service_type'] ?? '-'); ?></td>
                                                        <td><?php echo $s['hours']; ?></td>
                                                        <td>¥<?php echo Helper::formatMoney($s['hour_price']); ?></td>
                                                        <td>¥<?php echo Helper::formatMoney($s['amount']); ?></td>
                                                    </tr>
                                                <?php endforeach; ?>
                                            </tbody>
                                        </table>
                                    <?php else: ?>
                                        <div class="text-center py-4 text-muted">暂无维修项目</div>
                                    <?php endif; ?>
                                </div>
                            </div>

                            <div class="card mb-4">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">进度日志</h5>
                                </div>
                                <div class="card-body">
                                    <?php if (count($logs) > 0): ?>
                                        <?php foreach ($logs as $log): ?>
                                            <div class="timeline-item">
                                                <div class="timeline-dot"></div>
                                                <div class="small text-muted mb-1">
                                                    <?php echo htmlspecialchars($log['operator_name'] ?? ''); ?> · <?php echo Helper::formatDateTime($log['created_at']); ?>
                                                </div>
                                                <div class="fw-bold"><?php echo htmlspecialchars($log['content']); ?></div>
                                                <?php if ($log['remark']): ?>
                                                    <div class="text-muted small"><?php echo htmlspecialchars($log['remark']); ?></div>
                                                <?php endif; ?>
                                            </div>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <div class="text-center text-muted">暂无日志</div>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="card mb-4">
                                <div class="card-header bg-white">
                                    <h5 class="mb-0">操作</h5>
                                </div>
                                <div class="card-body">
                                    <div class="d-grid gap-2">
                                        <a href="edit.php?id=<?php echo $order['id']; ?>" class="btn btn-outline-primary"><i class="bi bi-pencil"></i> 编辑工单</a>
                                        <button class="btn btn-outline-secondary"><i class="bi bi-printer"></i> 打印工单</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="modal fade" id="assignModal" tabindex="-1">
                        <div class="modal-dialog">
                            <form method="POST">
                                <input type="hidden" name="action" value="assign">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">派工</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label class="form-label">选择技师</label>
                                            <select name="technician_id" class="form-select" required>
                                                <option value="">请选择</option>
                                                <?php foreach ($technicians as $t): ?>
                                                    <option value="<?php echo $t['id']; ?>"><?php echo htmlspecialchars($t['real_name'] ?: $t['username']); ?></option>
                                                <?php endforeach; ?>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                        <button type="submit" class="btn btn-primary">确认派工</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div class="modal fade" id="finishWorkModal" tabindex="-1">
                        <div class="modal-dialog">
                            <form method="POST">
                                <input type="hidden" name="action" value="finish_work">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">完工上报</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label class="form-label">备注</label>
                                            <textarea name="remark" class="form-control" rows="3"></textarea>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                        <button type="submit" class="btn btn-primary">确认完工</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div class="modal fade" id="inspectModal" tabindex="-1">
                        <div class="modal-dialog">
                            <form method="POST">
                                <input type="hidden" name="action" value="inspect">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">质检</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label class="form-label">质检结果</label>
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="result" value="1" id="result1" checked>
                                                <label class="form-check-label" for="result1">合格</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="result" value="0" id="result0">
                                                <label class="form-check-label" for="result0">不合格，返回维修</label>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">检查项目</label>
                                            <textarea name="check_items" class="form-control" rows="2"></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">缺陷描述</label>
                                            <textarea name="defect_desc" class="form-control" rows="2"></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">备注</label>
                                            <textarea name="remark" class="form-control" rows="2"></textarea>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                        <button type="submit" class="btn btn-primary">确认质检</button>
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
</body>
</html>
