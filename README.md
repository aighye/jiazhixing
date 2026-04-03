
# 汽车4S店维修业务管理系统

一套完整的汽车4S店维修业务管理系统，采用 PHP + MySQL 开发，无需编译，开箱即用。

## 系统特点

- 🚀 **无需编译**：PHP 解释型语言，直接运行
- 💾 **MySQL 数据库**：稳定、易维护
- 📦 **全模块覆盖**：客户接待→派工→维修→结算→出库→报表
- 🔐 **权限分级**：管理员/前台/技师/财务/库管多角色
- 🎨 **Bootstrap 5**：现代化UI设计

## 功能模块

### 1. 系统管理
- 用户账号管理
- 角色权限管理
- 系统日志
- 系统配置

### 2. 客户管理
- 客户信息建档
- 客户车辆档案
- 历史维修记录
- 会员积分管理

### 3. 维修接待
- 快速开单
- 故障描述
- 服务项目选择
- 工单生成与打印

### 4. 维修派工
- 工单分配
- 技师接单/开工/完工
- 进度实时更新

### 5. 配件管理
- 配件基础信息
- 入库/出库/盘点
- 库存预警

### 6. 维修结算
- 费用核算
- 优惠折扣
- 多种支付方式

### 7. 质检出厂
- 质量检验
- 返修登记
- 出厂确认

### 8. 统计报表
- 营业额报表
- 技师业绩统计
- 配件销售统计
- 数据导出Excel

## 安装部署

### 环境要求
- PHP 7.4 或更高版本
- MySQL 5.7 或更高版本
- Apache 或 Nginx

### 安装步骤

1. **上传文件**
   将所有文件上传到服务器目录

2. **导入数据库**
   ```bash
   mysql -u root -p < database/install.sql
   ```

3. **配置数据库连接**
   编辑 `core/Database.php`，修改数据库配置：
   ```php
   private $host = 'localhost';
   private $dbname = 'auto_4s_system';
   private $username = 'root';
   private $password = 'your_password';
   ```

4. **设置目录权限**
   ```bash
   chmod -R 755 /path/to/project
   ```

5. **访问系统**
   浏览器访问：`http://your-domain.com/`

### 默认账号
- 用户名：`admin`
- 密码：`admin123`

## 目录结构

```
auto_4s_system/
├── bootstrap.php          # 引导文件
├── index.php              # 首页入口
├── login.php              # 登录页
├── logout.php             # 退出登录
├── dashboard.php          # 仪表盘
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
├── customers/             # 客户管理模块
├── workorders/            # 工单管理模块
├── parts/                 # 配件管理模块
├── settlements/           # 结算管理模块
├── reports/               # 报表模块
└── system/                # 系统管理模块
```

## 技术栈

- **后端**：PHP 7.4+
- **数据库**：MySQL 5.7+
- **前端**：Bootstrap 5.3 + Bootstrap Icons
- **架构**：MVC 轻量级架构

## 开发说明

### 新增页面
1. 在对应模块目录下创建 PHP 文件
2. 引入 `bootstrap.php`
3. 调用 `Auth::check()` 验证登录
4. 使用 `Database` 类操作数据库

### 数据库操作
```php
$db = Database::getInstance();

// 查询
$users = $db->fetchAll("SELECT * FROM users");

// 插入
$id = $db->insert('users', ['username' => 'test', ...]);

// 更新
$db->update('users', ['real_name' => 'Test'], 'id = ?', [$id]);

// 删除
$db->delete('users', 'id = ?', [$id]);
```

## 许可证

MIT License

## 支持

如有问题，请联系技术支持。

