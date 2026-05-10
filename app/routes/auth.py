from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.models.user import User, OperationLog
from app.utils.helpers import APIResponse
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return APIResponse.error('请求数据格式错误')
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return APIResponse.error('用户名和密码不能为空')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return APIResponse.error('用户名或密码错误')

    if user.status != 1:
        return APIResponse.error('账号已被禁用')

    login_user(user, remember=True)
    user.last_login = datetime.utcnow()
    db.session.commit()

    # 记录操作日志
    log = OperationLog(
        user_id=user.id,
        username=user.username,
        action='login',
        module='auth',
        description='用户登录',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return APIResponse.success({
        'user': user.to_dict(),
        'token': 'session-based'
    }, '登录成功')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    log = OperationLog(
        user_id=current_user.id,
        username=current_user.username,
        action='logout',
        module='auth',
        description='用户登出',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    logout_user()
    return APIResponse.success(message='登出成功')

@auth_bp.route('/info', methods=['GET'])
@login_required
def user_info():
    return APIResponse.success(current_user.to_dict())

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not current_user.check_password(old_password):
        return APIResponse.error('原密码错误')

    current_user.set_password(new_password)
    db.session.commit()

    return APIResponse.success(message='密码修改成功')
