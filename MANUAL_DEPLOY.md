# 手动部署 - 汽车4S店维修系统

## 服务器信息
- IP：1.14.43.118
- 系统：Ubuntu

---

## 📋 完整部署步骤

### 第1步：连接服务器
在本地终端执行：
```bash
ssh root@1.14.43.118
```

---

### 第2步：更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

---

### 第3步：安装Apache
```bash
sudo apt install apache2 -y
sudo systemctl start apache2
sudo systemctl enable apache2
```

检查Apache是否运行：
```bash
sudo systemctl status apache2
```

---

### 第4步：安装PHP 8.1
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

---

### 第5步：安装MySQL
```bash
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
```

---

### 第6步：创建项目目录结构
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

# 查看目录结构
ls -la
```

你应该看到：
```
config/  core/  database/  customers/  workorders/  parts/  settlements/  reports/  system/  uploads/
```

---

### 第7步：上传项目文件（本地终端执行）

打开新的本地终端（PowerShell）：
```powershell
cd f:\solo\jiazhixing
scp -r * root@1.14.43.118:/var/www/html/
```

等待上传完成后，回到服务器终端。

---

### 第8步：配置MySQL数据库

#### 8.1 登录MySQL
```bash
sudo mysql
```

#### 8.2 执行以下SQL语句（复制粘贴）
```sql
CREATE DATABASE auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'auto_4s_user'@'localhost' IDENTIFIED BY 'Auto4s@2024';

GRANT ALL PRIVILEGES ON auto_4s_system.* TO 'auto_4s_user'@'localhost';

FLUSH PRIVILEGES;

EXIT;
```

#### 8.3 导入数据库
```bash
mysql -u auto_4s_user -p auto_4s_system < /var/www/html/database/install.sql
```
输入密码：`Auto4s@2024`

---

### 第9步：修改数据库连接配置

编辑配置文件：
```bash
sudo nano /var/www/html/core/Database.php
```

找到这几行并修改：
```php
private $host = 'localhost';
private $dbname = 'auto_4s_system';
private $username = 'auto_4s_user';
private $password = 'Auto4s@2024';
```

按 `Ctrl+O` 保存，然后按 `Enter`，最后按 `Ctrl+X` 退出。

---

### 第10步：设置文件权限
```bash
sudo chown -R www-data:www-data /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;
sudo chmod 777 /var/www/html/uploads
```

---

### 第11步：配置防火墙
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable
```

---

### 第12步：配置腾讯云安全组（重要！）

登录腾讯云控制台：
1. 进入云服务器实例
2. 点击"安全组"
3. 点击"修改规则"
4. 添加入站规则：
   - 类型：Custom
   - 协议端口：TCP:80
   - 来源：0.0.0.0/0
   - 策略：允许
   
   再添加一条：
   - 类型：Custom
   - 协议端口：TCP:443
   - 来源：0.0.0.0/0
   - 策略：允许

---

## ✅ 部署完成！

### 访问系统
在浏览器中打开：
```
http://1.14.43.118/
```

### 默认登录账号
- 用户名：`admin`
- 密码：`admin123`

---

## ⚠️ 重要提醒

1. **首次登录后立即修改管理员密码！**
2. **保存好数据库密码：`Auto4s@2024`**
3. **确保腾讯云安全组已开放80和443端口**

---

## 🔍 检查清单

- [ ] 能通过SSH连接服务器
- [ ] Apache已安装并运行
- [ ] PHP 8.1已安装
- [ ] MySQL已安装并运行
- [ ] 所有目录已创建
- [ ] 项目文件已上传
- [ ] 数据库已创建
- [ ] 数据库已导入
- [ ] Database.php配置已修改
- [ ] 文件权限已设置
- [ ] 防火墙已配置
- [ ] 腾讯云安全组已配置
- [ ] 能在浏览器访问 http://1.14.43.118/
- [ ] 能使用admin/admin123登录
