from datetime import datetime
from app.extensions import db
from app.models.work_order import WorkOrder, WorkOrderFlowLog, RepairItem, WorkOrderTechnician, WorkOrderPart
from app.models.finance import Payment
from app.models.user import User
from app.utils.helpers import generate_no, generate_order_no

def _get_operator_info(user_id):
    """获取操作人员信息（从用户表直接获取）"""
    user = User.query.get(user_id)
    if not user:
        return {'operator_id': user_id, 'operator_name': '系统', 'operator_no': '', 'operator_dept': ''}
    return {
        'operator_id': user_id,
        'operator_name': user.real_name,
        'operator_no': user.employee_no or '',
        'operator_dept': user.department or ''
    }

class WorkOrderService:
    @staticmethod
    def create_order(data, user_id):
        """创建维修工单"""
        # 处理空字符串：Numeric 字段不接受空字符串
        mileage = data.get('mileage')
        if mileage == '' or mileage is None:
            mileage = 0
        else:
            try:
                mileage = float(mileage)
            except (ValueError, TypeError):
                mileage = 0

        estimated_cost = data.get('estimated_cost')
        if estimated_cost == '' or estimated_cost is None:
            estimated_cost = 0
        else:
            try:
                estimated_cost = float(estimated_cost)
            except (ValueError, TypeError):
                estimated_cost = 0

        order = WorkOrder(
            order_no=generate_order_no(),
            customer_id=data['customer_id'],
            vehicle_id=data['vehicle_id'],
            mileage=mileage,
            service_type=data.get('service_type') or '',
            fault_description=data.get('fault_description') or '',
            repair_suggestion=data.get('repair_suggestion') or '',
            estimated_cost=estimated_cost,
            created_by=user_id
        )
        db.session.add(order)
        db.session.flush()  # 先 flush 以获取 order.id

        # 创建状态流转记录
        op_info = _get_operator_info(user_id)
        flow = WorkOrderFlowLog(
            order_id=order.id,
            from_status=None,
            to_status=0,
            **op_info,
            operation='create',
            remark='创建工单'
        )
        db.session.add(flow)
        db.session.commit()
        return order

    @staticmethod
    def update_status(order_id, new_status, user_id, remark=''):
        """更新工单状态"""
        order = WorkOrder.query.get_or_404(order_id)
        old_status = order.status

        status_field_map = {
            # 简化后只有 0=在修，暂不扩展
        }

        order.status = new_status

        op_info = _get_operator_info(user_id)
        flow = WorkOrderFlowLog(
            order_id=order_id,
            from_status=old_status,
            to_status=new_status,
            **op_info,
            operation=f'status_change_{old_status}_to_{new_status}',
            remark=remark
        )
        db.session.add(flow)
        db.session.commit()
        return order

    @staticmethod
    def calculate_order_cost(order_id):
        """计算工单费用"""
        order = WorkOrder.query.get_or_404(order_id)

        labor_cost = sum(float(item.labor_amount or 0) for item in order.repair_items.all())
        # 从工单备件记录自动汇总配件费
        parts_cost = sum(float(p.total_price or 0) for p in order.order_parts.all())
        # 每行折扣后的实收合计
        labor_actual = sum(float(item.labor_amount or 0) * float(item.discount_rate or 1) for item in order.repair_items.all())
        parts_actual = sum(float(p.total_price or 0) * float(p.discount_rate or 1) for p in order.order_parts.all())

        actual_cost = labor_actual + parts_actual

        order.labor_cost = labor_cost
        order.parts_cost = parts_cost
        order.actual_cost = actual_cost
        order.discount_amount = labor_cost + parts_cost - actual_cost
        order.total_amount = actual_cost

        db.session.commit()
        return order

    @staticmethod
    def add_repair_item(order_id, item_data, user_id):
        """添加维修项目，自动带出关联配件"""
        # 检查项目编码是否重复（同一工单下）
        item_code = item_data.get('item_code', '').strip()
        if item_code:
            existing = RepairItem.query.filter_by(order_id=order_id, item_code=item_code).first()
            if existing:
                raise ValueError(f'项目编码"{item_code}"已存在，不能重复添加')

        # 自动生成项目编码：X + 五位数字（仅当未提供编码时）
        if not item_code:
            max_item = RepairItem.query.filter(RepairItem.item_code.like('X%')).order_by(RepairItem.id.desc()).first()
            if max_item and max_item.item_code and max_item.item_code.startswith('X'):
                try:
                    next_num = int(max_item.item_code[1:]) + 1
                except ValueError:
                    next_num = 1
            else:
                next_num = 1
            item_code = f'X{next_num:05d}'

        item = RepairItem(
            order_id=order_id,
            item_name=item_data['item_name'],
            item_code=item_code,
            category=item_data.get('category'),
            charge_type=item_data.get('charge_type', '自费'),
            repair_category=item_data.get('repair_category', '保养'),
            labor_hours=item_data.get('labor_hours', 0),
            labor_price=item_data.get('labor_price', 0),
            labor_amount=float(item_data.get('labor_hours', 0)) * float(item_data.get('labor_price', 0)),
            technician_id=item_data.get('technician_id'),
            technician_name=item_data.get('technician_name'),
            remark=item_data.get('remark')
        )
        db.session.add(item)
        db.session.flush()  # 获取 item.id

        # 自动带出关联配件
        template_id = item_data.get('template_id')
        auto_parts = []
        if template_id:
            from app.models.work_order import RepairItemTemplatePart
            template_parts = RepairItemTemplatePart.query.filter_by(template_id=template_id).all()
            for tp in template_parts:
                # 检查工单中是否已有该配件
                existing_part = WorkOrderPart.query.filter_by(order_id=order_id, part_id=tp.part_id).first()
                if not existing_part and tp.part and tp.part.stock_quantity >= tp.quantity:
                    unit_price = float(tp.part.selling_price) if tp.part.selling_price else 0
                    op = WorkOrderPart(
                        order_id=order_id,
                        part_id=tp.part_id,
                        repair_item_id=item.id,
                        quantity=tp.quantity,
                        unit_price=unit_price,
                        total_price=round(tp.quantity * unit_price, 2),
                        charge_type=item_data.get('charge_type', '自费'),
                        repair_category=item_data.get('repair_category', '保养'),
                        created_by=user_id
                    )
                    db.session.add(op)
                    # 扣减库存
                    tp.part.stock_quantity = (tp.part.stock_quantity or 0) - tp.quantity
                    auto_parts.append({
                        'part_no': tp.part.part_no,
                        'part_name': tp.part.name,
                        'quantity': tp.quantity
                    })

        db.session.commit()
        # 自动重算工单费用
        WorkOrderService.calculate_order_cost(order_id)
        return item, auto_parts

    @staticmethod
    def assign_technician(order_id, tech_data, user_id):
        """分配维修技师"""
        tech = WorkOrderTechnician(
            order_id=order_id,
            repair_item_id=tech_data.get('repair_item_id'),
            technician_id=tech_data['technician_id'],
            technician_name=tech_data.get('technician_name'),
            assign_type=tech_data.get('assign_type', 'primary'),
            labor_hours=tech_data.get('labor_hours', 0),
            labor_amount=tech_data.get('labor_amount', 0),
            assigned_by=user_id
        )
        db.session.add(tech)
        db.session.commit()
        return tech
