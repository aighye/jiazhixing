# 🔧 Not Found 错误 - 文件缺失问题

## 问题
访问网站时显示：
> "Not Found - The requested URL was not found on this server"

## ✅ 检查和修复步骤

### 第1步：连接服务器
```bash
ssh root@1.14.43.118
```

---

### 第2步：检查 /var/www/html/ 目录内容

```bash
cd /var/www/html
ls -la
```

**应该看到这些文件：**
```
index.php
login.php
dashboard.php
logout.php
bootstrap.php
config/
core/
database/
customers/
workorders/
parts/
settlements/
reports/
system/
...
```

---

### 第3步：如果目录是空的，或者文件缺失

#### 情况A：完全没有文件
**重新上传所有文件！**

在本地 PowerShell 执行：
```powershell
cd f:\solo\jiazhixing
scp -r * root@1.14.43.118:/var/www/html/
```

#### 情况B：只有部分文件
确认本地 `f:\solo\jiazhixing\` 有完整的文件，然后重新上传。

---

### 第4步：检查 index.php 是否存在

```bash
ls -la /var/www/html/index.php
```

**如果不存在，创建一个简单的index.php：**

```bash
sudo nano /var/www/html/index.php
```

复制粘贴：
```php
<?php
require_once __DIR__ . '/bootstrap.php';

header('Location: /login.php');
exit;
?>
```

按 `Ctrl+O` 保存，`Enter` 确认，`Ctrl+X` 退出。

---

### 第5步：检查 bootstrap.php 和 core 目录

```bash
ls -la /var/www/html/bootstrap.php
ls -la /var/www/html/core/
```

**应该看到：**
```
Database.php
Auth.php
Logger.php
Helper.php
Config.php
```

如果这些文件缺失，必须重新上传！

---

### 第6步：检查 Apache DocumentRoot

```bash
sudo cat /etc/apache2/sites-available/000-default.conf | grep DocumentRoot
```

**应该是：**
```
DocumentRoot /var/www/html
```

如果不是，编辑配置：
```bash
sudo nano /etc/apache2/sites-available/000-default.conf
```

找到 DocumentRoot 改为：
```
DocumentRoot /var/www/html
```

保存退出，然后重启：
```bash
sudo systemctl restart apache2
```

---

### 第7步：修复文件权限（无论如何都执行）

```bash
cd /var/www/html
sudo chown -R www-data:www-data /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;
sudo mkdir -p /var/www/html/uploads
sudo chmod 777 /var/www/html/uploads
sudo systemctl restart apache2
```

---

### 第8步：创建测试文件验证 Apache

```bash
echo "<h1>Apache is working!</h1><p>Date: $(date)</p>" | sudo tee /var/www/html/test.html
```

然后访问：
```
http://1.14.43.118/test.html
```

**如果能看到 "Apache is working!"，说明 Apache 正常！**

---

## 🚀 快速修复脚本（一键执行）

```bash
# 1. 进入目录
cd /var/www/html

# 2. 列出内容
echo "=== 当前目录内容 ==="
ls -la

# 3. 如果index.php不存在，创建一个
if [ ! -f index.php ]; then
    echo "创建 index.php..."
    echo '<?php header("Location: login.php"); ?>' | sudo tee index.php
fi

# 4. 如果bootstrap.php不存在，提示重新上传
if [ ! -f bootstrap.php ]; then
    echo ""
    echo "❌ bootstrap.php 缺失！"
    echo "请重新上传所有文件！"
    echo ""
fi

# 5. 修复权限
echo "修复权限..."
sudo chown -R www-data:www-data /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;
sudo mkdir -p /var/www/html/uploads
sudo chmod 777 /var/www/html/uploads 2>/dev/null

# 6. 重启Apache
echo "重启Apache..."
sudo systemctl restart apache2

# 7. 创建测试文件
echo "<h1>测试成功！</h1><p>时间: $(date)</p>" | sudo tee /var/www/html/test.html

echo ""
echo "✅ 完成！"
echo "请访问 http://1.14.43.118/test.html"
echo "如果测试页正常，再访问 http://1.14.43.118/"
```

---

## 📋 检查清单

- [ ] 能通过SSH连接服务器
- [ ] `/var/www/html/` 目录有文件
- [ ] `index.php` 存在
- [ ] `bootstrap.php` 存在
- [ ] `core/` 目录存在且有5个PHP文件
- [ ] `database/` 目录存在且有 `install.sql`
- [ ] Apache DocumentRoot 是 /var/www/html
- [ ] 文件权限正确
- [ ] Apache 已重启
- [ ] 能访问 test.html

---

## ⚠️ 如果文件确实缺失

**必须重新上传所有文件！**

在本地 PowerShell 执行：
```powershell
cd f:\solo\jiazhixing
scp -r * root@1.14.43.118:/var/www/html/
```

确保上传过程中没有错误！
