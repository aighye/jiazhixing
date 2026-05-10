from flask import Blueprint, request
from flask_login import login_required
from app.extensions import db
from app.models.dict import ClaimManufacturer, InsuranceCompany
from app.models.work_order import WorkOrder
from app.utils.helpers import APIResponse

dict_bp = Blueprint('dict', __name__)


# ==================== 索赔厂家管理 ====================

@dict_bp.route('/manufacturers', methods=['GET'])
@login_required
def list_manufacturers():
    """获取所有索赔厂家"""
    items = ClaimManufacturer.query.order_by(ClaimManufacturer.id).all()
    return APIResponse.success([i.to_dict() for i in items])


@dict_bp.route('/manufacturers', methods=['POST'])
@login_required
def add_manufacturer():
    """新增索赔厂家"""
    data = request.get_json()
    if not data.get('name'):
        return APIResponse.error('名称不能为空')
    if ClaimManufacturer.query.filter_by(name=data['name']).first():
        return APIResponse.error('该厂家已存在')
    if data.get('code') and ClaimManufacturer.query.filter_by(code=data['code']).first():
        return APIResponse.error('该厂家编码已存在')
    item = ClaimManufacturer(
        code=data.get('code'),
        name=data['name'],
        contact_person=data.get('contact_person'),
        contact_phone=data.get('contact_phone'),
        remark=data.get('remark')
    )
    db.session.add(item)
    db.session.commit()
    return APIResponse.success(item.to_dict(), '添加成功')


@dict_bp.route('/manufacturers/<int:id>', methods=['GET'])
@login_required
def get_manufacturer(id):
    """获取索赔厂家详情"""
    item = ClaimManufacturer.query.get_or_404(id)
    return APIResponse.success(item.to_dict())


@dict_bp.route('/manufacturers/<int:id>', methods=['PUT'])
@login_required
def update_manufacturer(id):
    """修改索赔厂家"""
    item = ClaimManufacturer.query.get_or_404(id)
    data = request.get_json()
    if 'name' in data and data['name'] != item.name:
        if ClaimManufacturer.query.filter_by(name=data['name']).first():
            return APIResponse.error('该厂家已存在')
    for field in ['code', 'name', 'contact_person', 'contact_phone', 'remark', 'status']:
        if field in data:
            setattr(item, field, data[field])
    db.session.commit()
    return APIResponse.success(item.to_dict(), '更新成功')


@dict_bp.route('/manufacturers/<int:id>', methods=['DELETE'])
@login_required
def delete_manufacturer(id):
    """删除索赔厂家"""
    item = ClaimManufacturer.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return APIResponse.success(None, '删除成功')


@dict_bp.route('/manufacturers/<int:id>/work-orders', methods=['GET'])
@login_required
def manufacturer_work_orders(id):
    """获取索赔厂家关联的工单"""
    manufacturer = ClaimManufacturer.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = WorkOrder.query.filter_by(claim_manufacturer=manufacturer.name)
    pagination = query.order_by(WorkOrder.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@dict_bp.route('/insurances/<int:id>/work-orders', methods=['GET'])
@login_required
def insurance_work_orders(id):
    """获取保险公司关联的工单"""
    company = InsuranceCompany.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = WorkOrder.query.filter_by(insurance_company=company.name)
    pagination = query.order_by(WorkOrder.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


# ==================== 保险公司管理 ====================

@dict_bp.route('/insurances', methods=['GET'])
@login_required
def list_insurances():
    """获取所有保险公司"""
    items = InsuranceCompany.query.order_by(InsuranceCompany.id).all()
    return APIResponse.success([i.to_dict() for i in items])


@dict_bp.route('/insurances', methods=['POST'])
@login_required
def add_insurance():
    """新增保险公司"""
    data = request.get_json()
    if not data.get('name'):
        return APIResponse.error('名称不能为空')
    if InsuranceCompany.query.filter_by(name=data['name']).first():
        return APIResponse.error('该公司已存在')
    if data.get('code') and InsuranceCompany.query.filter_by(code=data['code']).first():
        return APIResponse.error('该公司编码已存在')
    item = InsuranceCompany(
        code=data.get('code'),
        name=data['name'],
        contact_person=data.get('contact_person'),
        contact_phone=data.get('contact_phone'),
        remark=data.get('remark')
    )
    db.session.add(item)
    db.session.commit()
    return APIResponse.success(item.to_dict(), '添加成功')


@dict_bp.route('/insurances/<int:id>', methods=['GET'])
@login_required
def get_insurance(id):
    """获取保险公司详情"""
    item = InsuranceCompany.query.get_or_404(id)
    return APIResponse.success(item.to_dict())


@dict_bp.route('/insurances/<int:id>', methods=['PUT'])
@login_required
def update_insurance(id):
    """修改保险公司"""
    item = InsuranceCompany.query.get_or_404(id)
    data = request.get_json()
    if 'name' in data and data['name'] != item.name:
        if InsuranceCompany.query.filter_by(name=data['name']).first():
            return APIResponse.error('该公司已存在')
    for field in ['code', 'name', 'contact_person', 'contact_phone', 'remark', 'status']:
        if field in data:
            setattr(item, field, data[field])
    db.session.commit()
    return APIResponse.success(item.to_dict(), '更新成功')


@dict_bp.route('/insurances/<int:id>', methods=['DELETE'])
@login_required
def delete_insurance(id):
    """删除保险公司"""
    item = InsuranceCompany.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return APIResponse.success(None, '删除成功')
