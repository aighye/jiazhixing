from flask import Blueprint, request
from flask_login import login_required, current_user
from app.utils.decorators import permission_required
from sqlalchemy import func
from datetime import datetime, timedelta
from app.extensions import db
from app.models.finance import Payment, Invoice
from app.models.work_order import WorkOrder
from app.models.customer import Customer
from app.services.finance_service import FinanceService
from app.utils.helpers import APIResponse, generate_no

finance_bp = Blueprint('finance', __name__)

# ========== 收款管理 ==========
@finance_bp.route('/payments', methods=['GET'])
@permission_required('finance:read')
def list_payments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    payment_method = request.args.get('payment_method')
    order_status = request.args.get('order_status', type=int)
    pay_status = request.args.get('status', type=int)
    payment_status = request.args.get('payment_status', '').strip()
    keyword = request.args.get('keyword', '').strip()

    # 以收款单为主体查询
    query = Payment.query
    if pay_status is not None:
        query = query.filter(Payment.status == pay_status)
    # 按统一收款状态筛选（基于工单动态状态）
    if payment_status:
        query = query.join(WorkOrder, Payment.order_id == WorkOrder.id)
    if start_date:
        query = query.filter(Payment.received_at >= start_date)
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        query = query.filter(Payment.received_at <= end_datetime)
    if payment_method:
        query = query.filter_by(payment_method=payment_method)
    if order_status is not None:
        query = query.join(WorkOrder, Payment.order_id == WorkOrder.id).filter(WorkOrder.status == order_status)
    if keyword:
        query = query.join(WorkOrder, Payment.order_id == WorkOrder.id).join(
            Customer, WorkOrder.customer_id == Customer.id).filter(
            db.or_(
                WorkOrder.order_no.contains(keyword),
                Customer.name.contains(keyword)
            ))

    pagination = query.order_by(Payment.received_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    items = []
    for p in pagination.items:
        data = p.to_dict()
        # 补充关联的工单信息
        if p.work_order:
            data['order_no'] = p.work_order.order_no
            data['order_status'] = p.work_order.status
            data['order_status_name'] = WorkOrder.STATUS_MAP.get(p.work_order.status, '未知')
            data['order_total'] = float(p.work_order.total_amount or 0)
            # 动态计算工单实际已收金额
            actual_received = sum(
                float(py.amount or 0) for py in p.work_order.payments if py.status in (1, 2)
            )
            data['order_received'] = actual_received
            # 动态计算收款状态（基于工单整体收款情况）
            total = data['order_total']
            if total <= 0:
                data['payment_status'] = '无需收款'
            elif actual_received <= 0:
                data['payment_status'] = '未收款'
            elif actual_received > total:
                data['payment_status'] = '超收'
            elif actual_received >= total:
                data['payment_status'] = '收清'
            else:
                data['payment_status'] = '部分收款'
            data['customer_name'] = p.work_order.customer.name if p.work_order.customer else ''
            data['plate_number'] = p.work_order.vehicle.plate_number if p.work_order.vehicle else ''
        items.append(data)

    return APIResponse.success({
        'items': items,
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@finance_bp.route('/payments', methods=['POST'])
@permission_required('finance:create')
def create_payment():
    data = request.get_json()
    payment = FinanceService.create_payment(data, current_user.id)
    return APIResponse.success(payment.to_dict(), '收款成功')

@finance_bp.route('/payments/<int:id>', methods=['GET'])
@permission_required('finance:read')
def get_payment(id):
    payment = Payment.query.get_or_404(id)
    data = payment.to_dict()
    # 补充关联的工单信息
    if payment.work_order:
        data['order_no'] = payment.work_order.order_no
        data['order_status'] = payment.work_order.status
        data['order_status_name'] = WorkOrder.STATUS_MAP.get(payment.work_order.status, '未知')
        data['order_total'] = float(payment.work_order.total_amount or 0)
        # 动态计算工单实际已收金额（已支付+已退款负值）
        actual_received = sum(
            float(p.amount or 0) for p in payment.work_order.payments
            if p.status in (1, 2)
        )
        data['order_received'] = actual_received
        data['plate_number'] = payment.work_order.vehicle.plate_number if payment.work_order.vehicle else ''
    if payment.customer:
        data['customer_name'] = payment.customer.name if not data.get('customer_name') else data['customer_name']
    # 操作人姓名
    if payment.received_by:
        from app.models.user import User
        u = User.query.get(payment.received_by)
        data['received_by_name'] = u.real_name or u.username if u else ''
    return APIResponse.success(data)


@finance_bp.route('/payments/<int:id>', methods=['PUT'])
@permission_required('finance:create')
def update_payment(id):
    """编辑收款单（仅未支付状态可编辑）"""
    payment = Payment.query.get_or_404(id)
    if payment.status != 0:
        return APIResponse.error('仅未支付的收款单可编辑')
    data = request.get_json()
    if 'amount' in data:
        payment.amount = data['amount']
    if 'payment_method' in data:
        payment.payment_method = data['payment_method']
    if 'payer_name' in data:
        payment.payer_name = data['payer_name']
    if 'remark' in data:
        payment.remark = data['remark']
    db.session.commit()
    return APIResponse.success(payment.to_dict(), '收款单更新成功')


@finance_bp.route('/payments/<int:id>/confirm', methods=['POST'])
@permission_required('finance:create')
def confirm_payment(id):
    """确认收款（未支付→已支付）"""
    payment = Payment.query.get_or_404(id)
    if payment.status != 0:
        return APIResponse.error('仅未支付的收款单可确认收款')
    payment.status = 1
    payment.received_at = datetime.utcnow()
    payment.received_by = current_user.id
    # 更新工单收款信息
    if payment.order_id:
        order = WorkOrder.query.get(payment.order_id)
        if order:
            order.received_amount = (float(order.received_amount or 0) + float(payment.amount))
            if order.received_amount >= float(order.total_amount or 0):
                order.is_paid = 1
    db.session.commit()
    return APIResponse.success(payment.to_dict(), '收款确认成功')

@finance_bp.route('/payments/<int:id>/refund', methods=['POST'])
@permission_required('finance:create')
def refund_payment(id):
    """退款：生成一张负值收款单，原收款单标记为已退款"""
    from app.utils.helpers import generate_no
    payment = Payment.query.get_or_404(id)
    if payment.status != 1:
        return APIResponse.error('仅已支付的收款单可退款')

    # 原收款单标记为已退款
    payment.status = 2

    # 生成负值退款收款单
    refund = Payment(
        payment_no=generate_no('PAY'),
        order_id=payment.order_id,
        customer_id=payment.customer_id,
        amount=-abs(float(payment.amount)),
        payment_method=payment.payment_method,
        payment_type='refund',
        payer_name=payment.payer_name,
        remark=f'退款（原收款单：{payment.payment_no}）',
        status=1,
        received_by=current_user.id,
        received_at=datetime.utcnow()
    )
    db.session.add(refund)

    # 更新工单已收金额
    if payment.order_id:
        order = WorkOrder.query.get(payment.order_id)
        if order:
            order.received_amount = max(0, float(order.received_amount or 0) - abs(float(payment.amount)))
            order.is_paid = 1 if order.received_amount >= float(order.total_amount or 0) else 0

    db.session.commit()
    return APIResponse.success(refund.to_dict(), '退款成功')

# ========== 发票管理 ==========
@finance_bp.route('/invoices', methods=['GET'])
@permission_required('finance:read')
def list_invoices():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Invoice.query.order_by(Invoice.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [i.to_dict() for i in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@finance_bp.route('/invoices', methods=['POST'])
@permission_required('finance:create')
def create_invoice():
    data = request.get_json()

    # 将空字符串转为 None 或默认值（MySQL 的 Numeric/Integer 列不接受空字符串）
    order_id = data.get('order_id')
    if order_id == '' or order_id is None:
        order_id = None
    tax_amount = data.get('tax_amount', 0)
    if tax_amount == '': tax_amount = 0
    amount = data.get('amount')
    if amount == '': amount = 0

    invoice = Invoice(
        invoice_no=generate_no('INV'),
        order_id=order_id,
        customer_id=data.get('customer_id'),
        invoice_type=data.get('invoice_type', 'normal'),
        title=data['title'],
        tax_no=data.get('tax_no') or None,
        amount=amount,
        tax_amount=tax_amount,
        issued_by=current_user.id
    )
    db.session.add(invoice)
    db.session.commit()
    return APIResponse.success(invoice.to_dict(), '发票创建成功')

@finance_bp.route('/invoices/<int:id>/issue', methods=['PUT'])
@permission_required('finance:update')
def issue_invoice(id):
    from datetime import datetime
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 1
    invoice.issued_by = current_user.id
    invoice.issued_at = datetime.utcnow()
    db.session.commit()
    return APIResponse.success(invoice.to_dict(), '发票已开具')

# ========== 财务汇总 ==========
@finance_bp.route('/summary/daily', methods=['GET'])
@permission_required('finance:read')
def daily_summary():
    date_str = request.args.get('date')
    if not date_str:
        from datetime import date
        date_str = date.today().isoformat()
    summary = FinanceService.get_daily_summary(date_str)
    return APIResponse.success(summary)

@finance_bp.route('/summary/monthly', methods=['GET'])
@permission_required('finance:read')
def monthly_summary():
    from datetime import date
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    summary = FinanceService.get_monthly_summary(year, month)
    return APIResponse.success(summary)
