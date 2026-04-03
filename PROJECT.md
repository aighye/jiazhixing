
# 汽车4S店维修业务管理系统 - 项目概述

## 项目简介

这是一套完整的汽车4S店维修业务管理系统，采用 PHP + MySQL 开发，无需编译，开箱即用。系统涵盖了从客户接待、工单创建、派工维修、配件管理、财务结算到统计报表的完整业务流程。

## 核心特性

- 🚀 **无需编译**：PHP 是解释型语言，直接运行
- 💾 **MySQL 数据库**：稳定可靠，易于维护
- 📦 **全模块覆盖**：完整的4S店业务流程
- 🔐 **多角色权限**：管理员/前台/技师/财务/库管
- 🎨 **Bootstrap 5 UI**：现代化、响应式界面
- 📊 **统计报表**：多维度数据分析
- ⚡ **快速部署**：支持 Windows/Linux，一键安装

## 功能模块清单

### 系统管理模块
- ✅ 用户账号管理（增删改查、角色分配）
- ✅ 角色权限管理
- ✅ 系统操作日志
- ✅ 系统配置管理

### 客户管理模块
- ✅ 客户信息建档
- ✅ 客户车辆档案管理
- ✅ 客户历史记录查询
- ✅ 会员等级与积分管理

### 维修接待模块
- ✅ 快速开单（客户+车辆自动关联）
- ✅ 故障描述与维修类型
- ✅ 服务项目选择
- ✅ 维修工单生成
- ✅ 工单状态跟踪

### 维修派工模块
- ✅ 工单分配（指定技师）
- ✅ 技师接单/开工/完工
- ✅ 维修进度实时更新
- ✅ 维修备注与异常登记

### 配件管理模块
- ✅ 配件基础信息管理
- ✅ 配件入库/出库/退货
- ✅ 库存盘点
- ✅ 库存预警功能
- ✅ 供应商管理

### 维修结算模块
- ✅ 工单费用核算
- ✅ 优惠折扣
- ✅ 会员积分/余额抵扣
- ✅ 多种支付方式
- ✅ 结算单打印

### 质检出厂模块
- ✅ 维修质量检验
- ✅ 不合格返修登记
- ✅ 质检通过出厂确认

### 统计报表模块
- ✅ 营业额报表（日/月/年）
- ✅ 工单数量统计
- ✅ 数据导出Excel

## 技术架构

### 后端
- **语言**：PHP 7.4+
- **数据库**：MySQL 5.7+
- **架构**：轻量级 MVC 架构
- **核心类库**：
  - `Database`：PDO 数据库操作类
  - `Auth`：用户认证与权限检查
  - `Logger`：系统日志记录
  - `Helper`：通用辅助函数
  - `Config`：配置管理

### 前端
- **框架**：Bootstrap 5.3
- **图标**：Bootstrap Icons
- **特性**：响应式设计、移动端适配

### 数据库设计
- 25+ 张数据表
- 完整的业务关系
- 索引优化
- 支持事务

## 快速开始

### 1. 环境准备
确保已安装：
- PHP 7.4+
- MySQL 5.7+
- Apache/Nginx

### 2. 导入数据库
```bash
mysql -u root -p < database/install.sql
```

### 3. 配置数据库
编辑 `core/Database.php`：
```php
private $host = 'localhost';
private $dbname = 'auto_4s_system';
private $username = 'root';
private $password = 'your_password';
```

### 4. 访问系统
- 地址：http://localhost/
- 默认账号：admin / admin123

## 数据库表结构

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| roles | 角色表 |
| permissions | 权限表 |
| customers | 客户表 |
| customer_vehicles | 客户车辆表 |
| work_orders | 维修工单表 |
| work_order_services | 工单服务项目表 |
| work_order_parts | 工单配件表 |
| work_order_logs | 工单进度日志 |
| parts | 配件表 |
| parts_categories | 配件分类表 |
| suppliers | 供应商表 |
| parts_inbound | 配件入库单 |
| parts_outbound | 配件出库单 |
| settlements | 结算单表 |
| payment_records | 支付记录表 |
| inspections | 质检表 |
| system_logs | 系统操作日志 |
| login_logs | 登录日志 |
| system_config | 系统配置表 |

## 安全建议

1. **修改默认密码**：首次登录后立即修改管理员密码
2. **HTTPS**：生产环境建议使用 HTTPS
3. **数据库权限**：使用专用数据库用户，最小权限原则
4. **定期备份**：定期备份数据库
5. **目录权限**：合理设置文件目录权限

## 扩展开发

### 新增页面
```php
<?php
require_once __DIR__ . '/../bootstrap.php';
Auth::check();

$db = Database::getInstance();
// 业务逻辑...
?>
<!-- HTML -->
```

### 数据库操作
```php
$db = Database::getInstance();

// 查询
$users = $db->fetchAll("SELECT * FROM users");

// 插入
$id = $db->insert('users', ['username' => 'test']);

// 更新
$db->update('users', ['name' => 'Test'], 'id = ?', [$id]);

// 删除
$db->delete('users', 'id = ?', [$id]);

// 事务
$db->beginTransaction();
try {
    // 操作...
    $db->commit();
} catch (Exception $e) {
    $db->rollback();
}
```

## 许可证

MIT License

## 致谢

感谢使用本系统！如有问题或建议，欢迎反馈。
