"""SQLite 数据库初始化脚本"""
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # 创建所有表
    db.create_all()
    print("数据库表创建完成！")
