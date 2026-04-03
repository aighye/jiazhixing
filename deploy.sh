#!/bin/bash

# 汽车4S店维修系统 - 腾讯云Ubuntu自动部署脚本
# 使用方法：chmod +x deploy.sh && sudo ./deploy.sh

set -e

echo "======================================"
echo "  汽车4S店维修系统 - 自动部署脚本"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用 root 用户运行此脚本${NC}"
    echo "使用命令: sudo $0"
    exit 1
fi

echo -e "${YELLOW}[1/8] 更新系统包...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}[2/8] 安装 Apache2...${NC}"
apt install apache2 -y
systemctl start apache2
systemctl enable apache2

echo -e "${YELLOW}[3/8] 安装 PHP 8.1...${NC}"
apt install software-properties-common -y
add-apt-repository ppa:ondrej/php -y
apt update
apt install php8.1 libapache2-mod-php8.1 php8.1-mysql php8.1-curl php8.1-gd php8.1-mbstring php8.1-xml php8.1-zip -y

echo -e "${YELLOW}[4/8] 安装 MySQL 8.0...${NC}"
apt install mysql-server -y
systemctl start mysql
systemctl enable mysql

echo -e "${YELLOW}[5/8] 配置 MySQL...${NC}"
# 生成随机密码
DB_ROOT_PASSWORD=$(openssl rand -base64 12)
DB_USER_PASSWORD=$(openssl rand -base64 12)

echo "创建数据库和用户..."
mysql <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$DB_ROOT_PASSWORD';
CREATE DATABASE IF NOT EXISTS auto_4s_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'auto_4s_user'@'localhost' IDENTIFIED BY '$DB_USER_PASSWORD';
GRANT ALL PRIVILEGES ON auto_4s_system.* TO 'auto_4s_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo -e "${YELLOW}[6/9] 创建必要目录...${NC}"
# 确保所有目录存在
mkdir -p /var/www/html/config
mkdir -p /var/www/html/core
mkdir -p /var/www/html/database
mkdir -p /var/www/html/customers/vehicles
mkdir -p /var/www/html/workorders
mkdir -p /var/www/html/parts
mkdir -p /var/www/html/settlements
mkdir -p /var/www/html/reports
mkdir -p /var/www/html/system
mkdir -p /var/www/html/uploads
echo "✅ 目录结构创建完成"

echo -e "${YELLOW}[7/9] 配置项目文件...${NC}"
# 设置目录权限
chown -R www-data:www-data /var/www/html
find /var/www/html -type d -exec chmod 755 {} \;
find /var/www/html -type f -exec chmod 644 {} \;

# 设置uploads目录权限
chmod 777 /var/www/html/uploads

# 更新数据库配置文件
if [ -f /var/www/html/core/Database.php ]; then
    echo "更新数据库连接配置..."
    sed -i "s/private \$password = ''/private \$password = '$DB_USER_PASSWORD'/" /var/www/html/core/Database.php
    sed -i "s/private \$username = 'root'/private \$username = 'auto_4s_user'/" /var/www/html/core/Database.php
fi

echo -e "${YELLOW}[8/9] 导入数据库...${NC}"
if [ -f /var/www/html/database/install.sql ]; then
    mysql -u auto_4s_user -p$DB_USER_PASSWORD auto_4s_system < /var/www/html/database/install.sql
fi

echo -e "${YELLOW}[9/9] 配置防火墙...${NC}"
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

echo ""
echo "======================================"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo "======================================"
echo ""
echo "📊 系统信息："
echo "   访问地址: http://$(curl -s ifconfig.me)"
echo ""
echo "🔐 数据库信息："
echo "   数据库名: auto_4s_system"
echo "   用户名: auto_4s_user"
echo "   密码: $DB_USER_PASSWORD"
echo "   Root密码: $DB_ROOT_PASSWORD"
echo ""
echo "👤 默认登录账号："
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo -e "${RED}⚠️  重要提醒：${NC}"
echo "   1. 请立即保存上述密码信息！"
echo "   2. 首次登录后请修改管理员密码！"
echo "   3. 请在腾讯云安全组开放80和443端口"
echo ""
echo "密码已保存到: /root/db_credentials.txt"

# 保存密码到文件
cat > /root/db_credentials.txt <<EOF
汽车4S店维修系统 - 数据库凭据
=================================
数据库名: auto_4s_system
用户名: auto_4s_user
密码: $DB_USER_PASSWORD
Root密码: $DB_ROOT_PASSWORD

系统默认账号:
用户名: admin
密码: admin123
EOF

chmod 600 /root/db_credentials.txt

echo ""
echo -e "${GREEN}🎉 部署成功！请访问 http://$(curl -s ifconfig.me)${NC}"
