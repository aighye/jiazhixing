from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.extensions import db
from app.models.employee import Employee, EmployeeLaborStat
from app.models.user import User, Role
from app.utils.helpers import APIResponse, generate_no

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/list', methods=['GET'])
@login_required
def list_employees():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    department = request.args.get('department')
    employee_type = request.args.get('employee_type')

    query = Employee.query.filter_by(status=1)
    if keyword:
        query = query.filter(or_(
            Employee.name.like(f'%{keyword}%'),
            Employee.employee_no.like(f'%{keyword}%'),
            Employee.phone.like(f'%{keyword}%')
        ))
    if department:
        query = query.filter_by(department=department)
    if employee_type:
        query = query.filter_by(employee_type=employee_type)

    pagination = query.order_by(Employee.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [e.to_dict() for e in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@employee_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_employee(id):
    employee = Employee.query.get_or_404(id)
    data = employee.to_dict()
    data['labor_stats'] = [s.to_dict() for s in employee.labor_stats.order_by(
        EmployeeLaborStat.stat_date.desc()).limit(30).all()]
    return APIResponse.success(data)

@employee_bp.route('', methods=['POST'])
@login_required
def create_employee():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # 如果提供了登录名和密码，创建系统用户
    user_id = None
    if username and password:
        if User.query.filter_by(username=username).first():
            return APIResponse.error('登录名已存在')
        # 根据员工类型匹配角色
        role_code_map = {'technician': 'technician', 'service': 'advisor', 'manager': 'manager'}
        role_code = role_code_map.get(data.get('employee_type'), 'technician')
        role = Role.query.filter_by(code=role_code).first()
        if not role:
            role = Role.query.first()
        user = User(
            username=username,
            real_name=data['name'],
            role_id=role.id if role else 1,
            phone=data.get('phone'),
            status=1
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        user_id = user.id

    # 将空字符串转为 None 或默认值（MySQL 的 INT/Numeric 列不接受空字符串）
    gender = data.get('gender', 0)
    base_salary = data.get('base_salary', 0)
    hourly_rate = data.get('hourly_rate', 0)
    if gender == '': gender = 0
    if base_salary == '': base_salary = 0
    if hourly_rate == '': hourly_rate = 0

    employee = Employee(
        employee_no=generate_no('EMP'),
        name=data['name'],
        gender=gender,
        phone=data.get('phone'),
        id_card=data.get('id_card'),
        department=data.get('department'),
        position=data.get('position'),
        employee_type=data.get('employee_type'),
        level=data.get('level'),
        entry_date=data.get('entry_date'),
        base_salary=base_salary,
        hourly_rate=hourly_rate,
        user_id=user_id
    )
    db.session.add(employee)
    db.session.commit()
    return APIResponse.success(employee.to_dict(), '员工创建成功')

@employee_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_employee(id):
    employee = Employee.query.get_or_404(id)
    data = request.get_json()

    # 需要将空字符串转为 None 或 0 的数值字段
    num_fields = ['gender', 'base_salary', 'hourly_rate']

    for field in ['name', 'gender', 'phone', 'id_card', 'department', 'position',
                  'employee_type', 'level', 'entry_date', 'base_salary', 'hourly_rate',
                  'status']:
        if field in data:
            val = data[field]
            # 将空字符串转为 None 或 0（MySQL 的 INT/Numeric 列不接受空字符串）
            if val == '' and field in num_fields:
                val = 0
            setattr(employee, field, val)

    db.session.commit()
    return APIResponse.success(employee.to_dict(), '员工更新成功')

@employee_bp.route('/technicians', methods=['GET'])
@login_required
def list_technicians():
    """获取技师列表（用于工单分配）"""
    technicians = Employee.query.filter_by(
        status=1, employee_type='technician'
    ).all()
    return APIResponse.success([{
        'id': t.id,
        'name': t.name,
        'employee_no': t.employee_no,
        'level': t.level,
        'hourly_rate': float(t.hourly_rate) if t.hourly_rate else 0
    } for t in technicians])
