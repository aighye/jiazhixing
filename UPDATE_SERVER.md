# 🚀 服务器更新指南

## 问题已修复！

我已经修复了以下问题：

1. ✅ **Auth 类** - 添加了 `Auth::require()` 方法，用于需要登录时自动重定向
2. ✅ **所有页面** - 将 `Auth::check()` 改为 `Auth::require()`（除了 index.php 和 login.php）
3. ✅ **Database::update()** - 修复了参数问题
4. ✅ **数据库连接** - 使用 127.0.0.1 代替 localhost

---

## 📋 在服务器上执行更新（2步）

### 第1步：上传所有修改的文件到服务器

在本地 PowerShell 执行：

```powershell
cd f:\solo\jiazhixing

# 上传核心文件
scp core/Auth.php root@1.14.43.118:/var/www/html/core/
scp core/Database.php root@1.14.43.118:/var/www/html/core/

# 上传所有修改的页面
scp dashboard.php root@1.14.43.118:/var/www/html/
scp logout.php root@1.14.43.118:/var/www/html/

# 上传customers模块
scp customers/index.php root@1.14.43.118:/var/www/html/customers/
scp customers/add.php root@1.14.43.118:/var/www/html/customers/
scp customers/edit.php root@1.14.43.118:/var/www/html/customers/
scp customers/view.php root@1.14.43.118:/var/www/html/customers/
scp customers/vehicles/add.php root@1.14.43.118:/var/www/html/customers/vehicles/
scp customers/vehicles/edit.php root@1.14.43.118:/var/www/html/customers/vehicles/

# 上传workorders模块
scp workorders/index.php root@1.14.43.118:/var/www/html/workorders/
scp workorders/add.php root@1.14.43.118:/var/www/html/workorders/
scp workorders/view.php root@1.14.43.118:/var/www/html/workorders/

# 上传parts模块
scp parts/index.php root@1.14.43.118:/var/www/html/parts/

# 上传settlements模块
scp settlements/index.php root@1.14.43.118:/var/www/html/settlements/
scp settlements/add.php root@1.14.43.118:/var/www/html/settlements/

# 上传reports模块
scp reports/index.php root@1.14.43.118:/var/www/html/reports/

# 上传system模块
scp system/users.php root@1.14.43.118:/var/www/html/system/
scp system/users_save.php root@1.14.43.118:/var/www/html/system/
```

---

### 第2步：在服务器上修复权限并重启

SSH连接服务器后：

```bash
cd /var/www/html
sudo chown -R www:www /var/www/html
sudo find /var/www/html -type d -exec chmod 755 {} \;
sudo find /var/www/html -type f -exec chmod 644 {} \;
sudo mkdir -p /var/www/html/uploads
sudo chmod 777 /var/www/html/uploads
sudo systemctl restart apache2
```

---

## ✅ 完成！

现在访问：
```
http://1.14.43.118/
```

所有功能应该都正常了！
