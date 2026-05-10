from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.extensions import db
from app.models.work_order import RepairItemTemplate, RepairItemTemplatePart
from app.utils.helpers import APIResponse

repair_item_bp = Blueprint('repair_item', __name__)


@repair_item_bp.route('/list', methods=['GET'])
@login_required
def list_templates():
    """获取维修项目模板列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    status = request.args.get('status', type=int)

    query = RepairItemTemplate.query
    if keyword:
        query = query.filter(or_(
            RepairItemTemplate.item_name.like(f'%{keyword}%'),
            RepairItemTemplate.item_code.like(f'%{keyword}%')
        ))
    if category:
        query = query.filter_by(category=category)
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(RepairItemTemplate.sort_order.asc(), RepairItemTemplate.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [t.to_dict() for t in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@repair_item_bp.route('/all', methods=['GET'])
@login_required
def get_all_active():
    """获取所有启用的维修项目模板（用于下拉选择）"""
    templates = RepairItemTemplate.query.filter_by(status=1).order_by(
        RepairItemTemplate.sort_order.asc(), RepairItemTemplate.id.asc()
    ).all()
    return APIResponse.success([t.to_dict() for t in templates])


@repair_item_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """获取所有维修项目分类"""
    categories = db.session.query(RepairItemTemplate.category).filter(
        RepairItemTemplate.category.isnot(None),
        RepairItemTemplate.category != '',
        RepairItemTemplate.status == 1
    ).distinct().order_by(RepairItemTemplate.category).all()
    return APIResponse.success([c[0] for c in categories])


@repair_item_bp.route('', methods=['POST'])
@login_required
def create_template():
    """创建维修项目模板"""
    data = request.get_json()
    # 自动生成项目编码：X + 五位数字
    max_template = RepairItemTemplate.query.filter(
        RepairItemTemplate.item_code.like('X%')
    ).order_by(RepairItemTemplate.id.desc()).first()
    if max_template and max_template.item_code and max_template.item_code.startswith('X'):
        try:
            next_num = int(max_template.item_code[1:]) + 1
        except ValueError:
            next_num = 1
    else:
        next_num = 1
    item_code = f'X{next_num:05d}'

    # 将空字符串转为 None 或默认值（MySQL 的 INT/Numeric 列不接受空字符串）
    labor_hours = data.get('labor_hours', 0)
    labor_price = data.get('labor_price', 0)
    sort_order = data.get('sort_order', 0)
    status = data.get('status', 1)
    if labor_hours == '': labor_hours = 0
    if labor_price == '': labor_price = 0
    if sort_order == '': sort_order = 0
    if status == '': status = 1

    template = RepairItemTemplate(
        item_name=data.get('item_name'),
        item_code=item_code,
        category=data.get('category'),
        labor_hours=labor_hours,
        labor_price=labor_price,
        description=data.get('description'),
        status=status,
        sort_order=sort_order,
        remark=data.get('remark'),
        created_by=current_user.id
    )
    db.session.add(template)
    db.session.commit()
    return APIResponse.success(template.to_dict(), '维修项目创建成功')


@repair_item_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_template(id):
    """获取维修项目模板详情"""
    template = RepairItemTemplate.query.get_or_404(id)
    return APIResponse.success(template.to_dict())


@repair_item_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_template(id):
    """更新维修项目模板"""
    template = RepairItemTemplate.query.get_or_404(id)
    data = request.get_json()

    # 需要将空字符串转为 None 或 0 的数值字段
    num_fields = ['labor_hours', 'labor_price', 'sort_order', 'status']

    for field in ['item_name', 'item_code', 'category', 'labor_hours', 'labor_price',
                  'description', 'status', 'sort_order', 'remark']:
        if field in data:
            val = data[field]
            # 将空字符串转为 None 或 0（MySQL 的 INT/Numeric 列不接受空字符串）
            if val == '' and field in num_fields:
                val = 0
            setattr(template, field, val)

    db.session.commit()
    return APIResponse.success(template.to_dict(), '维修项目更新成功')


@repair_item_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_template(id):
    """删除维修项目模板"""
    template = RepairItemTemplate.query.get_or_404(id)
    db.session.delete(template)
    db.session.commit()
    return APIResponse.success(message='维修项目已删除')


@repair_item_bp.route('/<int:template_id>/parts', methods=['POST'])
@login_required
def add_template_part(template_id):
    """给维修项目模板添加关联配件"""
    template = RepairItemTemplate.query.get_or_404(template_id)
    data = request.get_json()
    part_id = data.get('part_id')
    quantity = int(data.get('quantity', 1))
    if not part_id:
        return APIResponse.error('配件ID不能为空')
    # 检查是否已关联
    existing = RepairItemTemplatePart.query.filter_by(template_id=template_id, part_id=part_id).first()
    if existing:
        existing.quantity = quantity
    else:
        tp = RepairItemTemplatePart(template_id=template_id, part_id=part_id, quantity=quantity)
        db.session.add(tp)
    db.session.commit()
    return APIResponse.success(message='配件关联成功')


@repair_item_bp.route('/<int:template_id>/parts/<int:tp_id>', methods=['DELETE'])
@login_required
def remove_template_part(template_id, tp_id):
    """删除维修项目模板的关联配件"""
    tp = RepairItemTemplatePart.query.filter_by(id=tp_id, template_id=template_id).first_or_404()
    db.session.delete(tp)
    db.session.commit()
    return APIResponse.success(message='配件关联已删除')
