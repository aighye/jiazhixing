from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, JSONText
from flask_login import UserMixin

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    permissions = db.Column(JSONText)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = db.relationship('User', backref='role', lazy='dynamic')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.SmallInteger, default=0)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    id_card = db.Column(db.String(18))
    avatar = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    department = db.Column(db.String(50))
    position = db.Column(db.String(50))
    employee_type = db.Column(db.String(20))
    employee_no = db.Column(db.String(30))
    level = db.Column(db.String(20))
    title = db.Column(db.String(50))
    entry_date = db.Column(db.Date)
    base_salary = db.Column(db.Numeric(10, 2), default=0)
    hourly_rate = db.Column(db.Numeric(8, 2), default=0)
    status = db.Column(db.SmallInteger, default=1)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, perm):
        if not self.role or not self.role.permissions:
            return False
        perms = self.role.permissions
        if '*' in perms:
            return True
        module = perm.split(':')[0]
        if f'{module}:*' in perms:
            return True
        return perm in perms

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'gender': self.gender,
            'phone': self.phone,
            'email': self.email,
            'id_card': self.id_card,
            'avatar': self.avatar,
            'role': self.role.name if self.role else None,
            'role_id': self.role_id,
            'role_code': self.role.code if self.role else None,
            'permissions': self.role.permissions if self.role else [],
            'department': self.department,
            'position': self.position,
            'employee_type': self.employee_type,
            'employee_no': self.employee_no,
            'level': self.level,
            'title': self.title,
            'entry_date': str(self.entry_date) if self.entry_date else None,
            'base_salary': float(self.base_salary) if self.base_salary else 0,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else 0,
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(50))
    action = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50))
    description = db.Column(db.String(500))
    ip_address = db.Column(db.String(50))
    request_data = db.Column(JSONText)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'module': self.module,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
