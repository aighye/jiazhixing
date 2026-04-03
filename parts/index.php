<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::require();

$db = Database::getInstance();

$page = isset($_GET['page']) ? max(1, (int)$_GET['page']) : 1;
$limit = 15;
$offset = ($page - 1) * $limit;
$keyword = trim($_GET['keyword'] ?? '');
$lowStock = isset($_GET['low_stock']) ? (int)$_GET['low_stock'] : 0;

$where = 'WHERE 1=1';
$params = [];

if ($keyword) {
    $where .= ' AND (part_code LIKE ? OR part_name LIKE ?)';
    $likeKeyword = "%{$keyword}%";
    $params = [$likeKeyword, $likeKeyword];
}
if ($lowStock) {
    $where .= ' AND stock <= min_stock';
}

$total = $db->fetchOne("SELECT COUNT(*) as count FROM parts {$where}", $params)['count'];
$parts = $db->fetchAll("SELECT p.*, c.category_name, s.supplier_name FROM parts p LEFT JOIN parts_categories c ON p.category_id = c.id LEFT JOIN suppliers s ON p.supplier_id = s.id {$where} ORDER BY p.created_at DESC LIMIT {$limit} OFFSET {$offset}", $params);
$pagination = Helper::pagination($total, $page, $limit);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>配件管理 - 汽车4S店维修业务管理系统</title>
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
        .stock-low {
            color: #dc3545;
            font-weight: bold;
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
                    <a class="nav-link active" href="/parts/index.php"><i class="bi bi-box-seam"></i> 配件管理</a>
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
                        <h3>配件管理</h3>
                        <div class="d-flex gap-2">
                            <a href="inbound.php" class="btn btn-outline-primary"><i class="bi bi-box-arrow-in-down"></i> 入库</a>
                            <a href="add.php" class="btn btn-primary"><i class="bi bi-plus-lg"></i> 新增配件</a>
                        </div>
                    </div>

                    <div class="card mb-4">
                        <div class="card-body">
                            <form method="GET" class="row g-3">
                                <div class="col-md-4">
                                    <input type="text" name="keyword" class="form-control" placeholder="搜索配件编码或名称" value="<?php echo htmlspecialchars($keyword); ?>">
                                </div>
                                <div class="col-md-3">
                                    <div class="form-check mt-2">
                                        <input class="form-check-input" type="checkbox" name="low_stock" id="low_stock" value="1" <?php echo $lowStock ? 'checked' : ''; ?>>
                                        <label class="form-check-label" for="low_stock">仅显示低库存</label>
                                    </div>
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
                                        <th>配件编码</th>
                                        <th>配件名称</th>
                                        <th>分类</th>
                                        <th>规格</th>
                                        <th>进价</th>
                                        <th>售价</th>
                                        <th>库存</th>
                                        <th>状态</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (count($parts) > 0): ?>
                                        <?php foreach ($parts as $part): ?>
                                            <tr>
                                                <td><?php echo htmlspecialchars($part['part_code']); ?></td>
                                                <td><?php echo htmlspecialchars($part['part_name']); ?></td>
                                                <td><?php echo htmlspecialchars($part['category_name'] ?? '-'); ?></td>
                                                <td><?php echo htmlspecialchars($part['spec'] ?? '-'); ?></td>
                                                <td>¥<?php echo Helper::formatMoney($part['purchase_price']); ?></td>
                                                <td>¥<?php echo Helper::formatMoney($part['sale_price']); ?></td>
                                                <td class="<?php echo $part['stock'] <= $part['min_stock'] ? 'stock-low' : ''; ?>">
                                                    <?php echo $part['stock']; ?> / <?php echo $part['min_stock']; ?>
                                                </td>
                                                <td>
                                                    <span class="badge <?php echo $part['status'] ? 'bg-success' : 'bg-danger'; ?>">
                                                        <?php echo $part['status'] ? '正常' : '停用'; ?>
                                                    </span>
                                                </td>
                                                <td>
                                                    <a href="view.php?id=<?php echo $part['id']; ?>" class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i></a>
                                                    <a href="edit.php?id=<?php echo $part['id']; ?>" class="btn btn-sm btn-outline-secondary"><i class="bi bi-pencil"></i></a>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="9" class="text-center py-4 text-muted">暂无配件数据</td>
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
                                            <li class="page-item"><a class="page-link" href="?page=<?php echo $page - 1; ?>&keyword=<?php echo urlencode($keyword); ?>&low_stock=<?php echo $lowStock; ?>">上一页</a></li>
                                        <?php endif; ?>
                                        <?php for ($i = max(1, $page - 2); $i <= min($pagination['total_pages'], $page + 2); $i++): ?>
                                            <li class="page-item <?php echo $i == $page ? 'active' : ''; ?>">
                                                <a class="page-link" href="?page=<?php echo $i; ?>&keyword=<?php echo urlencode($keyword); ?>&low_stock=<?php echo $lowStock; ?>"><?php echo $i; ?></a>
                                            </li>
                                        <?php endfor; ?>
                                        <?php if ($pagination['has_next']): ?>
                                            <li class="page-item"><a class="page-link" href="?page=<?php echo $page + 1; ?>&keyword=<?php echo urlencode($keyword); ?>&low_stock=<?php echo $lowStock; ?>">下一页</a></li>
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
