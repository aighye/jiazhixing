from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.extensions import db
from app.models.work_order import WorkOrder, RepairItem, WorkOrderTechnician, WorkOrderPart
from app.models.parts import Part, StockMovement
from app.services.work_order_service import WorkOrderService
from app.utils.helpers import APIResponse
from app.utils.decorators import permission_required
from datetime import datetime, timedelta

work_order_bp = Blueprint('work_order', __name__)

# 允许操作备件的工单状态：在修(0)
PART_EDITABLE_STATUSES = [0]


@work_order_bp.route('/list', methods=['GET'])
@login_required
@permission_required('work_order:read')
def list_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = WorkOrder.query
    if keyword:
        query = query.filter(or_(
            WorkOrder.order_no.like(f'%{keyword}%'),
            WorkOrder.plate_number.like(f'%{keyword}%')
        ))
    if status is not None:
        query = query.filter_by(status=status)
    is_paid = request.args.get('is_paid', type=int)
    if is_paid is not None:
        query = query.filter_by(is_paid=is_paid)
    if start_date:
        query = query.filter(WorkOrder.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(WorkOrder.created_at <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))

    pagination = query.order_by(WorkOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@work_order_bp.route('/<int:id>', methods=['GET'])
@login_required
@permission_required('work_order:read')
def get_order(id):
    order = WorkOrder.query.get_or_404(id)
    return APIResponse.success(order.to_dict(include_details=True))


@work_order_bp.route('/<int:id>', methods=['PUT'])
@login_required
@permission_required('work_order:update')
def update_order(id):
    """更新工单基本信息"""
    order = WorkOrder.query.get_or_404(id)
    data = request.get_json()

    # 仅允许在新建状态(0)下编辑基本信息
    if order.status != 0:
        return APIResponse.error('当前工单状态不允许编辑基本信息')

    # 需要将空字符串转为 None 或 0 的数值字段
    num_fields = ['mileage']

    for field in ['service_type', 'mileage', 'fault_description', 'repair_suggestion',
                  'remark', 'other_cost']:
        if field in data:
            val = data[field]
            # 将空字符串转为 None 或 0（MySQL 的 INT/Numeric 列不接受空字符串）
            if val == '' and field in num_fields:
                val = 0
            setattr(order, field, val)

    db.session.commit()

    # 如果修改了其他费用，重新计算总费用
    if 'other_cost' in data:
        WorkOrderService.calculate_order_cost(id)

    return APIResponse.success(order.to_dict(), '工单信息已更新')


@work_order_bp.route('', methods=['POST'])
@login_required
@permission_required('work_order:create')
def create_order():
    data = request.get_json()
    order = WorkOrderService.create_order(data, current_user.id)
    return APIResponse.success(order.to_dict(), '工单创建成功')


@work_order_bp.route('/<int:id>/status', methods=['PUT'])
@login_required
@permission_required('work_order:status')
def update_status(id):
    data = request.get_json()
    new_status = data.get('status')
    remark = data.get('remark', '')

    try:
        order = WorkOrderService.update_status(id, new_status, current_user.id, remark)
    except ValueError as e:
        return APIResponse.error(str(e))
    return APIResponse.success(order.to_dict(), '状态更新成功')


@work_order_bp.route('/<int:id>/submit-payment', methods=['POST'])
@login_required
@permission_required('work_order:settle')
def submit_payment(id):
    """在修提交收款：生成待确认收款单，不改变工单状态"""
    from app.models.finance import Payment
    from app.utils.helpers import generate_no
    order = WorkOrder.query.get_or_404(id)
    if order.status != 0:
        return APIResponse.error('当前工单状态不允许提交收款')

    # 校验保险/索赔必填字段
    from app.models.work_order import RepairItem, WorkOrderPart
    has_insurance = RepairItem.query.filter_by(order_id=id, charge_type='保险').first() or \
                    WorkOrderPart.query.filter_by(order_id=id, charge_type='保险').first()
    has_claim = RepairItem.query.filter_by(order_id=id, charge_type='索赔').first() or \
                WorkOrderPart.query.filter_by(order_id=id, charge_type='索赔').first()
    if has_insurance and not order.insurance_company:
        return APIResponse.error('本单有保险，必须填写具体保险公司！')
    if has_claim and not order.claim_manufacturer:
        return APIResponse.error('本单有索赔，必须填写具体索赔厂家！')

    total_amount = float(order.total_amount or 0)
    unpaid_amount = max(0, total_amount - float(order.received_amount or 0))

    payment = Payment(
        payment_no=generate_no('PAY'),
        order_id=order.id,
        customer_id=order.customer_id,
        amount=unpaid_amount,
        payment_method='cash',
        payment_type='repair',
        payer_name=order.customer.name if order.customer else '',
        status=0,  # 0=待确认
        received_by=current_user.id
    )
    db.session.add(payment)
    order.status = 1  # 结算
    order.settled_by = current_user.id
    order.settled_at = datetime.utcnow()
    # 记录状态流转
    from app.models.work_order import WorkOrderFlowLog
    flow = WorkOrderFlowLog(
        order_id=order.id,
        from_status=0,
        to_status=1,
        operator_id=current_user.id,
        operator_name=current_user.real_name or current_user.username,
        operation='status_change_0_to_1',
        remark='提交收款，工单结算'
    )
    db.session.add(flow)
    db.session.commit()
    return APIResponse.success(payment.to_dict(), '收款单已提交，工单状态已变更为结算')


@work_order_bp.route('/<int:id>/items', methods=['POST'])
@login_required
@permission_required('work_order:repair')
def add_repair_item(id):
    data = request.get_json()
    try:
        item, auto_parts = WorkOrderService.add_repair_item(id, data, current_user.id)
    except ValueError as e:
        return APIResponse.error(str(e))
    return APIResponse.success({
        'item': item.to_dict(),
        'auto_parts': auto_parts
    }, '维修项目添加成功')


@work_order_bp.route('/<int:id>/items/<int:item_id>', methods=['PUT'])
@login_required
@permission_required('work_order:repair')
def update_repair_item(id, item_id):
    item = RepairItem.query.get_or_404(item_id)
    data = request.get_json()

    # 需要将空字符串转为 None 或 0 的数值字段
    num_fields = ['labor_hours', 'labor_price', 'discount_rate', 'technician_id', 'status']

    for field in ['item_name', 'item_code', 'category', 'charge_type', 'repair_category',
                  'labor_hours', 'labor_price', 'discount_rate',
                  'technician_id', 'technician_name', 'status', 'remark']:
        if field in data:
            val = data[field]
            # 将空字符串转为 None 或 0（MySQL 的 INT/Numeric 列不接受空字符串）
            if val == '' and field in num_fields:
                val = 0
            setattr(item, field, val)

    if 'labor_hours' in data and 'labor_price' in data:
        item.labor_amount = float(data['labor_hours']) * float(data['labor_price'])

    if 'discount_rate' in data:
        item.labor_amount = float(item.labor_hours or 0) * float(item.labor_price or 0)

    db.session.commit()

    # 自动重算工单费用
    WorkOrderService.calculate_order_cost(id)
    db.session.commit()

    return APIResponse.success(item.to_dict(), '维修项目更新成功')


@work_order_bp.route('/<int:id>/items/<int:item_id>', methods=['DELETE'])
@login_required
@permission_required('work_order:repair')
def delete_repair_item(id, item_id):
    item = RepairItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    # 自动重算工单费用
    WorkOrderService.calculate_order_cost(id)
    return APIResponse.success(message='维修项目已删除')


@work_order_bp.route('/<int:id>/technicians', methods=['POST'])
@login_required
@permission_required('work_order:repair')
def assign_technician(id):
    data = request.get_json()
    tech = WorkOrderService.assign_technician(id, data, current_user.id)
    return APIResponse.success(tech.to_dict(), '技师分配成功')


@work_order_bp.route('/<int:id>/calculate', methods=['POST'])
@login_required
@permission_required('work_order:settle')
def calculate_cost(id):
    order = WorkOrderService.calculate_order_cost(id)
    return APIResponse.success(order.to_dict(), '费用计算完成')


@work_order_bp.route('/<int:id>/discount', methods=['PUT'])
@login_required
@permission_required('work_order:settle')
def update_discount(id):
    order = WorkOrder.query.get_or_404(id)
    data = request.get_json()
    if 'discount_rate' in data:
        order.discount_rate = data['discount_rate']
    if 'other_cost' in data:
        order.other_cost = data['other_cost']
    if 'claim_manufacturer' in data:
        order.claim_manufacturer = data['claim_manufacturer']
    if 'insurance_company' in data:
        order.insurance_company = data['insurance_company']
    WorkOrderService.calculate_order_cost(id)
    return APIResponse.success(order.to_dict(), '费用更新成功')


@work_order_bp.route('/<int:id>/field', methods=['PUT'])
@login_required
@permission_required('work_order:edit')
def update_order_field(id):
    """更新工单单个字段（索赔厂家、保险公司等，在修步骤可用）"""
    order = WorkOrder.query.get_or_404(id)
    data = request.get_json()
    allowed_fields = ['claim_manufacturer', 'insurance_company']
    for field in allowed_fields:
        if field in data:
            setattr(order, field, data[field])
    db.session.commit()
    return APIResponse.success(order.to_dict(), '更新成功')


# ==================== 工单备件管理 ====================

@work_order_bp.route('/<int:id>/parts', methods=['GET'])
@login_required
@permission_required('work_order:parts')
def get_order_parts(id):
    """获取工单的备件列表"""
    order = WorkOrder.query.get_or_404(id)
    parts = order.order_parts.all()
    # 计算备件总费用
    total = sum(float(p.total_price or 0) for p in parts)
    return APIResponse.success({
        'items': [p.to_dict() for p in parts],
        'total': total,
        'can_edit': order.status in PART_EDITABLE_STATUSES
    })


@work_order_bp.route('/<int:id>/parts', methods=['POST'])
@login_required
@permission_required('work_order:parts')
def add_order_part(id):
    """为工单添加备件"""
    order = WorkOrder.query.get_or_404(id)

    # 检查工单状态是否允许操作备件
    if order.status not in PART_EDITABLE_STATUSES:
        return APIResponse.error(f'当前工单状态({order.STATUS_MAP.get(order.status)})不允许操作备件，仅限在修状态')

    data = request.get_json()
    part_id = data.get('part_id')
    quantity = data.get('quantity', 1)
    repair_item_id = data.get('repair_item_id')
    remark = data.get('remark', '')

    if not part_id:
        return APIResponse.error('请选择配件')
    if quantity < 1:
        return APIResponse.error('数量不能小于1')

    part = Part.query.get(part_id)
    if not part:
        return APIResponse.error('配件不存在')

    # 检查是否已添加过该配件（同工单下配件编号唯一）
    existing = WorkOrderPart.query.filter_by(
        order_id=id, part_id=part_id
    ).first()

    if existing:
        return APIResponse.error(f'配件"{part.part_no or part.name}"已添加过，不能重复添加')

    # 新增备件记录
    unit_price = float(data.get('unit_price') or part.selling_price or 0)
    total_price = quantity * unit_price

    order_part = WorkOrderPart(
        order_id=id,
        part_id=part_id,
        repair_item_id=repair_item_id,
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
        charge_type='自费',
        repair_category='保养',
        remark=remark,
        created_by=current_user.id
    )
    db.session.add(order_part)
    db.session.commit()

    # 重新计算工单费用
    WorkOrderService.calculate_order_cost(id)
    return APIResponse.success(order_part.to_dict(), f'备件"{part.name}"已添加')


@work_order_bp.route('/<int:id>/parts/<int:op_id>', methods=['PUT'])
@login_required
@permission_required('work_order:parts')
def update_order_part(id, op_id):
    """修改工单备件数量"""
    order = WorkOrder.query.get_or_404(id)

    if order.status not in PART_EDITABLE_STATUSES:
        return APIResponse.error(f'当前工单状态({order.STATUS_MAP.get(order.status)})不允许操作备件')

    order_part = WorkOrderPart.query.get_or_404(op_id)
    if order_part.order_id != id:
        return APIResponse.error('备件记录不属于该工单')

    data = request.get_json()
    new_quantity = data.get('quantity')

    if new_quantity is not None:
        if new_quantity < 0:
            return APIResponse.error('数量不能为负数')

        if new_quantity == 0:
            part = Part.query.get(order_part.part_id)
            return _remove_order_part(order, order_part, part, current_user.id)

        order_part.quantity = new_quantity
        part = Part.query.get(order_part.part_id)
        if part:
            order_part.unit_price = float(data.get('unit_price') or part.selling_price or 0)
        order_part.total_price = new_quantity * order_part.unit_price

    # 更新其他字段（折扣率、收费类型、维修类别等）
    if 'discount_rate' in data:
        order_part.discount_rate = data['discount_rate']
    if 'charge_type' in data:
        order_part.charge_type = data['charge_type']
    if 'repair_category' in data:
        order_part.repair_category = data['repair_category']
    db.session.commit()

    # 重新计算工单费用
    WorkOrderService.calculate_order_cost(id)
    return APIResponse.success(order_part.to_dict(), f'备件数量已更新为{new_quantity}')


@work_order_bp.route('/<int:id>/parts/<int:op_id>', methods=['DELETE'])
@login_required
@permission_required('work_order:parts')
def remove_order_part(id, op_id):
    """删除工单备件（回退库存）"""
    order = WorkOrder.query.get_or_404(id)

    if order.status not in PART_EDITABLE_STATUSES:
        return APIResponse.error(f'当前工单状态({order.STATUS_MAP.get(order.status)})不允许操作备件')

    order_part = WorkOrderPart.query.get_or_404(op_id)
    if order_part.order_id != id:
        return APIResponse.error('备件记录不属于该工单')

    part = Part.query.get(order_part.part_id)
    result = _remove_order_part(order, order_part, part, current_user.id)
    return result


@work_order_bp.route('/<int:id>/parts/<int:op_id>/outbound', methods=['PUT'])
@login_required
def outbound_order_part(id, op_id):
    """确认工单备件出库"""
    order = WorkOrder.query.get_or_404(id)
    if order.status != 0:
        return APIResponse.error('当前工单状态不允许操作备件出库')

    order_part = WorkOrderPart.query.get_or_404(op_id)
    if order_part.order_id != id:
        return APIResponse.error('备件记录不属于该工单')

    order_part.outbound_status = 1

    # 出库时扣减库存并记录变动
    part = Part.query.get(order_part.part_id)
    if part:
        old_stock = part.stock_quantity
        out_qty = order_part.quantity
        if old_stock < out_qty:
            return APIResponse.error(f'配件"{part.name}"库存不足，当前库存: {old_stock}，需要: {out_qty}')
        part.stock_quantity = old_stock - out_qty
        movement = StockMovement(
            part_id=part.id,
            movement_type='out',
            reference_type='wo_part_out',
            reference_id=order_part.id,
            quantity_before=old_stock,
            quantity_change=-out_qty,
            quantity_after=old_stock - out_qty,
            price_before=float(part.purchase_price or 0),
            price_after=float(part.purchase_price or 0),
            operator_id=current_user.id,
            remark=f'工单{order.order_no}配件出库: {part.name} x{out_qty}'
        )
        db.session.add(movement)

    db.session.commit()

    # 检查是否所有配件都已出库，自动标记配件出库确认
    all_outbound = all(p.outbound_status == 1 for p in order.order_parts.all())
    if all_outbound and not order.parts_outbound_confirmed:
        order.parts_outbound_confirmed = 1
        db.session.commit()

    return APIResponse.success(order_part.to_dict(), '备件出库成功')


def _remove_order_part(order, order_part, part, user_id):
    """内部方法：删除备件记录"""
    if not part:
        db.session.delete(order_part)
        db.session.commit()
        return APIResponse.success(message='备件已移除')

    old_stock = part.stock_quantity
    qty = order_part.quantity

    if order_part.outbound_status == 1:
        # 已出库配件：恢复出库时扣减的库存
        part.stock_quantity = old_stock + qty
        movement = StockMovement(
            part_id=part.id,
            movement_type='in',
            reference_type='wo_out_cancel',
            reference_id=order_part.id,
            quantity_before=old_stock,
            quantity_change=qty,
            quantity_after=old_stock + qty,
            price_before=float(part.purchase_price or 0),
            price_after=float(part.purchase_price or 0),
            operator_id=user_id,
            remark=f'工单{order.order_no}删除已出库配件(恢复库存): {part.name} x{qty}'
        )
        db.session.add(movement)

    db.session.delete(order_part)
    db.session.commit()

    # 重新计算工单费用
    WorkOrderService.calculate_order_cost(order.id)
    return APIResponse.success(message='备件已移除，库存已回退')
