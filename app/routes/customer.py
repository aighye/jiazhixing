from flask import Blueprint, request
from flask_login import login_required, current_user
from app.utils.decorators import permission_required
from sqlalchemy import or_
from app.extensions import db
from app.models.customer import Customer, Vehicle, Appointment
from app.utils.helpers import APIResponse, generate_no, generate_customer_no, generate_vehicle_no, generate_appointment_no
import re

customer_bp = Blueprint('customer', __name__)

PLATE_RE = re.compile(r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤川青藏琼宁][A-HJ-NP-Z][A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学警港澳]$')
PHONE_RE = re.compile(r'^1[3-9]\d{9}$')
VIN_RE = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$')

@customer_bp.route('/list', methods=['GET'])
@permission_required('customer:read')
def list_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', type=int)

    query = Customer.query
    if keyword:
        query = query.filter(or_(
            Customer.name.like(f'%{keyword}%'),
            Customer.phone.like(f'%{keyword}%'),
            Customer.customer_no.like(f'%{keyword}%')
        ))
    if status is not None:
        query = query.filter_by(status=status)

    query = query.order_by(Customer.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@customer_bp.route('/<int:id>', methods=['GET'])
@permission_required('customer:read')
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    data = customer.to_dict()
    data['vehicles'] = [v.to_dict() for v in customer.vehicles.all()]
    return APIResponse.success(data)

@customer_bp.route('', methods=['POST'])
@permission_required('customer:create')
def create_customer():
    data = request.get_json()
    phone = data.get('phone', '')
    if not PHONE_RE.match(phone):
        return APIResponse.error('手机号格式不正确')

    # 将空字符串转为 None 或默认值（MySQL 的 INT 列不接受空字符串）
    gender = data.get('gender', 0)
    customer_type = data.get('customer_type', 1)
    vip_level = data.get('vip_level', 0)
    if gender == '': gender = 0
    if customer_type == '': customer_type = 1
    if vip_level == '': vip_level = 0

    customer = Customer(
        customer_no=generate_customer_no(),
        name=data['name'],
        phone=data['phone'],
        email=data.get('email'),
        gender=gender,
        birthday=data.get('birthday'),
        id_card=data.get('id_card'),
        address=data.get('address'),
        customer_type=customer_type,
        company_name=data.get('company_name'),
        vip_level=vip_level,
        remark=data.get('remark'),
        created_by=current_user.id
    )
    db.session.add(customer)
    db.session.commit()
    return APIResponse.success(customer.to_dict(), '客户创建成功')

@customer_bp.route('/<int:id>', methods=['PUT'])
@permission_required('customer:update')
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()

    if 'phone' in data and not PHONE_RE.match(data['phone']):
        return APIResponse.error('手机号格式不正确')

    # 需要将空字符串转为 None 或 0 的数值字段
    num_fields = ['gender', 'customer_type', 'vip_level']

    for field in ['name', 'phone', 'email', 'gender', 'birthday', 'id_card',
                  'address', 'customer_type', 'company_name', 'vip_level', 'remark', 'status']:
        if field in data:
            val = data[field]
            # 将空字符串转为 None 或 0（MySQL 的 INT 列不接受空字符串）
            if val == '' and field in num_fields:
                val = 0
            setattr(customer, field, val)

    db.session.commit()
    return APIResponse.success(customer.to_dict(), '客户更新成功')

@customer_bp.route('/<int:id>', methods=['DELETE'])
@permission_required('customer:delete')
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    customer.status = 0
    db.session.commit()
    return APIResponse.success(message='客户已删除')

# ========== 车辆管理 ==========
@customer_bp.route('/vehicles/list', methods=['GET'])
@permission_required('customer:read')
def list_vehicles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    customer_id = request.args.get('customer_id', type=int)

    query = Vehicle.query.filter_by(status=1)
    if keyword:
        query = query.filter(or_(
            Vehicle.plate_number.like(f'%{keyword}%'),
            Vehicle.vin.like(f'%{keyword}%'),
            Vehicle.brand.like(f'%{keyword}%')
        ))
    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    pagination = query.order_by(Vehicle.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [v.to_dict() for v in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@customer_bp.route('/vehicles', methods=['POST'])
@permission_required('customer:create')
def create_vehicle():
    data = request.get_json()
    plate = data.get('plate_number', '')
    if not PLATE_RE.match(plate):
        return APIResponse.error('车牌号格式不正确')
    vin = data.get('vin', '')
    if vin and not VIN_RE.match(vin):
        return APIResponse.error('VIN码格式不正确，应为17位字母数字（不含I、O、Q）')

    # 将空字符串转为 None（MySQL 的 INT 列不接受空字符串）
    def _val(key):
        v = data.get(key, '')
        return v if v != '' else None

    vehicle = Vehicle(
        vehicle_no=generate_vehicle_no(),
        customer_id=data['customer_id'],
        plate_number=data['plate_number'],
        vin=_val('vin'),
        brand=_val('brand'),
        model=_val('model'),
        year=_val('year'),
        color=_val('color'),
        engine_no=_val('engine_no'),
        purchase_date=_val('purchase_date'),
        mileage=data.get('mileage', 0) or 0,
        insurance_date=_val('insurance_date'),
        inspection_date=_val('inspection_date'),
        remark=_val('remark')
    )
    db.session.add(vehicle)
    db.session.commit()
    return APIResponse.success(vehicle.to_dict(), '车辆添加成功')

@customer_bp.route('/vehicles/<int:id>', methods=['PUT'])
@permission_required('customer:update')
def update_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    data = request.get_json()

    if 'plate_number' in data and not PLATE_RE.match(data['plate_number']):
        return APIResponse.error('车牌号格式不正确')
    if 'vin' in data and data['vin'] and not VIN_RE.match(data['vin']):
        return APIResponse.error('VIN码格式不正确，应为17位字母数字（不含I、O、Q）')

    for field in ['plate_number', 'vin', 'brand', 'model', 'year', 'color',
                  'engine_no', 'purchase_date', 'mileage', 'insurance_date',
                  'inspection_date', 'remark', 'status']:
        if field in data:
            val = data[field]
            # 将空字符串转为 None（MySQL 的 INT 列不接受空字符串）
            if val == '' and field in ('year', 'mileage'):
                val = None if field == 'year' else 0
            setattr(vehicle, field, val)

    db.session.commit()
    return APIResponse.success(vehicle.to_dict(), '车辆更新成功')

# ========== 预约管理 ==========
@customer_bp.route('/appointments/<int:id>', methods=['GET'])
@permission_required('customer:read')
def get_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    return APIResponse.success(appointment.to_dict())

@customer_bp.route('/appointments/list', methods=['GET'])
@permission_required('customer:read')
def list_appointments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', type=int)

    query = Appointment.query
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(Appointment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return APIResponse.success({
        'items': [a.to_dict() for a in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@customer_bp.route('/appointments', methods=['POST'])
@permission_required('customer:create')
def create_appointment():
    data = request.get_json()
    from datetime import date as date_type, time as time_type
    ap_date = data['appointment_date']
    if isinstance(ap_date, str):
        ap_date = date_type.fromisoformat(ap_date)
    ap_time = data['appointment_time']
    if isinstance(ap_time, str):
        parts = ap_time.split(':')
        ap_time = time_type(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    appointment = Appointment(
        appointment_no=generate_appointment_no(),
        customer_id=data['customer_id'],
        vehicle_id=data['vehicle_id'],
        phone=data['phone'],
        appointment_date=ap_date,
        appointment_time=ap_time,
        service_type=data.get('service_type'),
        description=data.get('description'),
        confirm_by=current_user.id
    )
    db.session.add(appointment)
    db.session.commit()
    return APIResponse.success(appointment.to_dict(), '预约创建成功')

@customer_bp.route('/appointments/<int:id>/confirm', methods=['PUT'])
@permission_required('customer:update')
def confirm_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = 1
    appointment.confirm_by = current_user.id
    db.session.commit()
    return APIResponse.success(appointment.to_dict(), '预约已确认')

@customer_bp.route('/appointments/<int:id>/cancel', methods=['PUT'])
@permission_required('customer:update')
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    data = request.get_json()
    appointment.status = 3
    if data and data.get('remark'):
        appointment.remark = (appointment.remark + '\n取消原因：' + data['remark']) if appointment.remark else '取消原因：' + data['remark']
    db.session.commit()
    return APIResponse.success(appointment.to_dict(), '预约已取消')

@customer_bp.route('/appointments/<int:id>/complete', methods=['PUT'])
@permission_required('customer:update')
def complete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = 2
    db.session.commit()
    return APIResponse.success(appointment.to_dict(), '预约已完成')

@customer_bp.route('/appointments/<int:id>', methods=['PUT'])
@permission_required('customer:update')
def update_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.status != 0:
        return APIResponse.error('仅待确认状态的预约可编辑')
    data = request.get_json()
    from datetime import date as date_type, time as time_type
    for field in ['customer_id', 'vehicle_id', 'phone',
                  'service_type', 'description', 'remark']:
        if field in data:
            setattr(appointment, field, data[field])
    if 'appointment_date' in data:
        ap_date = data['appointment_date']
        if isinstance(ap_date, str):
            ap_date = date_type.fromisoformat(ap_date)
        appointment.appointment_date = ap_date
    if 'appointment_time' in data:
        ap_time = data['appointment_time']
        if isinstance(ap_time, str):
            parts = ap_time.split(':')
            ap_time = time_type(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
        appointment.appointment_time = ap_time
    db.session.commit()
    return APIResponse.success(appointment.to_dict(), '预约更新成功')

@customer_bp.route('/appointments/<int:id>', methods=['DELETE'])
@permission_required('customer:delete')
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.status != 0:
        return APIResponse.error('仅待确认状态的预约可删除')
    db.session.delete(appointment)
    db.session.commit()
    return APIResponse.success(None, '预约已删除')

@customer_bp.route('/appointments/<int:id>/to-work-order', methods=['POST'])
@permission_required('customer:create')
def appointment_to_work_order(id):
    """预约转工单"""
    appointment = Appointment.query.get_or_404(id)
    if appointment.status not in [0, 1]:
        return APIResponse.error('仅待确认或已确认的预约可转为工单')

    from app.services.work_order_service import WorkOrderService
    order = WorkOrderService.create_order({
        'customer_id': appointment.customer_id,
        'vehicle_id': appointment.vehicle_id,
        'service_type': appointment.service_type or '',
        'fault_description': appointment.description or '',
    }, current_user.id)

    appointment.status = 2
    db.session.commit()
    return APIResponse.success(order.to_dict(), '预约已转为工单')
