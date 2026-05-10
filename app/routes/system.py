from flask import Blueprint, request, current_app
from flask_login import login_required, current_user
from app.utils.decorators import permission_required
from app.extensions import db
from app.models.user import User, Role, OperationLog
from app.models.system import SystemConfig, BackupRecord, DictItem
from app.utils.helpers import APIResponse
from datetime import datetime
import os
import json
import subprocess

system_bp = Blueprint('system', __name__)

@system_bp.route('/configs', methods=['GET'])
@permission_required('system:config')
def list_configs():
    configs = SystemConfig.query.all()
    return APIResponse.success([c.to_dict() for c in configs])

@system_bp.route('/configs', methods=['PUT'])
@permission_required('system:config')
def update_configs():
    data = request.get_json()
    for key, value in data.items():
        config = SystemConfig.query.filter_by(config_key=key).first()
        if config:
            config.config_value = str(value)
    db.session.commit()
    return APIResponse.success(message='配置更新成功')

# ========== 用户管理 ==========
@system_bp.route('/users', methods=['GET'])
@permission_required('system:user')
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@system_bp.route('/users', methods=['POST'])
@permission_required('system:user')
def create_user():
    data = request.get_json()

    if User.query.filter_by(username=data['username']).first():
        return APIResponse.error('用户名已存在')

    user = User(
        username=data['username'],
        real_name=data['real_name'],
        phone=data.get('phone'),
        email=data.get('email'),
        role_id=data['role_id'],
        gender=data.get('gender', 0),
        id_card=data.get('id_card'),
        department=data.get('department'),
        position=data.get('position'),
        employee_type=data.get('employee_type'),
        employee_no=data.get('employee_no'),
        level=data.get('level'),
        title=data.get('title'),
        entry_date=data.get('entry_date'),
        base_salary=data.get('base_salary', 0),
        hourly_rate=data.get('hourly_rate', 0)
    )
    user.set_password(data.get('password', '123456'))
    db.session.add(user)
    db.session.commit()
    return APIResponse.success(user.to_dict(), '用户创建成功')

@system_bp.route('/users/<int:id>', methods=['PUT'])
@permission_required('system:user')
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()

    for field in ['real_name', 'phone', 'email', 'role_id', 'status',
                  'gender', 'id_card', 'department', 'position',
                  'employee_type', 'employee_no', 'level', 'title', 'entry_date',
                  'base_salary', 'hourly_rate']:
        if field in data:
            setattr(user, field, data[field])

    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return APIResponse.success(user.to_dict(), '用户更新成功')

@system_bp.route('/users/<int:id>', methods=['DELETE'])
@permission_required('system:user')
def delete_user(id):
    if id == current_user.id:
        return APIResponse.error('不能删除当前登录用户')
    user = User.query.get_or_404(id)
    user.status = 0
    db.session.commit()
    return APIResponse.success(message='用户已禁用')

# ========== 角色管理 ==========
@system_bp.route('/roles', methods=['GET'])
@permission_required('system:role')
def list_roles():
    roles = Role.query.all()
    return APIResponse.success([{
        'id': r.id,
        'name': r.name,
        'code': r.code,
        'description': r.description,
        'permissions': r.permissions if isinstance(r.permissions, list) else (json.loads(r.permissions) if r.permissions else []),
        'user_count': r.users.count(),
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in roles])

@system_bp.route('/roles', methods=['POST'])
@permission_required('system:role')
def create_role():
    data = request.get_json()
    if Role.query.filter_by(name=data['name']).first():
        return APIResponse.error('角色名称已存在')
    if Role.query.filter_by(code=data['code']).first():
        return APIResponse.error('角色编码已存在')
    role = Role(
        name=data['name'],
        code=data['code'],
        description=data.get('description', ''),
        permissions=data.get('permissions', [])
    )
    db.session.add(role)
    db.session.commit()
    return APIResponse.success({'id': role.id}, '角色创建成功')

@system_bp.route('/roles/<int:id>', methods=['PUT'])
@permission_required('system:role')
def update_role(id):
    role = Role.query.get_or_404(id)
    data = request.get_json()
    if 'name' in data and data['name'] != role.name:
        if Role.query.filter_by(name=data['name']).first():
            return APIResponse.error('角色名称已存在')
    if 'code' in data and data['code'] != role.code:
        if Role.query.filter_by(code=data['code']).first():
            return APIResponse.error('角色编码已存在')
    for field in ['name', 'code', 'description', 'permissions']:
        if field in data:
            setattr(role, field, data[field])
    db.session.commit()
    return APIResponse.success(message='角色更新成功')

@system_bp.route('/roles/<int:id>', methods=['DELETE'])
@permission_required('system:role')
def delete_role(id):
    role = Role.query.get_or_404(id)
    if role.users.count() > 0:
        return APIResponse.error(f'该角色下有 {role.users.count()} 个用户，无法删除')
    db.session.delete(role)
    db.session.commit()
    return APIResponse.success(message='角色删除成功')

@system_bp.route('/roles/<int:id>/users', methods=['GET'])
@permission_required('system:role')
def list_role_users(id):
    """获取某角色下的用户列表"""
    role = Role.query.get_or_404(id)
    users = role.users.filter(User.status == 1).all()
    return APIResponse.success([{
        'id': u.id,
        'username': u.username,
        'real_name': u.real_name,
        'phone': u.phone,
        'department': u.department,
        'position': u.position
    } for u in users])

@system_bp.route('/roles/<int:id>/users', methods=['POST'])
@permission_required('system:role')
def assign_role_users(id):
    """批量设置用户的角色"""
    role = Role.query.get_or_404(id)
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    users = User.query.filter(User.id.in_(user_ids)).all()
    for u in users:
        u.role_id = id
    db.session.commit()
    return APIResponse.success(message=f'已为 {len(users)} 个用户分配角色')

# ========== 操作日志 ==========
@system_bp.route('/logs', methods=['GET'])
@permission_required('system:log')
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    module = request.args.get('module')
    username = request.args.get('username')

    query = OperationLog.query
    if module:
        query = query.filter_by(module=module)
    if username:
        query = query.filter(OperationLog.username.like(f'%{username}%'))

    pagination = query.order_by(OperationLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [l.to_dict() for l in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

# ========== 数据备份 ==========
@system_bp.route('/backup', methods=['POST'])
@permission_required('system:config')
def create_backup():
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    backup_path = os.path.join(current_app.config.get('BACKUP_FOLDER', 'backups'), backup_name)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)

    record = BackupRecord(
        backup_name=backup_name,
        backup_type='full',
        file_path=backup_path,
        status=0,
        created_by=current_user.id
    )
    db.session.add(record)
    db.session.commit()

    try:
        from app.config import Config
        cmd = f"mysqldump -u{Config.DB_USER} -p{Config.DB_PASSWORD} {Config.DB_NAME} > {backup_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            record.status = 1
            if os.path.exists(backup_path):
                record.file_size = os.path.getsize(backup_path)
            db.session.commit()
            return APIResponse.success({'file_path': backup_path}, '备份成功')
        else:
            record.status = 2
            db.session.commit()
            return APIResponse.error('备份失败: ' + result.stderr)
    except Exception as e:
        record.status = 2
        db.session.commit()
        return APIResponse.error(f'备份异常: {str(e)}')

# ========== 业务字典 ==========
@system_bp.route('/dict-items', methods=['GET'])
@permission_required('system:config')
def list_dict_items():
    dict_type = request.args.get('type', '')
    query = DictItem.query
    if dict_type:
        query = query.filter_by(dict_type=dict_type)
    items = query.order_by(DictItem.sort, DictItem.id).all()
    return APIResponse.success([i.to_dict() for i in items])

@system_bp.route('/dict-items', methods=['POST'])
@permission_required('system:config')
def create_dict_item():
    data = request.get_json()
    item = DictItem(
        dict_type=data.get('dict_type', ''),
        name=data.get('name', ''),
        code=data.get('code', ''),
        sort=data.get('sort', 0),
        status=data.get('status', 1)
    )
    db.session.add(item)
    db.session.commit()
    return APIResponse.success(item.to_dict(), '创建成功')

@system_bp.route('/dict-items/<int:id>', methods=['PUT'])
@permission_required('system:config')
def update_dict_item(id):
    item = DictItem.query.get_or_404(id)
    data = request.get_json()
    if 'name' in data: item.name = data['name']
    if 'code' in data: item.code = data['code']
    if 'sort' in data: item.sort = data['sort']
    if 'status' in data: item.status = data['status']
    if 'dict_type' in data: item.dict_type = data['dict_type']
    db.session.commit()
    return APIResponse.success(item.to_dict(), '更新成功')

@system_bp.route('/dict-items/<int:id>', methods=['DELETE'])
@permission_required('system:config')
def delete_dict_item(id):
    item = DictItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return APIResponse.success(message='删除成功')
