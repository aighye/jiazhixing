# 🔧 PHP未解析 - 显示PHP源代码问题

## 问题描述
访问网站时，看到的是PHP源代码而不是网页内容：
```php
<?php
require_once __DIR__ . '/bootstrap.php';
...
```

## ✅ 原因分析
PHP模块没有被Apache正确加载或启用！

---

## 🛠️ 修复步骤

### 第1步：连接服务器
```bash
ssh root@1.14.43.118
```

---

### 第2步：检查PHP是否已安装
```bash
php -v
```

**应该看到PHP版本信息，例如：**
```
PHP 8.1.x (cli) (built: ...)
```

**如果没有，安装PHP：**
```bash
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update
sudo apt install php8.1 libapache2-mod-php8.1 php8.1-mysql php8.1-curl php8.1-gd php8.1-mbstring php8.1-xml php8.1-zip -y
```

---

### 第3步：启用PHP模块（关键！）
```bash
sudo a2enmod php8.1
```

**如果上面命令不行，尝试：**
```bash
sudo a2enmod php
```

---

### 第4步：检查Apache的PHP配置
```bash
ls -la /etc/apache2/mods-enabled/ | grep php
```

**应该看到：**
```
php8.1.conf -> ../mods-available/php8.1.conf
php8.1.load -> ../mods-available/php8.1.load
```

**如果没有，启用它们：**
```bash
sudo a2enconf php8.1
sudo a2enmod php8.1
```

---

### 第5步：重启Apache
```bash
sudo systemctl restart apache2
```

---

### 第6步：验证PHP是否工作

创建一个测试文件：
```bash
echo "<?php phpinfo(); ?>" | sudo tee /var/www/html/test.php
```

然后在浏览器访问：
```
http://1.14.43.118/test.php
```

**如果能看到PHP信息页面，说明PHP正常工作了！**

测试完删除测试文件：
```bash
sudo rm /var/www/html/test.php
```

---

### 第7步：再次访问系统
```
http://1.14.43.118/
```

现在应该能看到登录页面了！

---

## 🚀 一键修复命令（直接复制执行）

```bash
# 1. 确保PHP已安装
sudo apt update
sudo apt install php8.1 libapache2-mod-php8.1 php8.1-mysql -y

# 2. 启用PHP模块
sudo a2enmod php8.1
sudo a2enconf php8.1

# 3. 重启Apache
sudo systemctl restart apache2

# 4. 检查状态
sudo systemctl status apache2

# 5. 验证模块
ls -la /etc/apache2/mods-enabled/ | grep php
```

执行完后刷新浏览器！

---

## 🔍 如果还是不行

### 检查Apache配置
```bash
sudo cat /etc/apache2/mods-available/php8.1.conf
```

### 检查目录索引
```bash
sudo cat /etc/apache2/mods-available/dir.conf
```

**确保 index.php 在第一位：**
```
DirectoryIndex index.php index.html index.cgi index.pl index.xhtml index.htm
```

如果不是，编辑它：
```bash
sudo nano /etc/apache2/mods-available/dir.conf
```

把 `index.php` 移到最前面，保存退出，然后重启Apache。

---

## ✅ 验证清单

- [ ] PHP 8.1 已安装
- [ ] libapache2-mod-php8.1 已安装
- [ ] php8.1 模块已启用
- [ ] php8.1 conf 已启用
- [ ] Apache 已重启
- [ ] 访问 test.php 能看到PHP信息
- [ ] 访问主页能看到登录页面

---

## 🎉 成功后继续

看到登录页面后，继续：

1. 导入数据库（见 `IMPORT_DATABASE.md`）
2. 修改 `core/Database.php` 配置
3. 登录系统：admin / admin123
