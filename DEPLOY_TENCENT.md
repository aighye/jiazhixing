# 腾讯云Ubuntu服务器部署指南

## 服务器信息
- 操作系统：Ubuntu
- IP地址：1.14.43.118

## 一、连接服务器

### 1.1 使用SSH连接
在本地终端（Windows使用PowerShell或CMD，Mac/Linux使用终端）执行：

```bash
ssh root@1.14.43.118
```

输入密码后即可登录服务器。

---

## 二、安装必要软件

### 2.1 更新系统包
```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2 安装Apache Web服务器
```bash
sudo apt install apache2 -y
```

启动Apache并设置开机自启：
```bash
sudo systemctl start apache2
sudo systemctl enable apache2
```

检查Apache状态：
```bash
sudo systemctl status apache2
```

### 2.3 安装PHP 8.1（推荐版本）
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update
sudo apt install php8.1 libapache2-mod-php8.1 php8.1-mysql php8.1-curl php8.1-gd php8.1-mbstring php8.1-xml php8.1-zip -y
```

验证PHP安装：
```bash
php -v
```

### 2.4 安装MySQL 8.0
```bash
sudo apt install mysql-server -y
```

启动MySQL并设置开机自启：
```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

检查MySQL状态：
```bash
sudo systemctl status mysql
```

---

## 三、配置MySQL

### 3.1 安全配置MySQL
```bash
sudo mysql_secure_installation
```

按提示操作：
- 设置root密码（请记住此密码）
- 移除匿名用户：Y
- 禁止root远程登录：Y
- 移除测试数据库：Y
- 重新加载权限表：Y

### 3.2 创建数据库和用户
登录MySQL：
```bash
sudo mysql -u root -p
```

输入刚才设置的root密码，然后执行以下SQL：

```sql
-- 创建数据库
CREATE DATABASE auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户（请修改密码）
CREATE USER 'auto_4s_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';

-- 授权
GRANT ALL PRIVILEGES ON auto_4s_system.* TO 'auto_4s_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

---

## 四、创建项目目录结构

### 4.1 在服务器上创建所有必要目录

登录服务器后，先创建完整的目录结构：

```bash
# 进入Web根目录
cd /var/www/html

# 创建所有必要的目录
mkdir -p config
mkdir -p core
mkdir -p database
mkdir -p customers/vehicles
mkdir -p workorders
mkdir -p parts
mkdir -p settlements
mkdir -p reports
mkdir -p system
mkdir -p uploads

# 验证目录结构
ls -la
```

你应该看到以下目录：
- config/
- core/
- database/
- customers/
- customers/vehicles/
- workorders/
- parts/
- settlements/
- reports/
- system/
- uploads/

---

## 五、上传项目文件

### 5.1 使用SCP上传（本地终端执行）
在本地终端，进入项目所在目录：

```bash
# Windows PowerShell
cd f:\solo\jiazhixing

# 或者Mac/Linux
cd /path/to/jiazhixing
```

上传到服务器：
```bash
scp -r * root@1.14.43.118:/var/www/html/
```

或者，如果您使用Git，可以在服务器上克隆：
```bash
cd /var/www/html
git clone <your-repo-url> .
```

### 5.2 设置目录权限
```bash
# 设置所有者为www-data
sudo chown -R www-data:www-data /var/www/html

# 设置目录权限
sudo find /var/www/html -type d -exec chmod 755 {} \;

# 设置文件权限
sudo find /var/www/html -type f -exec chmod 644 {} \;

# 设置uploads目录权限
sudo chmod 777 /var/www/html/uploads
```

---

## 六、导入数据库

### 6.1 上传SQL文件
确保 `database/install.sql` 文件已上传到服务器。

### 6.2 导入数据
```bash
mysql -u auto_4s_user -p auto_4s_system < /var/www/html/database/install.sql
```

输入数据库用户密码。

---

## 七、配置项目

### 7.1 修改数据库连接配置
编辑 `core/Database.php`：

```bash
sudo nano /var/www/html/core/Database.php
```

修改以下内容：

```php
private $host = 'localhost';
private $dbname = 'auto_4s_system';
private $username = 'auto_4s_user';
private $password = 'YourStrongPassword123!';  // 修改为您设置的密码
```

按 `Ctrl+O` 保存，`Ctrl+X` 退出。

### 7.2 配置Apache

启用mod_rewrite（如果需要）：
```bash
sudo a2enmod rewrite
sudo systemctl restart apache2
```

---

## 八、配置防火墙

### 8.1 开放HTTP和HTTPS端口
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

检查防火墙状态：
```bash
sudo ufw status
```

### 8.2 腾讯云安全组
在腾讯云控制台：
1. 进入云服务器实例
2. 点击"安全组"
3. 添加入站规则：
   - 端口：80
   - 来源：0.0.0.0/0
   - 端口：443
   - 来源：0.0.0.0/0

---

## 九、访问系统

在浏览器中访问：
```
http://1.14.43.118/
```

默认登录账号：
- 用户名：`admin`
- 密码：`admin123`

⚠️ **重要：首次登录后请立即修改密码！**

---

## 十、配置SSL证书（推荐，HTTPS）

### 10.1 安装Certbot
```bash
sudo apt install certbot python3-certbot-apache -y
```

### 10.2 获取证书
```bash
sudo certbot --apache -d your-domain.com
```

按提示操作，Certbot会自动配置Apache。

---

## 十一、日常维护

### 11.1 查看Apache日志
```bash
# 访问日志
sudo tail -f /var/log/apache2/access.log

# 错误日志
sudo tail -f /var/log/apache2/error.log
```

### 11.2 备份数据库
```bash
mysqldump -u auto_4s_user -p auto_4s_system > backup_$(date +%Y%m%d).sql
```

### 11.3 重启服务
```bash
# 重启Apache
sudo systemctl restart apache2

# 重启MySQL
sudo systemctl restart mysql
```

---

## 常见问题

### Q1: 访问403 Forbidden
检查文件权限和所有者是否正确：
```bash
sudo chown -R www-data:www-data /var/www/html
```

### Q2: 数据库连接失败
检查 `core/Database.php` 配置是否正确，确认MySQL服务是否运行。

### Q3: 上传文件失败
确保uploads目录存在且权限为777。

---

## 安全建议

1. ✅ 修改默认管理员密码
2. ✅ 使用强密码
3. ✅ 定期更新系统和软件
4. ✅ 配置HTTPS
5. ✅ 定期备份数据库
6. ✅ 限制SSH访问IP
7. ✅ 禁用root远程登录（使用普通用户+sudo）
