# 🚀 汽车4S店系统 - 腾讯云快速部署命令清单

## 部署前准备

### 在本地执行（PowerShell）
```powershell
# 1. 进入项目目录
cd f:\solo\jiazhixing

# 2. 上传所有文件到服务器
scp -r * root@1.14.43.118:/var/www/html/
```

---

## 在服务器上执行（SSH连接后）

### 第一步：连接服务器
```bash
ssh root@1.14.43.118
```

### 第二步：创建完整目录结构
```bash
cd /var/www/html

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

# 验证目录
ls -la
```

### 第三步：运行自动部署脚本（推荐）
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

---

## 如果手动部署，按以下步骤：

### 1. 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安装Apache
```bash
sudo apt install apache2 -y
sudo systemctl start apache2
sudo systemctl enable apache2
```

### 3. 安装PHP 8.1
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update
sudo apt install php8.1 libapache2-mod-php8.1 php8.1-mysql php8.1-curl php8.1-gd php8.1-mbstring php8.1-xml php8.1-zip -y
```

### 4. 安装MySQL
```bash
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 5. 配置MySQL
```bash
sudo mysql
```

在MySQL提示符下执行：
```sql
CREATE DATABASE auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'auto_4s_user'@'localhost' IDENTIFIED BY 'YourPassword123!';
GRANT ALL PRIVILEGES ON auto_4s_system.* TO 'auto_4s_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. 导入数据库
```bash
mysql -u auto_4s_user -p auto_4s_system < /var/www/html/database/install.sql
```

### 7. 修改数据库配置
```bash
sudo nano /var/www/html/core/Database.php
```

修改为：
```php
private $host = 'localhost';
private $dbname = 'auto_4s_system';
private $username = 'auto_4s_user';
private $password = 'YourPassword123!';
```

### 8. 设置权限
```bash
sudo chown -R www-data:www-data /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;
sudo chmod 777 /var/www/html/uploads
```

### 9. 配置防火墙
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 访问系统

浏览器打开：
```
http://1.14.43.118/
```

默认账号：
- 用户名：`admin`
- 密码：`admin123`

---

## 别忘了！

1. ✅ 在腾讯云安全组开放 80 和 443 端口
2. ✅ 首次登录后立即修改管理员密码
3. ✅ 保存好数据库密码
