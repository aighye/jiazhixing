from datetime import datetime
from app.extensions import db

def _get_user_name(user_id):
    if not user_id:
        return ''
    from app.models.user import User
    user = User.query.get(user_id)
    return user.real_name if user and user.real_name else (user.username if user else '')

class WorkOrder(db.Model):
    __tablename__ = 'work_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(30), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    mileage = db.Column(db.Integer)
    status = db.Column(db.SmallInteger, default=0)
    service_type = db.Column(db.String(50))
    fault_description = db.Column(db.Text)
    repair_suggestion = db.Column(db.Text)
    estimated_cost = db.Column(db.Numeric(10, 2), default=0)
    actual_cost = db.Column(db.Numeric(10, 2), default=0)
    parts_cost = db.Column(db.Numeric(10, 2), default=0)
    labor_cost = db.Column(db.Numeric(10, 2), default=0)
    other_cost = db.Column(db.Numeric(10, 2), default=0)
    discount_rate = db.Column(db.Numeric(4, 2), default=1)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    received_amount = db.Column(db.Numeric(10, 2), default=0)
    is_paid = db.Column(db.SmallInteger, default=0)
    repair_confirmed = db.Column(db.SmallInteger, default=0)          # 在修确认完成(并行步骤)
    parts_outbound_confirmed = db.Column(db.SmallInteger, default=0) # 备件出库确认完成(并行步骤)
    created_by = db.Column(db.Integer)
    confirmed_by = db.Column(db.Integer)
    confirmed_at = db.Column(db.DateTime)
    assigned_by = db.Column(db.Integer)
    assigned_at = db.Column(db.DateTime)
    inspected_by = db.Column(db.Integer)
    inspected_at = db.Column(db.DateTime)
    completed_by = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime)
    settled_by = db.Column(db.Integer)
    settled_at = db.Column(db.DateTime)
    delivery_at = db.Column(db.DateTime)
    remark = db.Column(db.Text)
    claim_manufacturer = db.Column(db.String(50))
    insurance_company = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = db.relationship('Customer', backref='work_orders')
    vehicle = db.relationship('Vehicle', backref='work_orders')
    repair_items = db.relationship('RepairItem', backref='work_order', lazy='dynamic',
                                    cascade='all, delete-orphan')
    order_parts = db.relationship('WorkOrderPart', backref='work_order', lazy='dynamic',
                                  cascade='all, delete-orphan')
    technicians = db.relationship('WorkOrderTechnician', backref='work_order', lazy='dynamic',
                                   cascade='all, delete-orphan')
    flow_logs = db.relationship('WorkOrderFlowLog', backref='work_order', lazy='dynamic',
                                 cascade='all, delete-orphan')

    STATUS_MAP = {
        0: '在修',
        1: '结算'
    }

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'order_no': self.order_no,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'customer_phone': self.customer.phone if self.customer else None,
            'vehicle_id': self.vehicle_id,
            'plate_number': self.vehicle.plate_number if self.vehicle else None,
            'vehicle_brand': self.vehicle.brand if self.vehicle else None,
            'vehicle_model': self.vehicle.model if self.vehicle else None,
            'mileage': self.mileage,
            'status': self.status,
            'status_name': self.STATUS_MAP.get(self.status, '未知'),
            'service_type': self.service_type,
            'fault_description': self.fault_description,
            'repair_suggestion': self.repair_suggestion,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else 0,
            'actual_cost': float(self.actual_cost) if self.actual_cost else 0,
            'parts_cost': float(self.parts_cost) if self.parts_cost else 0,
            'labor_cost': float(self.labor_cost) if self.labor_cost else 0,
            'other_cost': float(self.other_cost) if self.other_cost else 0,
            'discount_rate': float(self.discount_rate) if self.discount_rate else 1,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'received_amount': float(self.received_amount) if self.received_amount else 0,
            'is_paid': self.is_paid,
            'repair_confirmed': self.repair_confirmed,
            'parts_outbound_confirmed': self.parts_outbound_confirmed,
            'remark': self.remark,
            'claim_manufacturer': self.claim_manufacturer,
            'insurance_company': self.insurance_company,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'creator_name': _get_user_name(self.created_by)
        }
        # 动态计算收款状态（基于收款记录）
        total_amount = float(self.total_amount) if self.total_amount else 0
        actual_received = sum(
            float(p.amount or 0) for p in self.payments if p.status in (1, 2)
        )
        if total_amount <= 0:
            data['payment_status'] = '无需收款'
        elif actual_received <= 0:
            data['payment_status'] = '未收款'
        elif actual_received > total_amount:
            data['payment_status'] = '超收'
        elif actual_received >= total_amount:
            data['payment_status'] = '收清'
        else:
            data['payment_status'] = '部分收款'
        data['actual_received'] = actual_received

        # 配件出库统计
        all_parts = list(self.order_parts.all())
        total_parts = len(all_parts)
        outbound_parts = sum(1 for p in all_parts if p.outbound_status == 1)
        data['parts_total'] = total_parts
        data['parts_outbound_count'] = outbound_parts
        if total_parts == 0:
            data['parts_outbound_status'] = 'no_parts'
        elif outbound_parts == total_parts:
            data['parts_outbound_status'] = 'all'
        elif outbound_parts > 0:
            data['parts_outbound_status'] = 'partial'
        else:
            data['parts_outbound_status'] = 'none_outbound'
        if include_details:
            data['repair_items'] = [item.to_dict() for item in self.repair_items.all()]
            data['order_parts'] = [p.to_dict() for p in self.order_parts.all()]
            data['technicians'] = [t.to_dict() for t in self.technicians.all()]
            data['flow_logs'] = [log.to_dict() for log in self.flow_logs.order_by(WorkOrderFlowLog.created_at).all()]
            data['payments'] = [p.to_dict() for p in sorted(
                self.payments,
                key=lambda x: x.created_at, reverse=True
            )]
            data['invoices'] = [inv.to_dict() for inv in sorted(
                self.invoices, key=lambda x: x.created_at or datetime.min, reverse=True
            )]
        return data

class WorkOrderFlowLog(db.Model):
    __tablename__ = 'work_order_flow_logs'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    from_status = db.Column(db.SmallInteger)
    to_status = db.Column(db.SmallInteger, nullable=False)
    operator_id = db.Column(db.Integer)
    operator_name = db.Column(db.String(50))
    operator_no = db.Column(db.String(30))
    operator_dept = db.Column(db.String(50))
    operation = db.Column(db.String(50))
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'operator_id': self.operator_id,
            'operator_name': self.operator_name,
            'operator_no': self.operator_no,
            'operator_dept': self.operator_dept,
            'operation': self.operation,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RepairItemTemplate(db.Model):
    """维修项目模板 - 标准维修项目基础数据，用于快速创建工单维修项目"""
    __tablename__ = 'repair_item_templates'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_code = db.Column(db.String(50))
    category = db.Column(db.String(50))
    charge_type = db.Column(db.String(20))
    repair_category = db.Column(db.String(20))
    labor_hours = db.Column(db.Numeric(6, 2), default=0)
    labor_price = db.Column(db.Numeric(10, 2), default=0)
    description = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=1)  # 1:启用 0:停用
    sort_order = db.Column(db.Integer, default=0)
    remark = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'item_code': self.item_code,
            'category': self.category,
            'charge_type': self.charge_type,
            'repair_category': self.repair_category,
            'labor_hours': float(self.labor_hours) if self.labor_hours else 0,
            'labor_price': float(self.labor_price) if self.labor_price else 0,
            'labor_amount': float(self.labor_hours or 0) * float(self.labor_price or 0),
            'description': self.description,
            'status': self.status,
            'status_name': '启用' if self.status == 1 else '停用',
            'sort_order': self.sort_order,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'parts': [p.to_dict() for p in self.template_parts]
        }

class RepairItemTemplatePart(db.Model):
    """维修项目模板-配件关联"""
    __tablename__ = 'repair_item_template_parts'
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('repair_item_templates.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    part = db.relationship('Part')
    template = db.relationship('RepairItemTemplate', backref='template_parts')

    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'part_id': self.part_id,
            'part_no': self.part.part_no if self.part else '',
            'part_name': self.part.name if self.part else '',
            'unit': self.part.unit if self.part else '',
            'brand': self.part.brand if self.part else '',
            'specification': self.part.specification if self.part else '',
            'selling_price': float(self.part.selling_price) if self.part and self.part.selling_price else 0,
            'quantity': self.quantity,
            'sort_order': self.sort_order
        }

class RepairItem(db.Model):
    __tablename__ = 'repair_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    item_code = db.Column(db.String(50))
    category = db.Column(db.String(50))
    charge_type = db.Column(db.String(20))
    repair_category = db.Column(db.String(20))
    labor_hours = db.Column(db.Numeric(6, 2), default=0)
    labor_price = db.Column(db.Numeric(10, 2), default=0)
    labor_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_rate = db.Column(db.Numeric(4, 2), default=1)
    technician_id = db.Column(db.Integer)
    technician_name = db.Column(db.String(50))
    status = db.Column(db.SmallInteger, default=0)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'item_name': self.item_name,
            'item_code': self.item_code,
            'category': self.category,
            'charge_type': self.charge_type,
            'repair_category': self.repair_category,
            'labor_hours': float(self.labor_hours) if self.labor_hours else 0,
            'labor_price': float(self.labor_price) if self.labor_price else 0,
            'labor_amount': float(self.labor_amount) if self.labor_amount else 0,
            'discount_rate': float(self.discount_rate) if self.discount_rate else 1,
            'actual_amount': float(self.labor_amount or 0) * float(self.discount_rate or 1),
            'technician_id': self.technician_id,
            'technician_name': self.technician_name,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'remark': self.remark
        }

class WorkOrderTechnician(db.Model):
    __tablename__ = 'work_order_technicians'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    repair_item_id = db.Column(db.Integer)
    technician_id = db.Column(db.Integer, nullable=False)
    technician_name = db.Column(db.String(50))
    assign_type = db.Column(db.String(20), default='primary')
    labor_hours = db.Column(db.Numeric(6, 2), default=0)
    labor_amount = db.Column(db.Numeric(10, 2), default=0)
    assigned_by = db.Column(db.Integer)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.SmallInteger, default=0)
    completed_at = db.Column(db.DateTime)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'repair_item_id': self.repair_item_id,
            'technician_id': self.technician_id,
            'technician_name': self.technician_name,
            'assign_type': self.assign_type,
            'labor_hours': float(self.labor_hours) if self.labor_hours else 0,
            'labor_amount': float(self.labor_amount) if self.labor_amount else 0,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'remark': self.remark
        }


class WorkOrderPart(db.Model):
    """工单备件使用记录 - 记录工单维修过程中使用的配件"""
    __tablename__ = 'work_order_parts'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    repair_item_id = db.Column(db.Integer, db.ForeignKey('repair_items.id'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), default=0)       # 销售单价
    total_price = db.Column(db.Numeric(10, 2), default=0)      # 小计 = quantity * unit_price
    discount_rate = db.Column(db.Numeric(4, 2), default=1)
    charge_type = db.Column(db.String(20))
    repair_category = db.Column(db.String(20))
    remark = db.Column(db.Text)
    outbound_status = db.Column(db.SmallInteger, default=0)  # 出库状态：0未出库 1已出库 2部分出库
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    part = db.relationship('Part', backref='order_parts')
    repair_item = db.relationship('RepairItem', backref='order_parts')

    def to_dict(self):
        # 成本单价：不含税取 part.purchase_price，含税取最近入库含税加权平均价
        cost_price_no_tax = 0
        cost_price_with_tax = 0
        if self.part:
            cost_price_no_tax = float(self.part.purchase_price) if self.part.purchase_price else 0
            cost_price_with_tax = self.part._get_latest_inbound_price_with_tax()
        qty = self.quantity or 1
        return {
            'id': self.id,
            'order_id': self.order_id,
            'part_id': self.part_id,
            'part_no': self.part.part_no if self.part else None,
            'part_name': self.part.name if self.part else None,
            'part_brand': self.part.brand if self.part else None,
            'part_model': self.part.model if self.part else None,
            'part_specification': self.part.specification if self.part else None,
            'part_unit': self.part.unit if self.part else '个',
            'repair_item_id': self.repair_item_id,
            'quantity': qty,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'discount_rate': float(self.discount_rate) if self.discount_rate else 1,
            'actual_amount': float(self.total_price or 0) * float(self.discount_rate or 1),
            'cost_price_no_tax': cost_price_no_tax,
            'cost_total_no_tax': round(cost_price_no_tax * qty, 2),
            'cost_price_with_tax': cost_price_with_tax,
            'cost_total_with_tax': round(cost_price_with_tax * qty, 2),
            'charge_type': self.charge_type,
            'repair_category': self.repair_category,
            'outbound_status': self.outbound_status or 0,
            'remark': self.remark,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
