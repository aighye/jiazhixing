from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract, cast, Date, String
from datetime import datetime, timedelta, date
from app.extensions import db
from app.models.work_order import WorkOrder
from app.models.customer import Customer
from app.models.parts import Part
from app.models.finance import Payment
from app.models.employee import Employee
from app.models.user import User
from app.models.customer import Appointment
from app.utils.helpers import APIResponse

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """获取仪表盘统计数据"""
    today = datetime.now().date()
    month_start = date(today.year, today.month, 1)

    # 今日数据
    today_orders = WorkOrder.query.filter(
        cast(WorkOrder.created_at, Date) == today
    ).count()

    today_revenue = db.session.query(func.sum(Payment.amount)).filter(
        cast(Payment.received_at, Date) == today,
        Payment.status == 1
    ).scalar() or 0

    # 本月数据
    month_orders = WorkOrder.query.filter(
        WorkOrder.created_at >= datetime.combine(month_start, datetime.min.time()),
        WorkOrder.created_at < datetime.now()
    ).count()

    month_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.received_at >= datetime.combine(month_start, datetime.min.time()),
        Payment.received_at < datetime.now(),
        Payment.status == 1
    ).scalar() or 0

    # 工单状态分布
    status_distribution = db.session.query(
        WorkOrder.status, func.count(WorkOrder.id)
    ).group_by(WorkOrder.status).all()

    # 库存预警
    low_stock_count = Part.query.filter(
        Part.status == 1,
        Part.stock_quantity <= Part.min_stock,
        Part.min_stock > 0
    ).count()

    # 客户总数
    total_customers = Customer.query.filter_by(status=1).count()

    # 员工总数
    total_employees = User.query.filter_by(status=1).count()

    # 近7天营收趋势
    seven_days_ago = today - timedelta(days=6)
    daily_revenue = []
    for i in range(7):
        d = seven_days_ago + timedelta(days=i)
        day_start = datetime.combine(d, datetime.min.time())
        day_end = datetime.combine(d + timedelta(days=1), datetime.min.time())
        revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.received_at >= day_start,
            Payment.received_at < day_end,
            Payment.status == 1
        ).scalar() or 0
        daily_revenue.append({
            'date': d.strftime('%m-%d'),
            'revenue': float(revenue)
        })

    # 最近工单
    recent_orders = WorkOrder.query.order_by(
        WorkOrder.created_at.desc()
    ).limit(10).all()

    return APIResponse.success({
        'today_orders': today_orders,
        'today_revenue': float(today_revenue),
        'month_orders': month_orders,
        'month_revenue': float(month_revenue),
        'status_distribution': {s: c for s, c in status_distribution},
        'low_stock_count': low_stock_count,
        'total_customers': total_customers,
        'total_employees': total_employees,
        'today_appointments': Appointment.query.filter(
            Appointment.appointment_date == today, Appointment.status.in_([0, 1])
        ).count(),
        'pending_appointments': Appointment.query.filter(Appointment.status == 0).count(),
        'daily_revenue': daily_revenue,
        'recent_orders': [o.to_dict() for o in recent_orders]
    })
