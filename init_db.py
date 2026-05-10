"""数据库初始化脚本"""
import pymysql
from app.config import Config

def init_database():
    """初始化数据库，执行SQL脚本"""
    connection = pymysql.connect(
        host=Config.DB_HOST,
        port=int(Config.DB_PORT),
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset='utf8mb4'
    )

    with open('init_db.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()

    cursor = connection.cursor()
    # Split by semicolons and execute each statement
    statements = sql_content.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"Warning: {e}")

    connection.commit()
    cursor.close()
    connection.close()
    print("数据库初始化完成！")

if __name__ == '__main__':
    init_database()
