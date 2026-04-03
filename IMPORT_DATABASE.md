# 📚 导入数据库 - 超详细操作指南

## 前提条件
- ✅ 已连接到服务器（SSH）
- ✅ 项目文件已上传到 `/var/www/html/`
- ✅ MySQL 已安装并运行

---

## 📋 完整步骤

### 第一步：确认 SQL 文件存在

在服务器终端执行：
```bash
cd /var/www/html
ls -la database/
```

你应该能看到 `install.sql` 文件：
```
-rw-r--r-- 1 root root xxxxx Apr  3 10:00 install.sql
```

如果没有这个文件，请先上传项目文件！

---

### 第二步：登录 MySQL

#### 方式一：使用 root 用户登录（推荐）
```bash
sudo mysql
```

注意：这里不需要输入密码，直接按回车。

#### 方式二：如果方式一不行，尝试：
```bash
mysql -u root -p
```
然后输入 MySQL root 密码（如果有的话）。

---

### 第三步：创建数据库（如果还没创建）

登录到 MySQL 后，你会看到 MySQL 提示符：
```
mysql>
```

现在复制下面的 SQL 语句，一行一行执行，或者一起粘贴：

```sql
CREATE DATABASE IF NOT EXISTS auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

按回车执行，你应该看到：
```
Query OK, 1 row affected (0.01 sec)
```

---

### 第四步：创建数据库用户

继续在 `mysql>` 提示符下执行：

```sql
CREATE USER IF NOT EXISTS 'auto_4s_user'@'localhost' IDENTIFIED BY 'Auto4s@2024';
```

按回车，你应该看到：
```
Query OK, 0 rows affected (0.01 sec)
```

---

### 第五步：授权

继续执行：

```sql
GRANT ALL PRIVILEGES ON auto_4s_system.* TO 'auto_4s_user'@'localhost';
```

按回车：
```
Query OK, 0 rows affected (0.01 sec)
```

---

### 第六步：刷新权限

```sql
FLUSH PRIVILEGES;
```

按回车：
```
Query OK, 0 rows affected (0.00 sec)
```

---

### 第七步：退出 MySQL

```sql
EXIT;
```

或者：
```sql
quit;
```

按回车，你会回到服务器终端提示符 `#` 或 `$`。

---

### 第八步：导入数据库（关键步骤！）

现在你回到了服务器终端，执行：

```bash
mysql -u auto_4s_user -p auto_4s_system < /var/www/html/database/install.sql
```

按回车后，会提示你输入密码：
```
Enter password:
```

**输入密码：`Auto4s@2024`**

注意：输入密码时屏幕上不会显示任何字符，这是正常的！输完直接按回车。

---

## ✅ 验证导入是否成功

### 方法一：查看是否有错误

如果导入成功，不会有任何输出（没有消息就是好消息！）

如果有错误，会显示类似：
```
ERROR 1045 (28000): Access denied for user...
```

### 方法二：登录数据库查看表

```bash
mysql -u auto_4s_user -p auto_4s_system
```

输入密码：`Auto4s@2024`

然后执行：
```sql
SHOW TABLES;
```

你应该看到 20+ 张表：
```
+--------------------------+
| Tables_in_auto_4s_system |
+--------------------------+
| customers                |
| customer_vehicles        |
| work_orders              |
| work_order_services      |
| ...                      |
+--------------------------+
25 rows in set (0.00 sec)
```

查看表数量对了就说明成功了！

然后退出：
```sql
EXIT;
```

---

## 🔧 常见问题解决

### 问题1：提示 "Access denied for user"

**原因**：密码输错了，或者用户没创建好

**解决**：
```bash
sudo mysql
```
然后重新执行第三步到第七步。

### 问题2：提示 "No such file or directory"

**原因**：`install.sql` 文件不存在

**解决**：
```bash
cd /var/www/html
ls -la database/
```
确认文件在那里，不在的话重新上传项目文件。

### 问题3：导入时提示 "Unknown database"

**原因**：数据库没创建

**解决**：回到第三步，先创建数据库。

---

## 📝 完整的导入流程（复制粘贴版）

### 整个流程可以一次性复制执行：

```bash
# 1. 确认文件存在
cd /var/www/html
ls -la database/

# 2. 创建数据库和用户
sudo mysql <<EOF
CREATE DATABASE IF NOT EXISTS auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'auto_4s_user'@'localhost' IDENTIFIED BY 'Auto4s@2024';
GRANT ALL PRIVILEGES ON auto_4s_system.* TO 'auto_4s_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# 3. 导入数据库
mysql -u auto_4s_user -pAuto4s@2024 auto_4s_system < /var/www/html/database/install.sql

# 4. 验证
mysql -u auto_4s_user -pAuto4s@2024 auto_4s_system -e "SHOW TABLES;"
```

注意：`-p` 和密码之间没有空格！

---

## ✅ 导入成功后的下一步

导入成功后，继续配置：

1. 修改 `core/Database.php` 文件
2. 设置文件权限
3. 配置防火墙
4. 访问系统

详见 `MANUAL_DEPLOY.md` 文件！
