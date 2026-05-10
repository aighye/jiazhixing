import uuid
from datetime import datetime, date
from decimal import Decimal

def generate_no(prefix):
    """生成编号"""
    today = datetime.now().strftime('%Y%m%d')
    unique_id = uuid.uuid4().hex[:6].upper()
    return f'{prefix}{today}{unique_id}'

def generate_seq_no(prefix, model, no_field, seq_len=4):
    """生成带日期的顺序编号：prefix + 年月日 + N位顺序号，如 RU202604220001"""
    from app.extensions import db
    today = datetime.now().strftime('%Y%m%d')
    full_prefix = f'{prefix}{today}'
    last = db.session.query(model).filter(
        getattr(model, no_field).like(f'{full_prefix}%')
    ).order_by(getattr(model, no_field).desc()).first()
    seq = 1
    if last:
        last_no = getattr(last, no_field)
        if last_no and last_no.startswith(full_prefix):
            try:
                seq = int(last_no[len(full_prefix):]) + 1
            except ValueError:
                seq = 1
    return f'{full_prefix}{str(seq).zfill(seq_len)}'

def generate_customer_no():
    """生成客户编号：K + 年月日 + 3位顺序号，如 K20260417001"""
    from app.extensions import db
    from app.models.customer import Customer
    today = datetime.now().strftime('%Y%m%d')
    prefix = f'K{today}'
    last = Customer.query.filter(
        Customer.customer_no.like(f'{prefix}%')
    ).order_by(Customer.customer_no.desc()).first()
    if last and last.customer_no.startswith(prefix):
        try:
            seq = int(last.customer_no[9:]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:03d}'

def generate_vehicle_no():
    """生成车辆编号：C + 年月日 + 3位顺序号，如 C20260417001"""
    from app.extensions import db
    from app.models.customer import Vehicle
    today = datetime.now().strftime('%Y%m%d')
    prefix = f'C{today}'
    last = Vehicle.query.filter(
        Vehicle.vehicle_no.like(f'{prefix}%')
    ).order_by(Vehicle.vehicle_no.desc()).first()
    if last and last.vehicle_no.startswith(prefix):
        try:
            seq = int(last.vehicle_no[9:]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:03d}'

def generate_appointment_no():
    """生成预约编号：Y + 年月日 + 4位顺序号，如 Y202604220001"""
    from app.extensions import db
    from app.models.customer import Appointment
    today = datetime.now().strftime('%Y%m%d')
    prefix = f'Y{today}'
    last = Appointment.query.filter(
        Appointment.appointment_no.like(f'{prefix}%')
    ).order_by(Appointment.appointment_no.desc()).first()
    if last and last.appointment_no.startswith(prefix):
        try:
            seq = int(last.appointment_no[9:]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:04d}'

def generate_order_no():
    """生成工单号：G + 年月日 + 4位顺序号，如 G202604170001"""
    from app.extensions import db
    from app.models.work_order import WorkOrder
    today = datetime.now().strftime('%Y%m%d')
    prefix = f'G{today}'
    # 查询当天所有工单号，提取最大序号
    today_orders = WorkOrder.query.filter(
        WorkOrder.order_no.like(f'{prefix}%')
    ).all()
    max_seq = 0
    for o in today_orders:
        try:
            seq_str = o.order_no[len(prefix):]
            seq = int(seq_str)
            if seq > max_seq:
                max_seq = seq
        except (ValueError, IndexError):
            pass
    return f'{prefix}{max_seq + 1:04d}'

def generate_payment_no():
    """生成收款单号：S + 年月日 + 4位顺序号，如 S202604170001"""
    from app.extensions import db
    from app.models.finance import Payment
    today = datetime.now().strftime('%Y%m%d')
    prefix = f'S{today}'
    last_payment = Payment.query.filter(
        Payment.payment_no.like(f'{prefix}%')
    ).order_by(Payment.payment_no.desc()).first()
    if last_payment and last_payment.payment_no.startswith(prefix):
        try:
            seq = int(last_payment.payment_no[9:]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:04d}'

def format_datetime(dt):
    """格式化日期时间"""
    if isinstance(dt, (datetime, date)):
        return dt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(dt, datetime) else dt.strftime('%Y-%m-%d')
    return None

def to_dict(obj):
    """将SQLAlchemy对象转为字典"""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

class APIResponse:
    """统一API响应格式"""
    @staticmethod
    def success(data=None, message='操作成功', code=200):
        return jsonify({
            'code': code,
            'message': message,
            'data': data
        }), code

    @staticmethod
    def error(message='操作失败', code=400, data=None):
        return jsonify({
            'code': code,
            'message': message,
            'data': data
        }), code

from flask import jsonify
