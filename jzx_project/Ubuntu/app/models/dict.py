from app.extensions import db
from datetime import datetime


class ClaimManufacturer(db.Model):
    """索赔厂家"""
    __tablename__ = 'claim_manufacturers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    contact_person = db.Column(db.String(50))
    contact_phone = db.Column(db.String(20))
    remark = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=1)  # 1启用 0停用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'remark': self.remark,
            'status': self.status,
            'status_name': '启用' if self.status == 1 else '停用',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InsuranceCompany(db.Model):
    """保险公司"""
    __tablename__ = 'insurance_companies'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    contact_person = db.Column(db.String(50))
    contact_phone = db.Column(db.String(20))
    remark = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=1)  # 1启用 0停用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'remark': self.remark,
            'status': self.status,
            'status_name': '启用' if self.status == 1 else '停用',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
