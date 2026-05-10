from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import or_, func, extract
from app.extensions import db
from app.models.user import User
from app.models.work_order import WorkOrder, WorkOrderTechnician, RepairItem
from app.utils.helpers import APIResponse
from datetime import datetime, date
from decimal import Decimal

technician_bp = Blueprint('technician', __name__)


@technician_bp.route('/list', methods=['GET'])
@login_required
def list_technicians():
    """获取技师列表（分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    level = request.args.get('level', '')
    status = request.args.get('status', type=int)

    query = User.query.filter_by(employee_type='technician')
    if keyword:
        query = query.filter(or_(
            User.real_name.like(f'%{keyword}%'),
            User.employee_no.like(f'%{keyword}%'),
            User.phone.like(f'%{keyword}%')
        ))
    if level:
        query = query.filter_by(level=level)
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(User.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [{**t.to_dict(), 'name': t.real_name} for t in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@technician_bp.route('/all', methods=['GET'])
@login_required
def get_all_active():
    """获取所有在岗技师（用于下拉选择）- 角色为维修技师的用户"""
    technicians = User.query.filter_by(
        status=1, role_id=4
    ).order_by(User.level.desc(), User.id.asc()).all()
    return APIResponse.success([{
        'id': t.id,
        'name': t.real_name,
        'employee_no': t.employee_no,
        'level': t.level,
        'hourly_rate': float(t.hourly_rate) if t.hourly_rate else 0
    } for t in technicians])


@technician_bp.route('/levels', methods=['GET'])
@login_required
def get_levels():
    """获取技师等级列表"""
    levels = db.session.query(User.level).filter(
        User.employee_type == 'technician',
        User.level.isnot(None),
        User.level != ''
    ).distinct().order_by(User.level).all()
    return APIResponse.success([l[0] for l in levels])


@technician_bp.route('', methods=['POST'])
@login_required
def create_technician():
    """新增技师"""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return APIResponse.error('技师姓名不能为空')

    # 检查工号是否重复
    employee_no = data.get('employee_no', '').strip()
    if employee_no and User.query.filter_by(employee_no=employee_no).first():
        return APIResponse.error(f'工号"{employee_no}"已存在')

    tech = User(
        username=employee_no or name,
        real_name=name,
        gender=data.get('gender', 0),
        phone=data.get('phone', ''),
        id_card=data.get('id_card', ''),
        department=data.get('department', '维修部'),
        position=data.get('position', '技师'),
        employee_type='technician',
        employee_no=employee_no,
        level=data.get('level', '初级'),
        entry_date=datetime.strptime(data['entry_date'], '%Y-%m-%d').date() if data.get('entry_date') else None,
        base_salary=data.get('base_salary', 0),
        hourly_rate=data.get('hourly_rate', 0),
        status=data.get('status', 1),
        role_id=4  # 维修技师角色
    )
    tech.set_password(data.get('password', '123456'))
    db.session.add(tech)
    db.session.commit()
    result = tech.to_dict()
    result['name'] = tech.real_name
    return APIResponse.success(result, '技师创建成功')


@technician_bp.route('/<int:id>', methods=['GET'])
@login_required
def get_technician(id):
    """获取技师详情"""
    tech = User.query.filter_by(id=id, employee_type='technician').first_or_404()
    data = tech.to_dict()
    data['name'] = tech.real_name
    return APIResponse.success(data)


@technician_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_technician(id):
    """更新技师信息"""
    tech = User.query.filter_by(id=id, employee_type='technician').first_or_404()
    data = request.get_json()

    # 检查工号唯一性
    employee_no = data.get('employee_no', '').strip()
    if employee_no and employee_no != tech.employee_no:
        if User.query.filter_by(employee_no=employee_no).first():
            return APIResponse.error(f'工号"{employee_no}"已存在')

    # name 映射为 real_name
    if 'name' in data:
        tech.real_name = data['name']

    for field in ['gender', 'phone', 'id_card', 'department', 'position',
                  'level', 'base_salary', 'hourly_rate', 'status']:
        if field in data:
            setattr(tech, field, data[field])

    if 'entry_date' in data and data['entry_date']:
        tech.entry_date = datetime.strptime(data['entry_date'], '%Y-%m-%d').date()
    elif 'entry_date' in data and not data['entry_date']:
        tech.entry_date = None

    if 'password' in data and data['password']:
        tech.set_password(data['password'])

    db.session.commit()
    result = tech.to_dict()
    result['name'] = tech.real_name
    return APIResponse.success(result, '技师信息已更新')


@technician_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_technician(id):
    """删除技师"""
    tech = User.query.filter_by(id=id, employee_type='technician').first_or_404()

    # 检查是否有未完成的工单分配
    active_assignments = WorkOrderTechnician.query.filter_by(
        technician_id=id
    ).join(WorkOrder).filter(WorkOrder.status == 0).first()
    if active_assignments:
        return APIResponse.error('该技师有未完成的工单分配，无法删除')

    db.session.delete(tech)
    db.session.commit()
    return APIResponse.success(message='技师已删除')


# ==================== 工时统计与工资核算 ====================

@technician_bp.route('/<int:id>/labor-stats', methods=['GET'])
@login_required
def get_labor_stats(id):
    """获取技师工时统计（按月）"""
    tech = User.query.filter_by(id=id, employee_type='technician').first_or_404()

    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    # 从工单技师分配记录中统计
    assignments = WorkOrderTechnician.query.filter_by(technician_id=id).join(
        WorkOrder, WorkOrderTechnician.order_id == WorkOrder.id
    ).filter(
        extract('year', WorkOrderTechnician.assigned_at) == year,
        extract('month', WorkOrderTechnician.assigned_at) == month
    ).all()

    # 汇总
    total_hours = sum(float(a.labor_hours or 0) for a in assignments)
    total_labor_amount = sum(float(a.labor_amount or 0) for a in assignments)
    order_count = len(set(a.order_id for a in assignments))

    # 工时明细
    details = []
    for a in assignments:
        order = WorkOrder.query.get(a.order_id)
        details.append({
            'id': a.id,
            'order_id': a.order_id,
            'order_no': order.order_no if order else '',
            'plate_number': order.plate_number if order else '',
            'repair_item_id': a.repair_item_id,
            'assign_type': a.assign_type,
            'labor_hours': float(a.labor_hours or 0),
            'labor_amount': float(a.labor_amount or 0),
            'status': order.status if order else 0,
            'status_name': order.STATUS_MAP.get(order.status, '未知') if order else '未知',
            'assigned_at': a.assigned_at.isoformat() if a.assigned_at else None
        })

    # 工资核算
    hourly_rate = float(tech.hourly_rate or 0)
    base_salary = float(tech.base_salary or 0)
    labor_wage = total_hours * hourly_rate  # 工时工资 = 总工时 × 时薪
    total_wage = base_salary + labor_wage    # 总工资 = 底薪 + 工时工资

    return APIResponse.success({
        'technician': {
            'id': tech.id,
            'name': tech.real_name,
            'level': tech.level,
            'hourly_rate': hourly_rate,
            'base_salary': base_salary
        },
        'period': f'{year}-{month:02d}',
        'summary': {
            'total_hours': round(total_hours, 2),
            'total_labor_amount': round(total_labor_amount, 2),
            'order_count': order_count,
            'labor_wage': round(labor_wage, 2),
            'base_salary': base_salary,
            'total_wage': round(total_wage, 2)
        },
        'details': details
    })


@technician_bp.route('/labor-summary', methods=['GET'])
@login_required
def labor_summary():
    """技师工时汇总（所有技师某月的汇总）"""
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    # 获取所有在岗技师
    technicians = User.query.filter_by(
        status=1, employee_type='technician'
    ).all()

    results = []
    for tech in technicians:
        # 统计该技师当月工时
        assignments = WorkOrderTechnician.query.filter_by(technician_id=tech.id).join(
            WorkOrder, WorkOrderTechnician.order_id == WorkOrder.id
        ).filter(
            extract('year', WorkOrderTechnician.assigned_at) == year,
            extract('month', WorkOrderTechnician.assigned_at) == month
        ).all()

        total_hours = sum(float(a.labor_hours or 0) for a in assignments)
        total_labor_amount = sum(float(a.labor_amount or 0) for a in assignments)
        order_count = len(set(a.order_id for a in assignments))
        hourly_rate = float(tech.hourly_rate or 0)
        base_salary = float(tech.base_salary or 0)
        labor_wage = total_hours * hourly_rate

        results.append({
            'technician_id': tech.id,
            'name': tech.real_name,
            'employee_no': tech.employee_no,
            'level': tech.level,
            'hourly_rate': hourly_rate,
            'base_salary': base_salary,
            'total_hours': round(total_hours, 2),
            'total_labor_amount': round(total_labor_amount, 2),
            'order_count': order_count,
            'labor_wage': round(labor_wage, 2),
            'total_wage': round(base_salary + labor_wage, 2)
        })

    # 按总工时降序排列
    results.sort(key=lambda x: x['total_hours'], reverse=True)

    # 汇总合计
    total_all = {
        'total_hours': round(sum(r['total_hours'] for r in results), 2),
        'total_labor_amount': round(sum(r['total_labor_amount'] for r in results), 2),
        'total_order_count': sum(r['order_count'] for r in results),
        'total_wage': round(sum(r['total_wage'] for r in results), 2)
    }

    return APIResponse.success({
        'period': f'{year}-{month:02d}',
        'items': results,
        'total': total_all
    })
