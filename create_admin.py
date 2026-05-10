"""创建默认管理员账号"""
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    # 检查是否已存在管理员
    existing = User.query.filter_by(username='admin').first()
    if existing:
        print(f"管理员账号已存在: {existing.username}")
    else:
        admin = User(
            username='admin',
            real_name='系统管理员',
            phone='13800000000',
            email='admin@jzx.com',
            status=1,
            role_id=1
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("管理员账号创建成功！")
        print("用户名: admin")
        print("密码: admin123")
