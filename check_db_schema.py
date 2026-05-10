"""Compare SQLAlchemy model columns against MySQL database columns"""
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

    # Get all tables
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

    # Get all model classes from registered models
    mappers = db.Model.registry.mappers
    missing_columns = []

    for mapper in mappers:
        table_name = mapper.local_table.name
        if table_name not in tables:
            print(f"⚠️  Table '{table_name}' does not exist in database!")
            continue

        # Get actual columns from DB
        with conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{table_name}`")
            db_columns = {row[0].lower() for row in cursor.fetchall()}

        # Get model columns
        model_columns = {c.key.lower() for c in mapper.column_attrs}
        model_cols_sql = {c.key: c.columns[0] for c in mapper.column_attrs}

        # Find missing columns in DB
        for col in model_columns:
            if col not in db_columns:
                column_def = model_cols_sql.get(col)
                if column_def is not None:
                    col_type = str(column_def.type)
                    missing_columns.append((table_name, col, col_type))

    conn.close()

    if missing_columns:
        print(f"\nFound {len(missing_columns)} missing columns in database:\n")
        for table, col, col_type in missing_columns:
            print(f"  ALTER TABLE `{table}` ADD COLUMN `{col}` ... ({col_type})")
    else:
        print("\n✅ All model columns match the database schema!")
