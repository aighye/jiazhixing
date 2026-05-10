from flask import Blueprint, request
from flask_login import login_required
from app.utils.decorators import permission_required
from sqlalchemy import func, extract, cast, Date, desc
from datetime import datetime, timedelta, date
from app.extensions import db
from app.models.work_order import WorkOrder, _get_user_name
from app.models.finance import Payment
from app.models.customer import Customer
from app.models.parts import Part
from app.utils.helpers import APIResponse

report_bp = Blueprint('report', __name__)

@report_bp.route('/revenue', methods=['GET'])
@permission_required('report:read')
def revenue_report():
    """营收报表"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Payment.query.filter_by(status=1)
    if start_date:
        query = query.filter(Payment.received_at >= start_date)
    if end_date:
        from datetime import datetime as dt
        end_datetime = dt.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        query = query.filter(Payment.received_at <= end_datetime)

    payments = query.all()
    total = sum(float(p.amount or 0) for p in payments)

    by_method = {}
    by_type = {}
    for p in payments:
        method = p.payment_method or '其他'
        by_method[method] = by_method.get(method, 0) + float(p.amount or 0)
        ptype = p.payment_type or '其他'
        by_type[ptype] = by_type.get(ptype, 0) + float(p.amount or 0)

    return APIResponse.success({
        'total': total,
        'count': len(payments),
        'by_method': by_method,
        'by_type': by_type
    })

@report_bp.route('/work-orders', methods=['GET'])
@permission_required('report:read')
def work_order_report():
    """工单统计报表"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = WorkOrder.query
    if start_date:
        query = query.filter(WorkOrder.created_at >= start_date)
    if end_date:
        from datetime import datetime as dt
        end_datetime = dt.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        query = query.filter(WorkOrder.created_at <= end_datetime)

    orders = query.all()
    total = len(orders)

    by_status = {}
    by_type = {}
    total_revenue = 0
    for o in orders:
        status_name = WorkOrder.STATUS_MAP.get(o.status, '未知')
        by_status[status_name] = by_status.get(status_name, 0) + 1
        stype = o.service_type or '其他'
        by_type[stype] = by_type.get(stype, 0) + 1
        total_revenue += float(o.total_amount or 0)

    return APIResponse.success({
        'total': total,
        'by_status': by_status,
        'by_type': by_type,
        'total_revenue': total_revenue
    })

@report_bp.route('/inventory', methods=['GET'])
@permission_required('report:read')
def inventory_report():
    """库存报表"""
    total_parts = Part.query.filter_by(status=1).count()
    total_value = db.session.query(
        func.sum(Part.stock_quantity * Part.purchase_price)
    ).filter(Part.status == 1).scalar() or 0

    low_stock_parts = Part.query.filter(
        Part.status == 1,
        Part.stock_quantity <= Part.min_stock,
        Part.min_stock > 0
    ).all()

    by_category = db.session.query(
        Part.category_id, func.count(Part.id), func.sum(Part.stock_quantity)
    ).filter(Part.status == 1).group_by(Part.category_id).all()

    return APIResponse.success({
        'total_parts': total_parts,
        'total_value': float(total_value),
        'low_stock_count': len(low_stock_parts),
        'low_stock_parts': [p.to_dict() for p in low_stock_parts],
        'by_category': [{'category_id': c, 'count': cnt, 'stock': int(s or 0)} for c, cnt, s in by_category]
    })

@report_bp.route('/customer', methods=['GET'])
@permission_required('report:read')
def customer_report():
    """客户统计报表"""
    total = Customer.query.filter_by(status=1).count()
    month_start = date(datetime.now().year, datetime.now().month, 1)
    new_this_month = Customer.query.filter(
        Customer.status == 1,
        Customer.created_at >= datetime.combine(month_start, datetime.min.time()),
        Customer.created_at < datetime.now()
    ).count()

    by_vip = db.session.query(
        Customer.vip_level, func.count(Customer.id)
    ).filter(Customer.status == 1).group_by(Customer.vip_level).all()

    return APIResponse.success({
        'total': total,
        'new_this_month': new_this_month,
        'by_vip': {f'VIP{v}': c for v, c in by_vip}
    })

@report_bp.route('/daily', methods=['GET'])
@permission_required('report:read')
def daily_report():
    """工单日报"""
    target_date = request.args.get('date')
    if not target_date:
        target_date = date.today().isoformat()

    # 查询指定日期的工单
    day_start = datetime.strptime(target_date, '%Y-%m-%d')
    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)

    orders = WorkOrder.query.filter(
        WorkOrder.created_at >= day_start,
        WorkOrder.created_at <= day_end
    ).order_by(desc(WorkOrder.created_at)).all()

    # 按状态统计
    status_count = {}
    total_amount = 0
    total_received = 0
    for o in orders:
        sn = WorkOrder.STATUS_MAP.get(o.status, '未知')
        status_count[sn] = status_count.get(sn, 0) + 1
        total_amount += float(o.total_amount or 0)
        total_received += float(o.received_amount or 0)

    # 工单列表
    items = []
    for o in orders:
        items.append({
            'id': o.id,
            'order_no': o.order_no,
            'customer_name': o.customer.name if o.customer else '',
            'plate_number': o.vehicle.plate_number if o.vehicle else '',
            'vehicle_model': f"{o.vehicle.brand or ''} {o.vehicle.model or ''}".strip() if o.vehicle else '',
            'service_type': o.service_type or '',
            'status': o.status,
            'status_name': WorkOrder.STATUS_MAP.get(o.status, '未知'),
            'total_amount': float(o.total_amount or 0),
            'received_amount': float(o.received_amount or 0),
            'is_paid': o.is_paid,
            'created_at': o.created_at.isoformat() if o.created_at else '',
            'creator_name': _get_user_name(o.created_by)
        })

    return APIResponse.success({
        'date': target_date,
        'total_orders': len(orders),
        'status_count': status_count,
        'total_amount': total_amount,
        'total_received': total_received,
        'items': items
    })
