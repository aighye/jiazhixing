from datetime import datetime
from app.extensions import db

def _get_user_name(user_id):
    if not user_id:
        return ''
    from app.models.user import User
    user = User.query.get(user_id)
    return user.real_name if user and user.real_name else (user.username if user else '')

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    payment_no = db.Column(db.String(30), nullable=False, unique=True)
    order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method = db.Column(db.String(20))
    payment_type = db.Column(db.String(20), default='repair')
    transaction_no = db.Column(db.String(50))
    payer_name = db.Column(db.String(50))
    status = db.Column(db.SmallInteger, default=1)
    remark = db.Column(db.Text)
    received_by = db.Column(db.Integer)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    work_order = db.relationship('WorkOrder', backref='payments')
    customer = db.relationship('Customer', backref='payments')

    def to_dict(self):
        return {
            'id': self.id,
            'payment_no': self.payment_no,
            'order_id': self.order_id,
            'order_no': self.work_order.order_no if self.work_order else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'amount': float(self.amount) if self.amount else 0,
            'payment_method': self.payment_method,
            'payment_type': self.payment_type,
            'transaction_no': self.transaction_no,
            'payer_name': self.payer_name,
            'status': self.status,
            'remark': self.remark,
            'received_by': self.received_by,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(30), nullable=False, unique=True)
    order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    customer_id = db.Column(db.Integer)
    invoice_type = db.Column(db.String(20), default='normal')
    title = db.Column(db.String(100), nullable=False)
    tax_no = db.Column(db.String(30))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(12, 2), default=0)
    status = db.Column(db.SmallInteger, default=0)
    issued_by = db.Column(db.Integer)
    issued_at = db.Column(db.DateTime)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    work_order = db.relationship('WorkOrder', backref='invoices')

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_no': self.invoice_no,
            'order_id': self.order_id,
            'invoice_type': self.invoice_type,
            'title': self.title,
            'tax_no': self.tax_no,
            'amount': float(self.amount) if self.amount else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'status': self.status,
            'issued_by': self.issued_by,
            'issued_by_name': _get_user_name(self.issued_by),
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator_name': _get_user_name(self.issued_by)
        }
