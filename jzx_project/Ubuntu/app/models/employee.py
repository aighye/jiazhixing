from datetime import datetime
from app.extensions import db

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_no = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.SmallInteger, default=0)
    phone = db.Column(db.String(20))
    id_card = db.Column(db.String(18))
    department = db.Column(db.String(50))
    position = db.Column(db.String(50))
    employee_type = db.Column(db.String(20))
    level = db.Column(db.String(20))
    entry_date = db.Column(db.Date)
    base_salary = db.Column(db.Numeric(10, 2), default=0)
    hourly_rate = db.Column(db.Numeric(8, 2), default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='employee', foreign_keys=[user_id])
    labor_stats = db.relationship('EmployeeLaborStat', backref='employee', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_no': self.employee_no,
            'name': self.name,
            'gender': self.gender,
            'phone': self.phone,
            'id_card': self.id_card,
            'department': self.department,
            'position': self.position,
            'employee_type': self.employee_type,
            'level': self.level,
            'entry_date': str(self.entry_date) if self.entry_date else None,
            'base_salary': float(self.base_salary) if self.base_salary else 0,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else 0,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EmployeeLaborStat(db.Model):
    __tablename__ = 'employee_labor_stats'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    stat_date = db.Column(db.Date, nullable=False)
    stat_month = db.Column(db.String(7), nullable=False)
    total_hours = db.Column(db.Numeric(8, 2), default=0)
    total_amount = db.Column(db.Numeric(12, 2), default=0)
    order_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'stat_date': str(self.stat_date) if self.stat_date else None,
            'stat_month': self.stat_month,
            'total_hours': float(self.total_hours) if self.total_hours else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'order_count': self.order_count
        }
