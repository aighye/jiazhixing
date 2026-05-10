from datetime import datetime
from app.extensions import db

def _get_user_name(user_id):
    if not user_id:
        return ''
    from app.models.user import User
    user = User.query.get(user_id)
    return user.real_name if user and user.real_name else (user.username if user else '')

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer_no = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    gender = db.Column(db.SmallInteger, default=0)
    birthday = db.Column(db.Date)
    id_card = db.Column(db.String(18))
    address = db.Column(db.String(200))
    customer_type = db.Column(db.SmallInteger, default=1)
    company_name = db.Column(db.String(100))
    vip_level = db.Column(db.SmallInteger, default=0)
    total_spending = db.Column(db.Numeric(12, 2), default=0)
    points = db.Column(db.Integer, default=0)
    remark = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=1)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicles = db.relationship('Vehicle', backref='customer', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='customer', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_no': self.customer_no,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'gender': self.gender,
            'birthday': str(self.birthday) if self.birthday else None,
            'id_card': self.id_card,
            'address': self.address,
            'customer_type': self.customer_type,
            'company_name': self.company_name,
            'vip_level': self.vip_level,
            'total_spending': float(self.total_spending) if self.total_spending else 0,
            'points': self.points,
            'remark': self.remark,
            'status': self.status,
            'vehicle_count': self.vehicles.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator_name': _get_user_name(self.created_by)
        }

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_no = db.Column(db.String(30), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    plate_number = db.Column(db.String(20), nullable=False)
    vin = db.Column(db.String(30))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    color = db.Column(db.String(20))
    engine_no = db.Column(db.String(30))
    purchase_date = db.Column(db.Date)
    mileage = db.Column(db.Integer, default=0)
    insurance_date = db.Column(db.Date)
    inspection_date = db.Column(db.Date)
    photo = db.Column(db.String(255))
    remark = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=1)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_no': self.vehicle_no,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'plate_number': self.plate_number,
            'vin': self.vin,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'color': self.color,
            'engine_no': self.engine_no,
            'purchase_date': str(self.purchase_date) if self.purchase_date else None,
            'mileage': self.mileage,
            'insurance_date': str(self.insurance_date) if self.insurance_date else None,
            'inspection_date': str(self.inspection_date) if self.inspection_date else None,
            'photo': self.photo,
            'remark': self.remark,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator_name': _get_user_name(self.created_by)
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    appointment_no = db.Column(db.String(30), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    service_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=0)
    confirm_by = db.Column(db.Integer)
    remark = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle = db.relationship('Vehicle', backref='appointments')

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_no': self.appointment_no,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'vehicle_id': self.vehicle_id,
            'plate_number': self.vehicle.plate_number if self.vehicle else None,
            'phone': self.phone,
            'appointment_date': str(self.appointment_date) if self.appointment_date else None,
            'appointment_time': str(self.appointment_time) if self.appointment_time else None,
            'service_type': self.service_type,
            'description': self.description,
            'status': self.status,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator_name': _get_user_name(self.created_by)
        }
