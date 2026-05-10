# 汽车4S店维修管理系统 - 部署指南

## 服务器信息
- IP: 1.14.43.118
- 系统: Ubuntu 20.04/22.04
- 访问地址: http://1.14.43.118

## 部署步骤

### 1. 上传项目文件到服务器

将整个 `4s_repair_management` 目录上传到服务器 `/opt/` 目录下：

```bash
# 本地执行（使用 scp）
scp -r 4s_repair_management root@1.14.43.118:/opt/

# 或使用 rsync
rsync -avz 4s_repair_management/ root@1.14.43.118:/opt/4s_repair_management/
```

### 2. 执行一键部署脚本

```bash
ssh root@1.14.43.118
cd /opt/4s_repair_management
chmod +x deploy/setup.sh
bash deploy/setup.sh
```

### 3. 验证部署

部署完成后，访问 http://1.14.43.118 确认系统正常运行。

默认账号: admin / admin123

## 手动部署（如需分步操作）

### 安装依赖
```bash
apt update
apt install -y python3 python3-pip python3-venv mysql-server nginx supervisor
```

### 配置 MySQL
```bash
mysql -u root
# 执行 SQL 设置密码和创建数据库
```

### 部署后端
```bash
cd /opt/4s_repair_management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mysql -u root -p4srepair2024 4s_repair_db < init_db.sql
```

### 部署前端
```bash
cd /opt/4s_repair_management/frontend
npm install
npm run build
cp -r dist/* /var/www/4s_repair/
```

### 启动服务
```bash
systemctl start 4s-repair
systemctl start nginx
```

## 常用运维命令

| 操作 | 命令 |
|------|------|
| 查看后端状态 | `systemctl status 4s-repair` |
| 重启后端 | `systemctl restart 4s-repair` |
| 后端日志 | `tail -f /opt/4s_repair_management/logs/gunicorn_error.log` |
| 重启 Nginx | `systemctl restart nginx` |
| Nginx 日志 | `tail -f /var/log/nginx/error.log` |
| 数据库备份 | `mysqldump -u root -p4srepair2024 4s_repair_db > backup.sql` |

## 安全建议

1. **修改默认密码**: 修改 MySQL 密码、管理员密码和 SECRET_KEY
2. **配置 HTTPS**: 使用 Let's Encrypt 免费证书
3. **防火墙**: 只开放 80、443、22 端口
4. **定期备份**: 设置数据库自动备份计划任务
