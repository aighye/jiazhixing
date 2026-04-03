# 🔧 故障排查 - "没有找到站点"

## 问题描述
访问 `http://1.14.43.118/` 时显示：
> "没有找到站点 您的请求在Web服务器中没有找到对应的站点！"

---

## ✅ 排查步骤（按顺序执行）

### 第1步：检查Apache是否运行

在服务器终端执行：
```bash
sudo systemctl status apache2
```

**预期结果：**
```
● apache2.service - The Apache HTTP Server
     Loaded: loaded (/lib/systemd/system/apache2.service; enabled; vendor preset: enabled)
     Active: active (running) since ...
```

**如果不是 running，启动它：**
```bash
sudo systemctl start apache2
sudo systemctl enable apache2
```

---

### 第2步：检查文件是否在正确的位置

```bash
cd /var/www/html
ls -la
```

**应该看到这些文件和目录：**
```
index.php
login.php
dashboard.php
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

**如果目录是空的，重新上传文件：**

在本地 PowerShell 执行：
```powershell
cd f:\solo\jiazhixing
scp -r * root@1.14.43.118:/var/www/html/
```

---

### 第3步：检查index.php是否存在

```bash
ls -la /var/www/html/index.php
```

**应该看到：**
```
-rw-r--r-- 1 www-data www-data xxx Apr  3 10:00 /var/www/html/index.php
```

---

### 第4步：检查Apache配置

```bash
sudo cat /etc/apache2/sites-available/000-default.conf
```

**检查DocumentRoot是否正确：**
```
DocumentRoot /var/www/html
```

**如果不是，编辑它：**
```bash
sudo nano /etc/apache2/sites-available/000-default.conf
```

找到 `DocumentRoot` 这一行，改为：
```
DocumentRoot /var/www/html
```

按 `Ctrl+O` 保存，`Enter` 确认，`Ctrl+X` 退出。

然后重启Apache：
```bash
sudo systemctl restart apache2
```

---

### 第5步：检查目录权限

```bash
ls -la /var/www/html/
```

**所有者应该是 www-data:www-data**

如果不是，修复权限：
```bash
sudo chown -R www-data:www-data /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;
```

---

### 第6步：测试Apache默认页面

先创建一个简单的测试文件：
```bash
echo "<?php phpinfo(); ?>" | sudo tee /var/www/html/test.php
```

然后访问：
```
http://1.14.43.118/test.php
```

**如果能看到PHP信息页面，说明Apache和PHP正常！**

测试完删除：
```bash
sudo rm /var/www/html/test.php
```

---

### 第7步：检查Apache错误日志

```bash
sudo tail -50 /var/log/apache2/error.log
```

看看有什么错误信息。

---

### 第8步：检查是否有其他Web服务

```bash
sudo netstat -tlnp | grep :80
```

**应该只看到 apache2**

如果看到 nginx 或其他，停止它们：
```bash
sudo systemctl stop nginx
sudo systemctl disable nginx
```

然后重启Apache：
```bash
sudo systemctl restart apache2
```

---

## 🚀 快速修复命令（一键执行）

如果不确定问题在哪，一次性执行这些命令：

```bash
# 1. 确保Apache运行
sudo systemctl start apache2
sudo systemctl enable apache2

# 2. 修复权限
sudo chown -R www-data:www-data /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;
sudo chmod 777 /var/www/html/uploads 2>/dev/null || true

# 3. 重启Apache
sudo systemctl restart apache2

# 4. 查看状态
sudo systemctl status apache2

# 5. 列出目录内容
ls -la /var/www/html/
```

执行完后，刷新浏览器再试！

---

## 📋 检查清单

- [ ] Apache 正在运行
- [ ] 文件已上传到 /var/www/html/
- [ ] index.php 存在
- [ ] 所有者是 www-data:www-data
- [ ] 目录权限是 755
- [ ] 文件权限是 644
- [ ] Apache已重启
- [ ] 腾讯云安全组开放了80端口

---

## 🆘 如果还是不行

### 检查腾讯云安全组

1. 登录腾讯云控制台
2. 进入云服务器实例
3. 点击"安全组"
4. 确保有这两条规则：
   - 端口：80，来源：0.0.0.0/0，策略：允许
   - 端口：443，来源：0.0.0.0/0，策略：允许

### 查看Apache访问日志

```bash
sudo tail -f /var/log/apache2/access.log
```

然后刷新浏览器，看有没有访问记录。

---

## ✅ 一切正常后

确认访问 `http://1.14.43.118/` 能看到登录页面后，继续：

1. 导入数据库（见 `IMPORT_DATABASE.md`）
2. 修改 `core/Database.php` 配置
3. 设置权限
4. 登录系统（admin / admin123）
