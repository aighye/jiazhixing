#!/bin/bash
# ============================================
# 汽车4S店维修管理系统 - 环境恢复脚本
# 每次环境重置后运行此脚本即可恢复
# 用法: bash setup_env.sh
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_PASS="4srepair2024"
DB_NAME="4s_repair_db"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  汽车4S店维修管理系统 - 环境恢复${NC}"
echo -e "${GREEN}============================================${NC}"

# ========== 1. 启动 MySQL ==========
echo -e "${YELLOW}[1/5] 启动 MySQL...${NC}"

if ! pgrep -x mysqld > /dev/null 2>&1; then
    # 确保 socket 目录存在
    mkdir -p /var/run/mysqld
    chown mysql:mysql /var/run/mysqld 2>/dev/null || true

    # 尝试多种方式启动
    if command -v systemctl &>/dev/null; then
        systemctl start mysql 2>/dev/null || true
    fi

    if ! pgrep -x mysqld > /dev/null 2>&1; then
        mysqld --user=root --datadir=/var/lib/mysql &>/dev/null &
        sleep 6
    fi

    if ! pgrep -x mysqld > /dev/null 2>&1; then
        mysqld_safe --user=root &>/dev/null &
        sleep 6
    fi
fi

# 等待 MySQL 就绪（最多30秒）
for i in $(seq 1 30); do
    if mysql -u root -e "SELECT 1" &>/dev/null 2>&1; then
        echo "MySQL 已启动"
        break
    fi
    if mysql -u root -p${DB_PASS} -e "SELECT 1" &>/dev/null 2>&1; then
        echo "MySQL 已启动（已设置密码）"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}MySQL 启动失败，请检查: tail -20 /tmp/mysql_start.log${NC}"
        exit 1
    fi
    sleep 1
done

# ========== 2. 配置 MySQL ==========
echo -e "${YELLOW}[2/5] 配置 MySQL...${NC}"

# 设置密码（如果还没设置）
if mysql -u root -e "SELECT 1" &>/dev/null 2>&1; then
    mysql -u root <<EOF 2>/dev/null
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASS}';
FLUSH PRIVILEGES;
EOF
fi

MYSQL_CMD="mysql -u root -p${DB_PASS}"

# 创建数据库
$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;" 2>/dev/null

# 检查是否需要初始化表
TABLE_COUNT=$($MYSQL_CMD $DB_NAME -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${DB_NAME}';" 2>/dev/null || echo "0")

if [ "$TABLE_COUNT" -eq 0 ] || [ -z "$TABLE_COUNT" ]; then
    echo "数据库为空，执行初始化..."
    if [ -f "${APP_DIR}/init_db.sql" ]; then
        $MYSQL_CMD $DB_NAME < "${APP_DIR}/init_db.sql"
        echo "数据库初始化完成"
    else
        echo -e "${RED}init_db.sql 不存在${NC}"
        exit 1
    fi
else
    echo "数据库已存在 ${TABLE_COUNT} 张表，跳过初始化"
fi

# 创建缺失的 dict_items 表（init_db.sql 中可能没有）
$MYSQL_CMD $DB_NAME -e "
CREATE TABLE IF NOT EXISTS dict_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dict_type VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50),
    sort INT DEFAULT 0,
    status SMALLINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dict_type (dict_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
" 2>/dev/null

# 补充 init_db.sql 中缺失的字段和表
for sql in \
  "ALTER TABLE work_orders ADD COLUMN repair_confirmed TINYINT DEFAULT 0" \
  "ALTER TABLE work_orders ADD COLUMN parts_outbound_confirmed TINYINT DEFAULT 0" \
  "ALTER TABLE work_orders ADD COLUMN claim_manufacturer VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE work_orders ADD COLUMN insurance_company VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN pinyin_code VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN specification VARCHAR(100) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN network_price DECIMAL(10,2) DEFAULT 0" \
  "ALTER TABLE parts ADD COLUMN safety_stock INT DEFAULT 0" \
  "ALTER TABLE parts ADD COLUMN min_package_qty INT DEFAULT 0" \
  "ALTER TABLE parts ADD COLUMN boutique_location VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN spare_location VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN factory_code VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN origin VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN replaceable_part VARCHAR(100) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN location_code VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN warehouse_location VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN applicable_vehicles TEXT DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN applicable_vehicle VARCHAR(100) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN category1 VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN category2 VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE parts ADD COLUMN discontinued TINYINT(1) DEFAULT 0" \
  "ALTER TABLE parts ADD COLUMN archive_remark TEXT DEFAULT NULL" \
  "ALTER TABLE parts_inbound ADD COLUMN invoice_type VARCHAR(10) DEFAULT '无发票'" \
  "ALTER TABLE parts_inbound ADD COLUMN tax_rate DECIMAL(5,2) DEFAULT 0" \
  "ALTER TABLE parts_inbound_details ADD COLUMN unit_price_with_tax DECIMAL(12,2) DEFAULT 0" \
  "ALTER TABLE parts_inbound_details ADD COLUMN unit VARCHAR(20) DEFAULT ''" \
  "ALTER TABLE parts_inbound_details ADD COLUMN location VARCHAR(50) DEFAULT ''" \
  "ALTER TABLE work_order_flow_logs ADD COLUMN operator_no VARCHAR(30) DEFAULT NULL" \
  "ALTER TABLE work_order_flow_logs ADD COLUMN operator_dept VARCHAR(50) DEFAULT NULL" \
  "ALTER TABLE repair_items ADD COLUMN charge_type VARCHAR(20) DEFAULT NULL" \
  "ALTER TABLE repair_items ADD COLUMN repair_category VARCHAR(20) DEFAULT NULL" \
  "ALTER TABLE repair_items ADD COLUMN discount_rate DECIMAL(4,2) DEFAULT 1" \
  "ALTER TABLE vehicles ADD COLUMN created_by INT DEFAULT NULL" \
  "ALTER TABLE appointments ADD COLUMN created_by INT DEFAULT NULL"; do
  $MYSQL_CMD $DB_NAME -e "$sql" 2>/dev/null || true
done

# 创建缺失的表
$MYSQL_CMD $DB_NAME -e "
CREATE TABLE IF NOT EXISTS work_order_parts (
    id INT PRIMARY KEY AUTO_INCREMENT, order_id INT NOT NULL, part_id INT NOT NULL,
    repair_item_id INT DEFAULT NULL, quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) DEFAULT 0, total_price DECIMAL(10,2) DEFAULT 0,
    discount_rate DECIMAL(4,2) DEFAULT 1, charge_type VARCHAR(20) DEFAULT NULL,
    repair_category VARCHAR(20) DEFAULT NULL, remark TEXT DEFAULT NULL,
    outbound_status SMALLINT DEFAULT 0, created_by INT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES work_orders(id), FOREIGN KEY (part_id) REFERENCES parts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS repair_item_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100) NOT NULL,
    item_code VARCHAR(50) DEFAULT NULL,
    category VARCHAR(50) DEFAULT NULL,
    charge_type VARCHAR(20) DEFAULT NULL,
    repair_category VARCHAR(20) DEFAULT NULL,
    labor_hours DECIMAL(6,2) DEFAULT 0,
    labor_price DECIMAL(10,2) DEFAULT 0,
    description TEXT DEFAULT NULL,
    status SMALLINT DEFAULT 1,
    sort_order INT DEFAULT 0,
    remark TEXT DEFAULT NULL,
    created_by INT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS repair_item_template_parts (
    id INT PRIMARY KEY AUTO_INCREMENT, template_id INT NOT NULL,
    part_id INT NOT NULL, quantity INT DEFAULT 1,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES repair_item_templates(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS claim_manufacturers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE DEFAULT NULL,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(50) DEFAULT NULL,
    contact_phone VARCHAR(20) DEFAULT NULL,
    remark TEXT DEFAULT NULL,
    status TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS insurance_companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE DEFAULT NULL,
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(50) DEFAULT NULL,
    contact_phone VARCHAR(20) DEFAULT NULL,
    remark TEXT DEFAULT NULL,
    status TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO claim_manufacturers (id, name, code, status) VALUES
(1, '宝马中国', 'SP001', 1), (2, '奔驰中国', 'SP002', 1), (3, '奥迪中国', 'SP003', 1), (4, '大众中国', 'SP004', 1), (5, '丰田中国', 'SP005', 1);
INSERT IGNORE INTO insurance_companies (id, name, code, status) VALUES
(1, '中国人保', 'BX001', 1), (2, '中国平安', 'BX002', 1), (3, '太平洋保险', 'BX003', 1), (4, '中国人寿', 'BX004', 1), (5, '阳光保险', 'BX005', 1);
" 2>/dev/null

# 插入默认字典数据
$MYSQL_CMD $DB_NAME -e "
INSERT IGNORE INTO dict_items (dict_type, name, code, sort, status) VALUES
('repair_category', '保养', 'maintenance', 1, 1),
('repair_category', '机修', 'mechanical', 2, 1),
('repair_category', '钣金', 'sheet_metal', 3, 1);
" 2>/dev/null

# 创建默认管理员账号（init_db.sql 中不含用户数据）
python3 -c "
from werkzeug.security import generate_password_hash
import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', password='${DB_PASS}', database='${DB_NAME}', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('SELECT id FROM users WHERE username=%s', ('admin',))
if not cursor.fetchone():
    cursor.execute('SELECT id FROM roles WHERE code=%s', ('admin',))
    role = cursor.fetchone()
    role_id = role[0] if role else 1
    pw_hash = generate_password_hash('admin123')
    cursor.execute('INSERT INTO users (username, password_hash, real_name, role_id, status) VALUES (%s, %s, %s, %s, 1)',
                   ('admin', pw_hash, '系统管理员', role_id))
    conn.commit()
    print('管理员账号已创建: admin / admin123')
else:
    print('管理员账号已存在')
cursor.close()
conn.close()
" 2>/dev/null

echo "MySQL 配置完成"

# ========== 3. 安装 Python 依赖 ==========
echo -e "${YELLOW}[3/5] 安装 Python 依赖...${NC}"

if [ -f "${APP_DIR}/requirements.txt" ]; then
    pip install -r "${APP_DIR}/requirements.txt" --break-system-packages --quiet 2>/dev/null
    echo "Python 依赖安装完成"
else
    echo -e "${RED}requirements.txt 不存在${NC}"
    exit 1
fi

# ========== 4. 构建前端 ==========
echo -e "${YELLOW}[4/5] 构建前端...${NC}"

if [ -d "${APP_DIR}/frontend" ] && [ -d "${APP_DIR}/frontend/node_modules" ]; then
    cd "${APP_DIR}/frontend"
    node ./node_modules/vite/bin/vite.js build 2>/dev/null | tail -1
    echo "前端构建完成"
elif [ -d "${APP_DIR}/frontend/dist" ]; then
    echo "前端已构建，跳过"
else
    echo -e "${YELLOW}前端 node_modules 不存在，请先执行: cd frontend && npm install${NC}"
fi

# ========== 5. 启动 Flask 服务 ==========
echo -e "${YELLOW}[5/5] 启动 Flask 服务...${NC}"

# 停止已有进程
pkill -f "python3 run.py" 2>/dev/null || true
sleep 1

cd "${APP_DIR}"
nohup python3 run.py > /tmp/flask.log 2>&1 &
sleep 4

# 验证服务
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}Flask 服务已启动: http://localhost:5000${NC}"
else
    echo -e "${RED}Flask 服务启动失败(HTTP ${HTTP_CODE})，查看日志: tail -20 /tmp/flask.log${NC}"
    exit 1
fi

# 导入示例数据（仅首次或表为空时执行）
python3 -c "
import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', password='${DB_PASS}', database='${DB_NAME}', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM customers')
if cursor.fetchone()[0] == 0:
    import subprocess
    subprocess.run(['mysql', '-u', 'root', '-p${DB_PASS}', '${DB_NAME}'], stdin=open('sample_data.sql','r'), check=False, capture_output=True)
    conn.commit()
    print('示例数据导入完成')
else:
    print('示例数据已存在，跳过')
conn.close()
" 2>/dev/null

# ========== 完成 ==========
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  环境恢复完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "访问地址: http://localhost:5000"
echo "默认账号: admin / admin123"
echo ""
echo "如需重新运行: bash setup_env.sh"
