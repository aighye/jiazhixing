<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$orderId = (int)($_GET['order_id'] ?? 0);
$order = $db->fetchOne("SELECT wo.*, c.name as customer_name, c.member_points, c.balance, cv.plate_number FROM work_orders wo LEFT JOIN customers c ON wo.customer_id = c.id LEFT JOIN customer_vehicles cv ON wo.vehicle_id = cv.id WHERE wo.id = ?", [$orderId]);

if (!$order || $order['status'] != 4) {
    Helper::redirect('/workorders/index.php');
}

$services = $db->fetchAll("SELECT * FROM work_order_services WHERE order_id = ?", [$orderId]);
$parts = $db->fetchAll("SELECT * FROM work_order_parts WHERE order_id = ?", [$orderId]);

$servicesTotal = array_sum(array_column($services, 'amount'));
$partsTotal = array_sum(array_column($parts, 'amount'));
$totalAmount = $servicesTotal + $partsTotal;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $db->beginTransaction();
    try {
        $discountAmount = (float)$_POST['discount_amount'];
        $pointsDeduct = (float)$_POST['points_deduct'];
        $balanceDeduct = (float)$_POST['balance_deduct'];
        $payableAmount = max(0, $totalAmount - $discountAmount - $pointsDeduct - $balanceDeduct);
        $paidAmount = (float)$_POST['paid_amount'];

        $settlementId = $db->insert('settlements', [
            'settle_no' => Helper::generateOrderNo('ST'),
            'order_id' => $orderId,
            'total_amount' => $totalAmount,
            'discount_amount' => $discountAmount,
            'points_deduct' => $pointsDeduct,
            'balance_deduct' => $balanceDeduct,
            'payable_amount' => $payableAmount,
            'paid_amount' => $paidAmount,
            'payment_method' => $_POST['payment_method'],
            'invoice_title' => trim($_POST['invoice_title']),
            'remark' => trim($_POST['remark']),
            'cashier_id' => Auth::id(),
            'settle_time' => date('Y-m-d H:i:s')
        ]);

        $db->insert('payment_records', [
            'settlement_id' => $settlementId,
            'payment_method' => $_POST['payment_method'],
            'amount' => $paidAmount,
            'transaction_no' => trim($_POST['transaction_no']),
            'remark' => trim($_POST['remark'])
        ]);

        if ($pointsDeduct > 0) {
            $db->update('customers', ['member_points' => $db->fetchOne("SELECT member_points FROM customers WHERE id = ?", [$order['customer_id']])['member_points'] - $pointsDeduct], 'id = ?', [$order['customer_id']]);
        }
        if ($balanceDeduct > 0) {
            $db->update('customers', ['balance' => $db->fetchOne("SELECT balance FROM customers WHERE id = ?", [$order['customer_id']])['balance'] - $balanceDeduct], 'id = ?', [$order['customer_id']]);
        }

        $db->update('work_orders', ['status' => 5, 'final_amount' => $paidAmount, 'settle_date' => date('Y-m-d H:i:s')], 'id = ?', [$orderId]);

        $db->insert('work_order_logs', [
            'order_id' => $orderId,
            'status' => 5,
            'operator_id' => Auth::id(),
            'operator_name' => Auth::user()['real_name'] ?? Auth::user()['username'],
            'content' => '结算完成'
        ]);

        $db->commit();
        Logger::log('工单结算', "工单 {$order['order_no']} 结算完成", 'settlements');
        Helper::redirect('view.php?id=' . $settlementId);
    } catch (Exception $e) {
        $db->rollback();
        $error = '结算失败: ' . $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工单结算 - 汽车4S店维修业务管理系统</title>
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
        .amount-row {
            font-size: 18px;
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
                            <a href="/logout.php" class="btn btn-outline-danger"><i class="bi bi-box-arrow-left"></i> 退出</a>
                        </div>
                    </div>
                </nav>

                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <a href="/workorders/view.php?id=<?php echo $orderId; ?>" class="btn btn-outline-secondary btn-sm me-2"><i class="bi bi-arrow-left"></i> 返回</a>
                            <span class="h3">工单结算</span>
                        </div>
                    </div>

                    <?php if (isset($error)): ?>
                        <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
                    <?php endif; ?>

                    <form method="POST" id="settlementForm">
                        <div class="row">
                            <div class="col-md-7">
                                <div class="card mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="mb-0">工单与客户信息</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <div class="text-muted small">工单编号</div>
                                                <div class="fw-bold"><?php echo htmlspecialchars($order['order_no']); ?></div>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <div class="text-muted small">车牌</div>
                                                <div class="fw-bold"><?php echo htmlspecialchars($order['plate_number'] ?? '-'); ?></div>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <div class="text-muted small">客户姓名</div>
                                                <div><?php echo htmlspecialchars($order['customer_name'] ?? '-'); ?></div>
                                            </div>
                                            <div class="col-md-3 mb-3">
                                                <div class="text-muted small">会员积分</div>
                                                <div class="text-primary"><?php echo number_format($order['member_points']); ?></div>
                                            </div>
                                            <div class="col-md-3 mb-3">
                                                <div class="text-muted small">账户余额</div>
                                                <div class="text-success">¥<?php echo Helper::formatMoney($order['balance']); ?></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="card mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="mb-0">维修项目</h5>
                                    </div>
                                    <div class="card-body p-0">
                                        <table class="table table-hover mb-0">
                                            <thead class="table-light">
                                                <tr>
                                                    <th>项目名称</th>
                                                    <th>工时</th>
                                                    <th>单价</th>
                                                    <th>金额</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php foreach ($services as $s): ?>
                                                    <tr>
                                                        <td><?php echo htmlspecialchars($s['service_name']); ?></td>
                                                        <td><?php echo $s['hours']; ?></td>
                                                        <td>¥<?php echo Helper::formatMoney($s['hour_price']); ?></td>
                                                        <td>¥<?php echo Helper::formatMoney($s['amount']); ?></td>
                                                    </tr>
                                                <?php endforeach; ?>
                                            </tbody>
                                            <tfoot class="table-light">
                                                <tr>
                                                    <th colspan="3" class="text-end">小计</th>
                                                    <th>¥<?php echo Helper::formatMoney($servicesTotal); ?></th>
                                                </tr>
                                            </tfoot>
                                        </table>
                                    </div>
                                </div>

                                <?php if (count($parts) > 0): ?>
                                    <div class="card mb-4">
                                        <div class="card-header bg-white">
                                            <h5 class="mb-0">配件清单</h5>
                                        </div>
                                        <div class="card-body p-0">
                                            <table class="table table-hover mb-0">
                                                <thead class="table-light">
                                                    <tr>
                                                        <th>配件名称</th>
                                                        <th>数量</th>
                                                        <th>单价</th>
                                                        <th>金额</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <?php foreach ($parts as $p): ?>
                                                        <tr>
                                                            <td><?php echo htmlspecialchars($p['part_name']); ?></td>
                                                            <td><?php echo $p['quantity']; ?></td>
                                                            <td>¥<?php echo Helper::formatMoney($p['price']); ?></td>
                                                            <td>¥<?php echo Helper::formatMoney($p['amount']); ?></td>
                                                        </tr>
                                                    <?php endforeach; ?>
                                                </tbody>
                                                <tfoot class="table-light">
                                                    <tr>
                                                        <th colspan="3" class="text-end">小计</th>
                                                        <th>¥<?php echo Helper::formatMoney($partsTotal); ?></th>
                                                    </tr>
                                                </tfoot>
                                            </table>
                                        </div>
                                    </div>
                                <?php endif; ?>
                            </div>

                            <div class="col-md-5">
                                <div class="card mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="mb-0">费用计算</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between mb-3 amount-row">
                                            <span>总金额</span>
                                            <span id="totalAmount" class="fw-bold">¥<?php echo Helper::formatMoney($totalAmount); ?></span>
                                        </div>
                                        <hr>
                                        <div class="mb-3">
                                            <label class="form-label">优惠金额</label>
                                            <input type="number" name="discount_amount" id="discountAmount" class="form-control" step="0.01" value="0" onchange="calculate()">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">积分抵扣</label>
                                            <input type="number" name="points_deduct" id="pointsDeduct" class="form-control" step="0.01" value="0" max="<?php echo $order['member_points']; ?>" onchange="calculate()">
                                            <div class="form-text">可用积分: <?php echo number_format($order['member_points']); ?></div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">余额抵扣</label>
                                            <input type="number" name="balance_deduct" id="balanceDeduct" class="form-control" step="0.01" value="0" max="<?php echo $order['balance']; ?>" onchange="calculate()">
                                            <div class="form-text">可用余额: ¥<?php echo Helper::formatMoney($order['balance']); ?></div>
                                        </div>
                                        <hr>
                                        <div class="d-flex justify-content-between mb-3 amount-row text-success">
                                            <span>应付金额</span>
                                            <span id="payableAmount" class="fw-bold">¥<?php echo Helper::formatMoney($totalAmount); ?></span>
                                        </div>
                                    </div>
                                </div>

                                <div class="card mb-4">
                                    <div class="card-header bg-white">
                                        <h5 class="mb-0">支付信息</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="mb-3">
                                            <label class="form-label">支付方式 <span class="text-danger">*</span></label>
                                            <select name="payment_method" class="form-select" required>
                                                <option value="">请选择</option>
                                                <option value="现金">现金</option>
                                                <option value="微信支付">微信支付</option>
                                                <option value="支付宝">支付宝</option>
                                                <option value="刷卡">刷卡</option>
                                                <option value="挂账">挂账</option>
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">实付金额 <span class="text-danger">*</span></label>
                                            <input type="number" name="paid_amount" id="paidAmount" class="form-control" step="0.01" required onchange="calculate()">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">交易流水号</label>
                                            <input type="text" name="transaction_no" class="form-control">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">发票抬头</label>
                                            <input type="text" name="invoice_title" class="form-control">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">备注</label>
                                            <textarea name="remark" class="form-control" rows="2"></textarea>
                                        </div>
                                    </div>
                                </div>

                                <div class="d-grid gap-2">
                                    <button type="submit" class="btn btn-success btn-lg"><i class="bi bi-check-circle"></i> 确认结算</button>
                                    <a href="/workorders/view.php?id=<?php echo $orderId; ?>" class="btn btn-outline-secondary">取消</a>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const totalAmount = <?php echo $totalAmount; ?>;

        function calculate() {
            const discount = parseFloat(document.getElementById('discountAmount').value) || 0;
            const points = parseFloat(document.getElementById('pointsDeduct').value) || 0;
            const balance = parseFloat(document.getElementById('balanceDeduct').value) || 0;
            const payable = Math.max(0, totalAmount - discount - points - balance);

            document.getElementById('payableAmount').textContent = '¥' + payable.toFixed(2);
            document.getElementById('paidAmount').value = payable.toFixed(2);
        }
    </script>
</body>
</html>
