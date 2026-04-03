# 汽车4S店维修业务管理系统 - 快速安装指南

## 系统要求

- PHP 7.4 或更高版本
- MySQL 5.7 或更高版本
- Apache/Nginx Web服务器
- 浏览器：Chrome、Firefox、Edge 等现代浏览器

## 安装步骤

### 第一步：上传文件

将所有文件上传到您的 Web 服务器目录，例如：
- `/var/www/html/auto_4s/` (Linux)
- `C:\xampp\htdocs\auto_4s\` (Windows)

### 第二步：创建数据库

1. 登录 MySQL：
   ```bash
   mysql -u root -p
   ```

2. 创建数据库：
   ```sql
   CREATE DATABASE auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. 导入数据：
   ```bash
   mysql -u root -p auto_4s_system < database/install.sql
   ```

或者使用 phpMyAdmin：
- 打开 phpMyAdmin
- 创建数据库 `auto_4s_system`
- 导入 `database/install.sql` 文件

### 第三步：配置数据库连接

编辑文件 `core/Database.php`，修改以下配置：

```php
private $host = 'localhost';        // 数据库主机
private $dbname = 'auto_4s_system'; // 数据库名
private $username = 'root';         // 数据库用户名
private $password = '';             // 数据库密码
```

### 第四步：设置目录权限（Linux）

```bash
chmod -R 755 /path/to/auto_4s
```

如果有上传目录，确保可写：
```bash
chmod -R 777 /path/to/auto_4s/uploads
```

### 第五步：访问系统

在浏览器中访问：
- `http://localhost/auto_4s/` (本地)
- `http://your-domain.com/` (服务器)

### 默认登录账号

- 用户名：`admin`
- 密码：`admin123`

⚠️ **重要：首次登录后请立即修改密码！**

## 模块说明

### 1. 仪表盘
- 今日工单统计
- 待处理工单
- 今日营业额
- 库存预警
- 最新工单列表

### 2. 维修工单
- 新建工单
- 工单列表
- 工单详情
- 派工管理
- 维修进度跟踪
- 质检管理

### 3. 客户管理
- 客户档案
- 车辆档案
- 历史工单查询
- 会员管理

### 4. 配件管理
- 配件档案
- 入库管理
- 出库管理
- 库存盘点
- 库存预警

### 5. 财务结算
- 工单结算
- 结算记录
- 优惠管理
- 多种支付方式

### 6. 统计报表
- 营业统计
- 工单统计
- 导出Excel

### 7. 系统设置
- 用户管理
- 角色管理
- 操作日志
- 系统配置

## 常见问题

### 1. 提示数据库连接失败
检查 `core/Database.php` 中的数据库配置是否正确。

### 2. 页面显示空白
查看 PHP 错误日志，通常在：
- Linux: `/var/log/apache2/error.log`
- Windows: `C:\xampp\php\logs\php_error_log`

### 3. 无法上传文件
确保上传目录有写入权限。

### 4. 忘记管理员密码
执行以下 SQL 重置密码为 `admin123`：

```sql
UPDATE users SET password = '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi' WHERE username = 'admin';
```

## 技术支持

如有问题，请检查：
1. PHP 版本 >= 7.4
2. MySQL 版本 >= 5.7
3. PDO 扩展已启用
4. 错误日志中的详细信息

## 目录结构

```
auto_4s_system/
├── index.php              # 首页
├── login.php              # 登录页
├── logout.php             # 退出
├── dashboard.php          # 仪表盘
├── bootstrap.php          # 引导文件
├── README.md              # 说明文档
├── INSTALL.md             # 安装指南
├── config/
│   └── app.php           # 应用配置
├── core/
│   ├── Database.php      # 数据库类
│   ├── Auth.php          # 认证类
│   ├── Logger.php        # 日志类
│   ├── Helper.php        # 辅助函数
│   └── Config.php        # 配置类
├── database/
│   └── install.sql       # 数据库安装脚本
├── customers/             # 客户管理
├── workorders/            # 工单管理
├── parts/                 # 配件管理
├── settlements/           # 结算管理
├── reports/               # 报表管理
└── system/                # 系统管理
```
