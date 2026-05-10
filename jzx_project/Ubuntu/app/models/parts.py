from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import lazyload

def _get_user_name(user_id):
    if not user_id:
        return ''
    from app.models.user import User
    user = User.query.get(user_id)
    return user.real_name if user and user.real_name else (user.username if user else '')

class PartsCategory(db.Model):
    __tablename__ = 'parts_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, default=0)
    level = db.Column(db.SmallInteger, default=1)
    sort = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parts = db.relationship('Part', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'level': self.level,
            'sort': self.sort,
            'status': self.status,
            'parts_count': self.parts.count()
        }

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    contact_person = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    credit_level = db.Column(db.SmallInteger, default=1)
    status = db.Column(db.SmallInteger, default=1)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'bank_name': self.bank_name,
            'bank_account': self.bank_account,
            'credit_level': self.credit_level,
            'status': self.status,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Part(db.Model):
    __tablename__ = 'parts'
    id = db.Column(db.Integer, primary_key=True)
    part_no = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    pinyin_code = db.Column(db.String(50))  # 拼音简码
    category_id = db.Column(db.Integer, db.ForeignKey('parts_categories.id'))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(100))
    specification = db.Column(db.String(100))  # 规格型号
    unit = db.Column(db.String(20), default='个')
    purchase_price = db.Column(db.Numeric(10, 2), default=0)
    selling_price = db.Column(db.Numeric(10, 2), default=0)
    network_price = db.Column(db.Numeric(10, 2), default=0)  # 网点价
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=0)
    max_stock = db.Column(db.Integer, default=0)
    safety_stock = db.Column(db.Integer, default=0)  # 安全库存
    min_package_qty = db.Column(db.Integer, default=0)  # 最小包装量
    warehouse = db.Column(db.String(50), default='默认仓库')
    location = db.Column(db.String(50))
    boutique_location = db.Column(db.String(50))  # 精品库房库位
    spare_location = db.Column(db.String(50))  # 备件库库位
    factory_code = db.Column(db.String(50))  # 原厂编码
    origin = db.Column(db.String(50))  # 备件产地
    replaceable_part = db.Column(db.String(100))  # 可替换件
    location_code = db.Column(db.String(50))  # 位置码
    warehouse_location = db.Column(db.String(50))  # 库位编码
    applicable_vehicles = db.Column(db.Text)  # 适用车系，JSON数组
    applicable_vehicle = db.Column(db.String(100))  # 适用车系（单选）
    category1 = db.Column(db.String(50))  # 分类一
    category2 = db.Column(db.String(50))  # 分类二
    discontinued = db.Column(db.Boolean, default=False)  # 停用标记
    archive_remark = db.Column(db.Text)  # 档案备注
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        import json
        vehicles = []
        if self.applicable_vehicles:
            try:
                vehicles = json.loads(self.applicable_vehicles)
            except:
                vehicles = []
        return {
            'id': self.id,
            'part_no': self.part_no,
            'name': self.name,
            'pinyin_code': self.pinyin_code,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'brand': self.brand,
            'model': self.model,
            'specification': self.specification,
            'unit': self.unit,
            'purchase_price': float(self.purchase_price) if self.purchase_price else 0,
            'selling_price': float(self.selling_price) if self.selling_price else 0,
            'network_price': float(self.network_price) if self.network_price else 0,
            'stock_quantity': self.stock_quantity,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'safety_stock': self.safety_stock,
            'min_package_qty': self.min_package_qty,
            'warehouse': self.warehouse,
            'location': self.location,
            'boutique_location': self.boutique_location,
            'spare_location': self.spare_location,
            'factory_code': self.factory_code,
            'origin': self.origin,
            'replaceable_part': self.replaceable_part,
            'location_code': self.location_code,
            'warehouse_location': self.warehouse_location or '',
            'applicable_vehicles': vehicles,
            'applicable_vehicle': self.applicable_vehicle or '',
            'category1': self.category1,
            'category2': self.category2,
            'discontinued': self.discontinued,
            'archive_remark': self.archive_remark,
            'status': self.status,
            'is_low_stock': self.stock_quantity <= self.min_stock if self.min_stock else False,
            'stock_age': (datetime.utcnow() - self.updated_at).days if self.updated_at else 0,
            'latest_inbound_price_with_tax': self._get_latest_inbound_price_with_tax(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def _get_latest_inbound_price_with_tax(self):
        """获取最近一次入库的含税单价"""
        try:
            detail = PartsInboundDetail.query.filter_by(part_id=self.id)\
                .join(PartsInbound, PartsInboundDetail.inbound_id == PartsInbound.id)\
                .filter(PartsInbound.status == 1)\
                .order_by(PartsInboundDetail.created_at.desc())\
                .first()
            if detail and detail.unit_price_with_tax:
                return float(detail.unit_price_with_tax)
            elif detail and detail.unit_price and detail.inbound and detail.inbound.tax_rate:
                rate = 1 + float(detail.inbound.tax_rate) / 100
                return round(float(detail.unit_price) * rate, 2)
            elif detail and detail.unit_price:
                return float(detail.unit_price)
        except Exception:
            pass
        return 0

class PartsInbound(db.Model):
    __tablename__ = 'parts_inbound'
    id = db.Column(db.Integer, primary_key=True)
    inbound_no = db.Column(db.String(30), nullable=False, unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    total_amount = db.Column(db.Numeric(12, 2), default=0)
    total_quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=0)
    inbound_by = db.Column(db.Integer)
    inbound_at = db.Column(db.DateTime)
    remark = db.Column(db.Text)
    invoice_type = db.Column(db.String(10), default='无发票')  # 专票、普票、无发票
    tax_rate = db.Column(db.Numeric(5, 2), default=0)  # 税率
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', backref='inbounds')
    details = db.relationship('PartsInboundDetail', backref='inbound', lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'inbound_no': self.inbound_no,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'total_quantity': self.total_quantity,
            'status': self.status,
            'inbound_by': self.inbound_by,
            'inbound_by_name': _get_user_name(self.inbound_by),
            'inbound_at': self.inbound_at.isoformat() if self.inbound_at else None,
            'remark': self.remark,
            'invoice_type': self.invoice_type or '无发票',
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator_name': _get_user_name(self.created_by)
        }
        if include_details:
            data['details'] = [d.to_dict() for d in self.details.all()]
        return data

class PartsInboundDetail(db.Model):
    __tablename__ = 'parts_inbound_details'
    id = db.Column(db.Integer, primary_key=True)
    inbound_id = db.Column(db.Integer, db.ForeignKey('parts_inbound.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price_with_tax = db.Column(db.Numeric(12, 2), default=0)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    unit = db.Column(db.String(20), default='')
    location = db.Column(db.String(50), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    part = db.relationship('Part')

    def to_dict(self):
        return {
            'id': self.id,
            'inbound_id': self.inbound_id,
            'part_id': self.part_id,
            'part_name': self.part.name if self.part else None,
            'part_no': self.part.part_no if self.part else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'unit_price_with_tax': float(self.unit_price_with_tax) if self.unit_price_with_tax else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'unit': self.unit or '',
            'location': self.location or ''
        }

class PartsOutbound(db.Model):
    __tablename__ = 'parts_outbound'
    id = db.Column(db.Integer, primary_key=True)
    outbound_no = db.Column(db.String(30), nullable=False, unique=True)
    order_id = db.Column(db.Integer)
    outbound_type = db.Column(db.String(20), default='repair')
    total_amount = db.Column(db.Numeric(12, 2), default=0)
    total_quantity = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=0)
    outbound_by = db.Column(db.Integer)
    outbound_at = db.Column(db.DateTime)
    remark = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    details = db.relationship('PartsOutboundDetail', backref='outbound', lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'outbound_no': self.outbound_no,
            'order_id': self.order_id,
            'outbound_type': self.outbound_type,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'total_quantity': self.total_quantity,
            'status': self.status,
            'outbound_by': self.outbound_by,
            'outbound_by_name': _get_user_name(self.outbound_by),
            'outbound_at': self.outbound_at.isoformat() if self.outbound_at else None,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator_name': _get_user_name(self.created_by)
        }
        if include_details:
            data['details'] = [d.to_dict() for d in self.details.all()]
        return data

class PartsOutboundDetail(db.Model):
    __tablename__ = 'parts_outbound_details'
    id = db.Column(db.Integer, primary_key=True)
    outbound_id = db.Column(db.Integer, db.ForeignKey('parts_outbound.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    part = db.relationship('Part')

    def to_dict(self):
        return {
            'id': self.id,
            'outbound_id': self.outbound_id,
            'part_id': self.part_id,
            'part_name': self.part.name if self.part else None,
            'part_no': self.part.part_no if self.part else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0
        }

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)
    reference_type = db.Column(db.String(20))
    reference_id = db.Column(db.Integer)
    quantity_before = db.Column(db.Integer, nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)
    quantity_after = db.Column(db.Integer, nullable=False)
    price_before = db.Column(db.Numeric(10, 2))
    price_after = db.Column(db.Numeric(10, 2))
    operator_id = db.Column(db.Integer)
    remark = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    part = db.relationship('Part')

    def to_dict(self):
        return {
            'id': self.id,
            'part_id': self.part_id,
            'part_name': self.part.name if self.part else None,
            'part_no': self.part.part_no if self.part else None,
            'movement_type': self.movement_type,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'quantity_before': self.quantity_before,
            'quantity_change': self.quantity_change,
            'quantity_after': self.quantity_after,
            'price_before': float(self.price_before) if self.price_before else 0,
            'price_after': float(self.price_after) if self.price_after else 0,
            'operator_id': self.operator_id,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
