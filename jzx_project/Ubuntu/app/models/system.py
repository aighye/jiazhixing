from datetime import datetime
from app.extensions import db

class SystemConfig(db.Model):
    __tablename__ = 'system_configs'
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(50), nullable=False, unique=True)
    config_value = db.Column(db.Text)
    config_type = db.Column(db.String(20), default='string')
    description = db.Column(db.String(200))
    group_name = db.Column('group', db.String(50), default='general')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'group': self.group_name,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BackupRecord(db.Model):
    __tablename__ = 'backup_records'
    id = db.Column(db.Integer, primary_key=True)
    backup_name = db.Column(db.String(100), nullable=False)
    backup_type = db.Column(db.String(20), default='full')
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.BigInteger)
    status = db.Column(db.SmallInteger, default=0)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'backup_name': self.backup_name,
            'backup_type': self.backup_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DictItem(db.Model):
    __tablename__ = 'dict_items'
    id = db.Column(db.Integer, primary_key=True)
    dict_type = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50))
    sort = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'dict_type': self.dict_type,
            'name': self.name,
            'code': self.code,
            'sort': self.sort,
            'status': self.status
        }
