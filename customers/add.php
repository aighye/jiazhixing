<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = [
        'customer_no' => 'CU' . date('YmdHis') . mt_rand(1000, 9999),
        'name' => trim($_POST['name']),
        'phone' => trim($_POST['phone']),
        'email' => trim($_POST['email']),
        'id_card' => trim($_POST['id_card']),
        'address' => trim($_POST['address']),
        'member_level' => (int)$_POST['member_level'],
        'source' => trim($_POST['source']),
        'remark' => trim($_POST['remark']),
        'status' => isset($_POST['status']) ? 1 : 0,
        'created_by' => Auth::id()
    ];

    if (empty($data['name']) || empty($data['phone'])) {
        $error = '请填写客户姓名和手机号';
    } else {
        $db->insert('customers', $data);
        Logger::log('新增客户', "创建客户: {$data['name']}", 'customers');
        Helper::redirect('index.php');
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新增客户 - 汽车4S店维修业务管理系统</title>
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
                        <h3>新增客户</h3>
                        <a href="index.php" class="btn btn-outline-secondary"><i class="bi bi-arrow-left"></i> 返回列表</a>
                    </div>

                    <div class="card">
                        <div class="card-body">
                            <?php if (isset($error)): ?>
                                <div class="alert alert-danger"><?php echo htmlspecialchars($error); ?></div>
                            <?php endif; ?>

                            <form method="POST">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">客户姓名 <span class="text-danger">*</span></label>
                                        <input type="text" name="name" class="form-control" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">手机号 <span class="text-danger">*</span></label>
                                        <input type="text" name="phone" class="form-control" required>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">邮箱</label>
                                        <input type="email" name="email" class="form-control">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">身份证号</label>
                                        <input type="text" name="id_card" class="form-control">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">地址</label>
                                    <textarea name="address" class="form-control" rows="2"></textarea>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">会员等级</label>
                                        <select name="member_level" class="form-select">
                                            <option value="1">普通会员</option>
                                            <option value="2">银卡会员</option>
                                            <option value="3">金卡会员</option>
                                            <option value="4">钻石会员</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">客户来源</label>
                                        <select name="source" class="form-select">
                                            <option value="">请选择</option>
                                            <option value="到店">到店</option>
                                            <option value="电话">电话</option>
                                            <option value="网络">网络</option>
                                            <option value="转介绍">转介绍</option>
                                            <option value="其他">其他</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">备注</label>
                                    <textarea name="remark" class="form-control" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="status" id="status" checked>
                                        <label class="form-check-label" for="status">启用状态</label>
                                    </div>
                                </div>
                                <div class="d-flex gap-2">
                                    <button type="submit" class="btn btn-primary"><i class="bi bi-save"></i> 保存</button>
                                    <a href="index.php" class="btn btn-outline-secondary">取消</a>
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
