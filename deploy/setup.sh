#!/bin/bash
# ============================================
# 汽车4S店维修管理系统 - Ubuntu 一键部署脚本
# 适用于腾讯云 Ubuntu 20.04/22.04
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  汽车4S店维修管理系统 - 自动部署脚本${NC}"
echo -e "${GREEN}============================================${NC}"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用 root 用户运行此脚本${NC}"
    echo "执行: sudo bash deploy/setup.sh"
    exit 1
fi

# ========== 配置变量 ==========
APP_DIR="/opt/4s_repair_management"
DB_NAME="4s_repair_db"
DB_USER="root"
DB_PASS="4srepair2024"
SERVER_IP="1.14.43.118"
PYTHON_VERSION="3.10"
NODE_VERSION="18"

# ========== 1. 更新系统 ==========
echo -e "${YELLOW}[1/8] 更新系统软件包...${NC}"
apt-get update -y
apt-get upgrade -y

# ========== 2. 安装基础依赖 ==========
echo -e "${YELLOW}[2/8] 安装基础依赖...${NC}"
apt-get install -y \
    python3 python3-pip python3-venv \
    mysql-server mysql-client \
    nginx \
    git curl wget unzip \
    build-essential libssl-dev libffi-dev \
    supervisor

# ========== 3. 配置 MySQL ==========
echo -e "${YELLOW}[3/8] 配置 MySQL...${NC}"

# 启动 MySQL
systemctl start mysql
systemctl enable mysql

# 设置 root 密码并创建数据库
mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASS}';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "MySQL 配置完成"

# ========== 4. 部署后端 ==========
echo -e "${YELLOW}[4/8] 部署后端应用...${NC}"

# 创建应用目录
mkdir -p ${APP_DIR}
mkdir -p ${APP_DIR}/uploads
mkdir -p ${APP_DIR}/backups
mkdir -p ${APP_DIR}/logs

# 复制后端代码（假设代码已上传到服务器）
# 如果使用 git，取消下面的注释
# cd ${APP_DIR} && git clone <your-repo-url> .

# 创建 Python 虚拟环境
python3 -m venv ${APP_DIR}/venv
source ${APP_DIR}/venv/bin/activate

# 安装 Python 依赖
if [ -f "${APP_DIR}/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r ${APP_DIR}/requirements.txt
fi

# 初始化数据库
if [ -f "${APP_DIR}/init_db.sql" ]; then
    mysql -u root -p${DB_PASS} ${DB_NAME} < ${APP_DIR}/init_db.sql
    echo "数据库初始化完成"
fi

# 创建默认管理员密码 (admin123)
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/4s_repair_management')
from werkzeug.security import generate_password_hash
hash_value = generate_password_hash('admin123')
print(f"Admin password hash: {hash_value}")

# Update admin password in database
import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', password='4srepair2024', database='4s_repair_db', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'admin'", (hash_value,))
conn.commit()
cursor.close()
conn.close()
print("管理员密码已设置: admin / admin123")
PYEOF

deactivate

echo "后端部署完成"

# ========== 5. 部署前端 ==========
echo -e "${YELLOW}[5/8] 部署前端应用...${NC}"

# 安装 Node.js
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
    apt-get install -y nodejs
fi

# 构建前端
if [ -d "${APP_DIR}/frontend" ]; then
    cd ${APP_DIR}/frontend
    npm install
    npm run build

    # 将构建产物复制到 Nginx 目录
    mkdir -p /var/www/4s_repair
    cp -r dist/* /var/www/4s_repair/
    echo "前端构建完成"
else
    echo "前端目录不存在，跳过前端构建"
fi

# ========== 6. 配置 Gunicorn ==========
echo -e "${YELLOW}[6/8] 配置 Gunicorn...${NC}"

cat > ${APP_DIR}/gunicorn_config.py << 'EOF'
import multiprocessing

bind = '127.0.0.1:5000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
threads = 2
timeout = 120
accesslog = '/opt/4s_repair_management/logs/gunicorn_access.log'
errorlog = '/opt/4s_repair_management/logs/gunicorn_error.log'
loglevel = 'info'
EOF

# ========== 7. 配置 Systemd 服务 ==========
echo -e "${YELLOW}[7/8] 配置 Systemd 服务...${NC}"

cat > /etc/systemd/system/4s_repair.service << EOF
[Unit]
Description=4S Repair Management System
After=network.target mysql.service

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=4s-repair-secret-key-change-in-production-2024"
Environment="DB_USER=${DB_USER}"
Environment="DB_PASSWORD=${DB_PASS}"
Environment="DB_HOST=127.0.0.1"
Environment="DB_PORT=3306"
Environment="DB_NAME=${DB_NAME}"
ExecStart=${APP_DIR}/venv/bin/gunicorn -c ${APP_DIR}/gunicorn_config.py "run:app"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable 4s-repair
systemctl start 4s-repair

echo "后端服务已启动"

# ========== 8. 配置 Nginx ==========
echo -e "${YELLOW}[8/8] 配置 Nginx...${NC}"

cat > /etc/nginx/sites-available/4s_repair << EOF
server {
    listen 80;
    server_name ${SERVER_IP};

    # 前端静态文件
    location / {
        root /var/www/4s_repair;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
        client_max_body_size 16M;
    }

    # 上传文件访问
    location /uploads/ {
        alias ${APP_DIR}/uploads/;
        expires 30d;
    }
}
EOF

# 启用站点配置
ln -sf /etc/nginx/sites-available/4s_repair /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
nginx -t

# 重启 Nginx
systemctl restart nginx
systemctl enable nginx

echo "Nginx 配置完成"

# ========== 配置防火墙 ==========
echo -e "${YELLOW}配置防火墙...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    # ufw enable  # 取消注释以启用防火墙
    echo "防火墙规则已添加（未启用）"
fi

# ========== 完成 ==========
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "访问地址: http://${SERVER_IP}"
echo "默认账号: admin / admin123"
echo ""
echo "常用命令："
echo "  查看后端状态: systemctl status 4s-repair"
echo "  查看后端日志: tail -f ${APP_DIR}/logs/gunicorn_error.log"
echo "  重启后端: systemctl restart 4s-repair"
echo "  查看 Nginx 日志: tail -f /var/log/nginx/error.log"
echo "  重启 Nginx: systemctl restart nginx"
echo ""
echo -e "${YELLOW}重要提示：${NC}"
echo "1. 请尽快修改 MySQL root 密码和系统 SECRET_KEY"
echo "2. 建议配置 HTTPS（使用 Let's Encrypt 免费证书）"
echo "3. 建议配置防火墙规则，只开放必要端口"
echo "4. 请定期备份数据库"
