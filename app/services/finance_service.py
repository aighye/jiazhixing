from datetime import datetime, date, timedelta
from app.extensions import db
from app.models.finance import Payment
from app.models.work_order import WorkOrder
from app.utils.helpers import generate_no, generate_payment_no
from sqlalchemy import cast, Date

class FinanceService:
    @staticmethod
    def create_payment(data, user_id):
        """创建收款记录"""
        payment = Payment(
            payment_no=generate_payment_no(),
            order_id=data.get('order_id'),
            customer_id=data.get('customer_id'),
            amount=data['amount'],
            payment_method=data.get('payment_method'),
            payment_type=data.get('payment_type', 'repair'),
            transaction_no=data.get('transaction_no'),
            payer_name=data.get('payer_name'),
            status=1,
            received_by=user_id,
            received_at=datetime.utcnow(),
            remark=data.get('remark')
        )
        db.session.add(payment)

        # 更新工单收款信息
        if data.get('order_id'):
            order = WorkOrder.query.get(data['order_id'])
            if order:
                order.received_amount = (float(order.received_amount or 0) + float(data['amount']))
                if order.received_amount >= float(order.total_amount or 0):
                    order.is_paid = 1

        db.session.commit()
        return payment

    @staticmethod
    def get_daily_summary(date_str):
        """获取每日财务汇总"""
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_start = datetime.combine(d, datetime.min.time())
        day_end = datetime.combine(d + timedelta(days=1), datetime.min.time())
        payments = Payment.query.filter(
            Payment.received_at >= day_start,
            Payment.received_at < day_end,
            Payment.status == 1
        ).all()

        total = sum(float(p.amount or 0) for p in payments)
        by_method = {}
        for p in payments:
            method = p.payment_method or '其他'
            by_method[method] = by_method.get(method, 0) + float(p.amount or 0)

        return {
            'date': date_str,
            'total': total,
            'count': len(payments),
            'by_method': by_method,
            'payments': [p.to_dict() for p in payments]
        }

    @staticmethod
    def get_monthly_summary(year, month):
        """获取每月财务汇总"""
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1)
        else:
            month_end = date(year, month + 1, 1)
        day_start = datetime.combine(month_start, datetime.min.time())
        day_end = datetime.combine(month_end, datetime.min.time())

        payments = Payment.query.filter(
            Payment.received_at >= day_start,
            Payment.received_at < day_end,
            Payment.status == 1
        ).all()

        total = sum(float(p.amount or 0) for p in payments)
        daily = {}
        for p in payments:
            day = p.received_at.strftime('%Y-%m-%d') if p.received_at else ''
            daily[day] = daily.get(day, 0) + float(p.amount or 0)

        return {
            'year': year,
            'month': month,
            'total': total,
            'count': len(payments),
            'daily': daily
        }
