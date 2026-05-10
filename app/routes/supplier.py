from flask import Blueprint, request
from flask_login import login_required
from sqlalchemy import or_
from app.extensions import db
from app.models.parts import Supplier, PartsInbound
from app.utils.helpers import APIResponse

supplier_bp = Blueprint('supplier', __name__)


@supplier_bp.route('/list', methods=['GET'])
@login_required
def list_suppliers():
    """获取供应商列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', type=int)

    query = Supplier.query
    if keyword:
        query = query.filter(or_(
            Supplier.name.like(f'%{keyword}%'),
            Supplier.code.like(f'%{keyword}%'),
            Supplier.contact_person.like(f'%{keyword}%'),
            Supplier.phone.like(f'%{keyword}%')
        ))
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(Supplier.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@supplier_bp.route('/all', methods=['GET'])
@login_required
def all_suppliers():
    """获取所有启用的供应商（用于下拉选择）"""
    items = Supplier.query.filter_by(status=1).order_by(Supplier.name).all()
    return APIResponse.success([s.to_dict() for s in items])


@supplier_bp.route('', methods=['POST'])
@login_required
def create_supplier():
    """创建供应商"""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return APIResponse.error('供应商名称不能为空')

    # 检查编码唯一性
    code = data.get('code', '').strip()
    if code:
        existing = Supplier.query.filter_by(code=code).first()
        if existing:
            return APIResponse.error(f'供应商编码"{code}"已存在')

    supplier = Supplier(
        name=name,
        code=code or None,
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        bank_name=data.get('bank_name'),
        bank_account=data.get('bank_account'),
        credit_level=data.get('credit_level', 1),
        status=data.get('status', 1),
        remark=data.get('remark')
    )
    db.session.add(supplier)
    db.session.commit()
    return APIResponse.success(supplier.to_dict(), '供应商创建成功')


@supplier_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_supplier(id):
    """获取供应商详情"""
    supplier = Supplier.query.get_or_404(id)
    return APIResponse.success(supplier.to_dict())


@supplier_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_supplier(id):
    """更新供应商"""
    supplier = Supplier.query.get_or_404(id)
    data = request.get_json()

    name = data.get('name', '').strip()
    if not name:
        return APIResponse.error('供应商名称不能为空')

    # 检查编码唯一性
    code = data.get('code', '').strip()
    if code and code != supplier.code:
        existing = Supplier.query.filter_by(code=code).first()
        if existing:
            return APIResponse.error(f'供应商编码"{code}"已存在')

    supplier.name = name
    supplier.code = code or None
    supplier.contact_person = data.get('contact_person')
    supplier.phone = data.get('phone')
    supplier.email = data.get('email')
    supplier.address = data.get('address')
    supplier.bank_name = data.get('bank_name')
    supplier.bank_account = data.get('bank_account')
    supplier.credit_level = data.get('credit_level', 1)
    supplier.status = data.get('status', 1)
    supplier.remark = data.get('remark')

    db.session.commit()
    return APIResponse.success(supplier.to_dict(), '供应商更新成功')


@supplier_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_supplier(id):
    """删除供应商"""
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    return APIResponse.success(message='供应商已删除')


@supplier_bp.route('/<int:id>/inbounds', methods=['GET'])
@login_required
def supplier_inbounds(id):
    """获取供应商的入库单列表"""
    supplier = Supplier.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = PartsInbound.query.filter_by(supplier_id=id)
    pagination = query.order_by(PartsInbound.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [i.to_dict() for i in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })
