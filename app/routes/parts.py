from flask import Blueprint, request
from flask_login import login_required, current_user
from app.utils.decorators import permission_required
from sqlalchemy import or_
from app.extensions import db
from app.models.parts import PartsCategory, Supplier, Part, PartsInbound, PartsOutbound, PartsInboundDetail, PartsOutboundDetail, _get_user_name
from app.services.parts_service import PartsService
from app.utils.helpers import APIResponse

parts_bp = Blueprint('parts', __name__)

# ========== 配件分类 ==========
@parts_bp.route('/categories', methods=['GET'])
@permission_required('parts:read')
def list_categories():
    categories = PartsCategory.query.filter_by(status=1).order_by(PartsCategory.sort).all()
    return APIResponse.success([c.to_dict() for c in categories])

@parts_bp.route('/categories', methods=['POST'])
@permission_required('parts:create')
def create_category():
    data = request.get_json()
    # 将空字符串转为 None 或默认值（MySQL 的 INT 列不接受空字符串）
    parent_id = data.get('parent_id', 0)
    level = data.get('level', 1)
    sort = data.get('sort', 0)
    if parent_id == '': parent_id = 0
    if level == '': level = 1
    if sort == '': sort = 0

    category = PartsCategory(
        name=data['name'],
        code=data.get('code'),
        parent_id=parent_id,
        level=level,
        sort=sort
    )
    db.session.add(category)
    db.session.commit()
    return APIResponse.success(category.to_dict(), '分类创建成功')

# ========== 供应商 ==========
@parts_bp.route('/suppliers', methods=['GET'])
@permission_required('parts:read')
def list_suppliers():
    keyword = request.args.get('keyword', '')
    query = Supplier.query.filter_by(status=1)
    if keyword:
        query = query.filter(or_(
            Supplier.name.like(f'%{keyword}%'),
            Supplier.code.like(f'%{keyword}%')
        ))
    suppliers = query.order_by(Supplier.created_at.desc()).all()
    return APIResponse.success([s.to_dict() for s in suppliers])

@parts_bp.route('/suppliers', methods=['POST'])
@permission_required('parts:create')
def create_supplier():
    data = request.get_json()
    supplier = Supplier(
        name=data['name'],
        code=data.get('code'),
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        bank_name=data.get('bank_name'),
        bank_account=data.get('bank_account'),
        credit_level=data.get('credit_level', 1),
        remark=data.get('remark')
    )
    db.session.add(supplier)
    db.session.commit()
    return APIResponse.success(supplier.to_dict(), '供应商创建成功')

@parts_bp.route('/suppliers/<int:id>', methods=['PUT'])
@permission_required('parts:update')
def update_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    data = request.get_json()
    for field in ['name', 'code', 'contact_person', 'phone', 'email', 'address',
                  'bank_name', 'bank_account', 'credit_level', 'remark', 'status']:
        if field in data:
            setattr(supplier, field, data[field])
    db.session.commit()
    return APIResponse.success(supplier.to_dict(), '供应商更新成功')

# ========== 配件库存 ==========
@parts_bp.route('/list', methods=['GET'])
@permission_required('parts:read')
def list_parts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    category_id = request.args.get('category_id', type=int)
    low_stock = request.args.get('low_stock', type=int)

    query = Part.query.filter_by(status=1)
    if keyword:
        query = query.filter(or_(
            Part.name.like(f'%{keyword}%'),
            Part.part_no.like(f'%{keyword}%'),
            Part.brand.like(f'%{keyword}%')
        ))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if low_stock:
        query = query.filter(Part.stock_quantity <= Part.min_stock, Part.min_stock > 0)

    pagination = query.order_by(Part.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@parts_bp.route('/<int:id>', methods=['GET'])
@permission_required('parts:read')
def get_part(id):
    part = Part.query.get_or_404(id)
    return APIResponse.success(part.to_dict())

@parts_bp.route('', methods=['POST'])
@permission_required('parts:create')
def create_part():
    data = request.get_json()

    # 将空字符串转为 None 或默认值（MySQL 的 INT/Numeric 列不接受空字符串）
    def _num(key, default=0):
        val = data.get(key, default)
        if val == '' or val is None:
            return default
        return val

    part = Part(
        part_no=data['part_no'],
        name=data['name'],
        category_id=_num('category_id') or None,
        brand=data.get('brand'),
        model=data.get('model'),
        unit=data.get('unit', '个'),
        purchase_price=_num('purchase_price'),
        selling_price=_num('selling_price'),
        stock_quantity=_num('stock_quantity'),
        min_stock=_num('min_stock'),
        max_stock=_num('max_stock'),
        warehouse=data.get('warehouse', '默认仓库'),
        location=data.get('location'),
        factory_code=data.get('factory_code'),
        location_code=data.get('location_code'),
        warehouse_location=data.get('warehouse_location'),
        applicable_vehicle=data.get('applicable_vehicle'),
        network_price=_num('network_price'),
        safety_stock=_num('safety_stock'),
        min_package_qty=_num('min_package_qty'),
        archive_remark=data.get('archive_remark')
    )
    db.session.add(part)
    db.session.commit()
    return APIResponse.success(part.to_dict(), '配件创建成功')

@parts_bp.route('/<int:id>', methods=['PUT'])
@permission_required('parts:update')
def update_part(id):
    import json
    part = Part.query.get_or_404(id)
    data = request.get_json()

    # 需要将空字符串转为 None 或 0 的数值字段
    num_fields = ['category_id', 'selling_price', 'min_stock', 'max_stock',
                  'network_price', 'safety_stock', 'min_package_qty']

    for field in ['name', 'category_id', 'brand', 'model', 'unit',
                  'selling_price', 'min_stock', 'max_stock', 'warehouse',
                  'location', 'status', 'pinyin_code', 'specification',
                  'network_price', 'safety_stock', 'min_package_qty',
                  'boutique_location', 'spare_location', 'factory_code',
                  'origin', 'replaceable_part', 'location_code',
                  'warehouse_location', 'applicable_vehicle',
                  'category1', 'category2', 'discontinued', 'archive_remark']:
        if field in data:
            val = data[field]
            # 将空字符串转为 None 或 0（MySQL 的 INT/Numeric 列不接受空字符串）
            if val == '' and field in num_fields:
                val = 0 if field != 'category_id' else None
            setattr(part, field, val)
    if 'applicable_vehicles' in data:
        part.applicable_vehicles = json.dumps(data['applicable_vehicles'], ensure_ascii=False)
    db.session.commit()
    return APIResponse.success(part.to_dict(), '配件更新成功')

# ========== 入库管理 ==========
@parts_bp.route('/inbound', methods=['POST'])
@permission_required('parts:stock')
def create_inbound():
    data = request.get_json()
    inbound = PartsService.inbound(data, current_user.id)
    return APIResponse.success(inbound.to_dict(include_details=True), '入库成功')

@parts_bp.route('/inbound/list', methods=['GET'])
@permission_required('parts:read')
def list_inbound():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = PartsInbound.query.order_by(
        PartsInbound.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [i.to_dict() for i in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@parts_bp.route('/inbound/<int:id>', methods=['GET'])
@permission_required('parts:read')
def get_inbound(id):
    inbound = PartsInbound.query.get_or_404(id)
    return APIResponse.success(inbound.to_dict(include_details=True))

@parts_bp.route('/inbound/<int:id>', methods=['PUT'])
@permission_required('parts:update')
def update_inbound(id):
    inbound = PartsInbound.query.get_or_404(id)
    if inbound.status != 0:
        return APIResponse.error('只能修改暂存状态的入库单')
    result = PartsService.update_inbound(id, request.json, current_user.id)
    return APIResponse.success(result.to_dict(include_details=True), '修改成功')

# ========== 备件出入库记录 ==========
@parts_bp.route('/<int:id>/stock-records', methods=['GET'])
@permission_required('parts:read')
def part_stock_records(id):
    """查询某备件的入库和出库记录"""
    Part.query.get_or_404(id)
    inbound_details = PartsInboundDetail.query.filter_by(part_id=id).order_by(PartsInboundDetail.created_at.desc()).all()
    outbound_details = PartsOutboundDetail.query.filter_by(part_id=id).order_by(PartsOutboundDetail.created_at.desc()).all()
    inbound_records = []
    for d in inbound_details:
        tax_rate = float(d.inbound.tax_rate) if d.inbound and d.inbound.tax_rate else 0
        rate = 1 + tax_rate / 100
        unit_price = float(d.unit_price) if d.unit_price else 0
        total_price = float(d.total_price) if d.total_price else 0
        # 优先使用存储的含税单价，避免反算精度丢失
        stored_price_with_tax = float(d.unit_price_with_tax) if d.unit_price_with_tax else 0
        price_with_tax = stored_price_with_tax if stored_price_with_tax else round(unit_price * rate, 2)
        inbound_records.append({
            'type': '入库',
            'ref_id': d.inbound_id,
            'ref_no': d.inbound.inbound_no if d.inbound else '',
            'quantity': d.quantity,
            'unit_price': unit_price,
            'unit_price_with_tax': price_with_tax,
            'total_price': total_price,
            'total_price_with_tax': round(d.quantity * price_with_tax, 2),
            'tax_amount': round(d.quantity * price_with_tax - total_price, 2),
            'tax_rate': tax_rate,
            'operator_name': _get_user_name(d.inbound.inbound_by) if d.inbound else '',
            'created_at': d.created_at.isoformat() if d.created_at else None
        })
    outbound_records = []
    for d in outbound_details:
        outbound_records.append({
            'type': '出库',
            'ref_id': d.outbound_id,
            'ref_no': d.outbound.outbound_no if d.outbound else '',
            'quantity': d.quantity,
            'unit_price': float(d.unit_price) if d.unit_price else 0,
            'total_price': float(d.total_price) if d.total_price else 0,
            'created_at': d.created_at.isoformat() if d.created_at else None
        })
    # 工单出库和回退记录（从库存变动表查询，删除配件后记录仍保留）
    from app.models.parts import StockMovement
    from app.models.user import User
    # 获取该配件最近一次入库的税率
    latest_inbound_detail = PartsInboundDetail.query.filter_by(part_id=id).order_by(PartsInboundDetail.id.desc()).first()
    tax_rate = 0
    if latest_inbound_detail and latest_inbound_detail.inbound:
        tax_rate = float(latest_inbound_detail.inbound.tax_rate) if latest_inbound_detail.inbound.tax_rate else 0
    price_rate = 1 + tax_rate / 100

    wo_movements = StockMovement.query.filter(
        StockMovement.part_id == id,
        StockMovement.reference_type.in_(['wo_part_out', 'wo_out_cancel'])
    ).order_by(StockMovement.created_at.desc()).all()
    work_order_records = []
    for m in wo_movements:
        # 从remark中提取工单号
        ref_no = ''
        if m.remark and '工单' in m.remark:
            ref_no = m.remark.split('工单')[1].split('配')[0].split('删')[0].strip()
        # 查询操作人姓名
        operator_name = ''
        if m.operator_id:
            operator = User.query.get(m.operator_id)
            if operator:
                operator_name = operator.real_name or operator.username
        qty = abs(m.quantity_change)
        unit_price_no_tax = float(m.price_before) if m.price_before else 0
        unit_price_with_tax = round(unit_price_no_tax * price_rate, 2)
        total_no_tax = qty * unit_price_no_tax
        total_with_tax = round(qty * unit_price_with_tax, 2)
        tax_amount = round(total_with_tax - total_no_tax, 2)
        if m.reference_type == 'wo_part_out':
            work_order_records.append({
                'type': '工单出库',
                'ref_id': m.reference_id,
                'ref_no': ref_no,
                'quantity': qty,
                'unit_price': unit_price_no_tax,
                'total_price': total_no_tax,
                'unit_price_with_tax': unit_price_with_tax,
                'total_price_with_tax': total_with_tax,
                'tax_amount': tax_amount,
                'operator_name': operator_name,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })
        else:
            work_order_records.append({
                'type': '工单出库回退',
                'ref_id': m.reference_id,
                'ref_no': ref_no,
                'quantity': -qty,
                'unit_price': -unit_price_no_tax,
                'total_price': -total_no_tax,
                'unit_price_with_tax': -unit_price_with_tax,
                'total_price_with_tax': -total_with_tax,
                'tax_amount': -tax_amount,
                'operator_name': operator_name,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })
    all_records = sorted(inbound_records + outbound_records + work_order_records, key=lambda x: x['created_at'] or '', reverse=True)
    return APIResponse.success(all_records)

# ========== 出库管理 ==========
@parts_bp.route('/outbound/<int:id>', methods=['GET'])
@permission_required('parts:read')
def get_outbound(id):
    outbound = PartsOutbound.query.get_or_404(id)
    return APIResponse.success(outbound.to_dict(include_details=True))

@parts_bp.route('/outbound', methods=['POST'])
@permission_required('parts:stock')
def create_outbound():
    data = request.get_json()
    outbound = PartsService.outbound(data, current_user.id)
    return APIResponse.success(outbound.to_dict(include_details=True), '出库成功')

@parts_bp.route('/outbound/list', methods=['GET'])
@permission_required('parts:read')
def list_outbound():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    outbound_type = request.args.get('outbound_type', '')
    status = request.args.get('status', type=int)

    query = PartsOutbound.query
    if keyword:
        query = query.filter(PartsOutbound.outbound_no.like(f'%{keyword}%'))
    if outbound_type:
        query = query.filter_by(outbound_type=outbound_type)
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(
        PartsOutbound.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@parts_bp.route('/outbound/<int:id>', methods=['PUT'])
@permission_required('parts:update')
def update_outbound(id):
    outbound = PartsOutbound.query.get_or_404(id)
    data = request.get_json()
    if 'status' in data and data['status'] == 2 and outbound.status == 1:
        # 取消已出库的单据，回滚库存
        PartsService.cancel_outbound(id)
        return APIResponse.success(message='出库单已取消')
    return APIResponse.error('不支持的修改操作')

# ========== 库存预警 ==========
@parts_bp.route('/low-stock', methods=['GET'])
@permission_required('parts:read')
def get_low_stock():
    parts = PartsService.get_low_stock_parts()
    return APIResponse.success([p.to_dict() for p in parts])

# ========== 库存变动记录 ==========
@parts_bp.route('/stock-movements', methods=['GET'])
@permission_required('parts:read')
def stock_movements():
    part_id = request.args.get('part_id', type=int)
    from app.models.parts import StockMovement
    query = StockMovement.query
    if part_id:
        query = query.filter_by(part_id=part_id)
    movements = query.order_by(StockMovement.created_at.desc()).limit(100).all()
    return APIResponse.success([m.to_dict() for m in movements])
