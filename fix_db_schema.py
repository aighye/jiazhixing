"""Fix missing columns in database tables"""
from app import create_app
from app.extensions import db
import pymysql

app = create_app()

with app.app_context():
    config = app.config
    conn = pymysql.connect(
        host=config.get('DB_HOST', '127.0.0.1'),
        port=int(config.get('DB_PORT', '3306')),
        user=config.get('DB_USER', '4srepair'),
        password=config.get('DB_PASSWORD', '4srepair2024'),
        database=config.get('DB_NAME', '4s_repair_db'),
        charset='utf8mb4'
    )
    
    # Define missing columns to add
    missing_cols = {
        'parts_inbound_details': [
            ("unit", "VARCHAR(20) DEFAULT ''"),
            ("unit_price_with_tax", "DECIMAL(12,2) DEFAULT 0"),
            ("location", "VARCHAR(50) DEFAULT ''"),
        ],
        'repair_items': [
            ("discount_rate", "DECIMAL(4,2) DEFAULT 1"),
            ("charge_type", "VARCHAR(20)"),
            ("repair_category", "VARCHAR(20)"),
        ],
        'parts_inbound': [
            ("invoice_type", "VARCHAR(10) DEFAULT '无发票'"),
            ("tax_rate", "DECIMAL(5,2) DEFAULT 0"),
        ],
        'work_orders': [
            ("insurance_company", "VARCHAR(50)"),
            ("claim_manufacturer", "VARCHAR(50)"),
        ],
    }
    
    with conn.cursor() as cursor:
        for table, columns in missing_cols.items():
            cursor.execute(f"DESCRIBE `{table}`")
            existing = {row[0].lower() for row in cursor.fetchall()}
            
            for col_name, col_def in columns:
                if col_name not in existing:
                    sql = f"ALTER TABLE `{table}` ADD COLUMN `{col_name}` {col_def}"
                    print(f"Adding {col_name} to {table}...")
                    cursor.execute(sql)
                    conn.commit()
                    print(f"  Done!")
                else:
                    print(f"Skipping {col_name} in {table} (already exists)")
    
    # Create missing tables
    tables_sql = [
        """CREATE TABLE IF NOT EXISTS `claim_manufacturers` (
            `id` INT PRIMARY KEY AUTO_INCREMENT,
            `name` VARCHAR(100) NOT NULL,
            `code` VARCHAR(50),
            `contact_person` VARCHAR(50),
            `phone` VARCHAR(20),
            `address` VARCHAR(200),
            `status` TINYINT DEFAULT 1,
            `remark` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB COMMENT='索赔厂家表'""",
        
        """CREATE TABLE IF NOT EXISTS `dict_items` (
            `id` INT PRIMARY KEY AUTO_INCREMENT,
            `dict_type` VARCHAR(50) NOT NULL,
            `dict_label` VARCHAR(100) NOT NULL,
            `dict_value` VARCHAR(100),
            `sort` INT DEFAULT 0,
            `status` TINYINT DEFAULT 1,
            `remark` VARCHAR(200),
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX `idx_dict_type` (`dict_type`)
        ) ENGINE=InnoDB COMMENT='字典表'""",
        
        """CREATE TABLE IF NOT EXISTS `work_order_parts` (
            `id` INT PRIMARY KEY AUTO_INCREMENT,
            `order_id` INT NOT NULL COMMENT '工单ID',
            `part_id` INT NOT NULL COMMENT '配件ID',
            `quantity` INT NOT NULL COMMENT '数量',
            `unit_price` DECIMAL(10,2) NOT NULL COMMENT '单价',
            `total_price` DECIMAL(10,2) NOT NULL COMMENT '总价',
            `status` TINYINT DEFAULT 0 COMMENT '状态：0待出库 1已出库',
            `outbound_at` DATETIME COMMENT '出库时间',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`order_id`) REFERENCES `work_orders`(`id`),
            FOREIGN KEY (`part_id`) REFERENCES `parts`(`id`)
        ) ENGINE=InnoDB COMMENT='工单配件关联表'""",
        
        """CREATE TABLE IF NOT EXISTS `insurance_companies` (
            `id` INT PRIMARY KEY AUTO_INCREMENT,
            `name` VARCHAR(100) NOT NULL,
            `code` VARCHAR(50),
            `contact_person` VARCHAR(50),
            `phone` VARCHAR(20),
            `address` VARCHAR(200),
            `cooperation_level` TINYINT DEFAULT 1,
            `status` TINYINT DEFAULT 1,
            `remark` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB COMMENT='保险公司表'""",
        
        """CREATE TABLE IF NOT EXISTS `repair_item_templates` (
            `id` INT PRIMARY KEY AUTO_INCREMENT,
            `name` VARCHAR(100) NOT NULL COMMENT '模板名称',
            `code` VARCHAR(50) COMMENT '模板编码',
            `category` VARCHAR(50) COMMENT '分类',
            `standard_hours` DECIMAL(8,2) DEFAULT 0 COMMENT '标准工时',
            `standard_price` DECIMAL(10,2) DEFAULT 0 COMMENT '标准价格',
            `description` TEXT COMMENT '描述',
            `status` TINYINT DEFAULT 1,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY `idx_code` (`code`)
        ) ENGINE=InnoDB COMMENT='维修项目模板表'""",
        
        """CREATE TABLE IF NOT EXISTS `repair_item_template_parts` (
            `id` INT PRIMARY KEY AUTO_INCREMENT,
            `template_id` INT NOT NULL COMMENT '模板ID',
            `part_id` INT NOT NULL COMMENT '配件ID',
            `quantity` INT DEFAULT 1 COMMENT '数量',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`template_id`) REFERENCES `repair_item_templates`(`id`),
            FOREIGN KEY (`part_id`) REFERENCES `parts`(`id`)
        ) ENGINE=InnoDB COMMENT='维修项目模板配件关联表'""",
    ]
    
    print("\nCreating missing tables...")
    with conn.cursor() as cursor:
        for sql in tables_sql:
            table_name = sql.split('`')[1] if '`' in sql else 'unknown'
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"  Created table: {table_name}")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print(f"  Table {table_name} already exists, skipping")
                else:
                    print(f"  Error creating {table_name}: {e}")
    
    conn.close()
    print("\n✅ Database schema fix completed!")
