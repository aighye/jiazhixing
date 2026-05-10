"""Fix remaining missing columns in database tables"""
from app import create_app
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
    
    # Define remaining missing columns to add
    missing_cols = {
        'claim_manufacturers': [
            ("contact_phone", "VARCHAR(20)"),
        ],
        'dict_items': [
            ("name", "VARCHAR(100)"),
            ("code", "VARCHAR(50)"),
        ],
        'system_configs': [
            ("group_name", "VARCHAR(50) DEFAULT 'general'"),
        ],
        'work_order_parts': [
            ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            ("repair_category", "VARCHAR(20)"),
            ("created_by", "INT"),
            ("charge_type", "VARCHAR(20)"),
            ("repair_item_id", "INT"),
            ("remark", "TEXT"),
            ("outbound_status", "TINYINT DEFAULT 0"),
            ("discount_rate", "DECIMAL(4,2) DEFAULT 1"),
        ],
        'vehicles': [
            ("created_by", "INT"),
        ],
        'repair_item_template_parts': [
            ("sort_order", "INT DEFAULT 0"),
        ],
        'insurance_companies': [
            ("contact_phone", "VARCHAR(20)"),
        ],
        'repair_item_templates': [
            ("repair_category", "VARCHAR(20)"),
            ("created_by", "INT"),
            ("item_code", "VARCHAR(50)"),
            ("charge_type", "VARCHAR(20)"),
            ("labor_price", "DECIMAL(10,2) DEFAULT 0"),
            ("remark", "TEXT"),
            ("labor_hours", "DECIMAL(6,2) DEFAULT 0"),
            ("sort_order", "INT DEFAULT 0"),
            ("item_name", "VARCHAR(100)"),
        ],
    }
    
    count = 0
    with conn.cursor() as cursor:
        for table, columns in missing_cols.items():
            cursor.execute(f"DESCRIBE `{table}`")
            existing = {row[0].lower() for row in cursor.fetchall()}
            
            for col_name, col_def in columns:
                if col_name not in existing:
                    sql = f"ALTER TABLE `{table}` ADD COLUMN `{col_name}` {col_def}"
                    try:
                        cursor.execute(sql)
                        conn.commit()
                        print(f"Added {col_name} to {table}")
                        count += 1
                    except Exception as e:
                        print(f"Error adding {col_name} to {table}: {e}")
                else:
                    print(f"Skipping {col_name} in {table} (already exists)")
    
    conn.close()
    print(f"\n✅ Added {count} columns successfully!")
