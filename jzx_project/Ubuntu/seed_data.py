"""示例数据填充脚本 - 为系统各模块生成真实的展示数据"""
import sys
import os
import random
from datetime import datetime, timedelta, date, time as dt_time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User, Role, OperationLog
from app.models.customer import Customer, Vehicle, Appointment
from app.models.work_order import WorkOrder, WorkOrderFlowLog, RepairItem, WorkOrderTechnician
from app.models.parts import PartsCategory, Supplier, Part, PartsInbound, PartsInboundDetail, PartsOutbound, PartsOutboundDetail, StockMovement
from app.models.finance import Payment, Invoice
from app.models.employee import Employee, EmployeeLaborStat
from app.models.system import SystemConfig

def seed():
    app = create_app()
    with app.app_context():
        # 清空旧数据（按依赖顺序）
        print("🗑️  清空旧数据...")
        for model in [StockMovement, PartsOutboundDetail, PartsOutbound, PartsInboundDetail, PartsInbound,
                       WorkOrderTechnician, RepairItem, WorkOrderFlowLog, Payment, Invoice,
                       WorkOrder, Appointment, Vehicle, Customer, Employee, EmployeeLaborStat,
                       OperationLog, SystemConfig, Part, Supplier, PartsCategory, User, Role]:
            try:
                model.__table__.drop(db.engine, checkfirst=True)
            except:
                pass

        db.create_all()
        print("✅ 表重建完成")

        # ========== 1. 角色 ==========
        roles_data = [
            Role(name='系统管理员', code='admin', description='系统超级管理员', permissions='["*"]'),
            Role(name='服务经理', code='manager', description='服务部门经理', permissions='["customer:*","work_order:*","parts:*","finance:*","report:*"]'),
            Role(name='服务顾问', code='advisor', description='接待客户', permissions='["customer:read","customer:create","work_order:create","work_order:read","work_order:update"]'),
            Role(name='维修技师', code='technician', description='维修技师', permissions='["work_order:read","work_order:repair"]'),
            Role(name='配件管理员', code='parts_manager', description='配件管理', permissions='["parts:*"]'),
            Role(name='财务人员', code='finance', description='财务', permissions='["finance:*","report:finance"]'),
        ]
        db.session.add_all(roles_data)
        db.session.flush()
        role_map = {r.code: r.id for r in roles_data}
        print("✅ 角色创建完成")

        # ========== 2. 用户 ==========
        users_data = [
            User(username='admin', real_name='张管理', phone='13800000001', email='admin@4s.com', role_id=role_map['admin'], status=1),
            User(username='wang_advisor', real_name='王顾问', phone='13800000002', role_id=role_map['advisor'], status=1),
            User(username='li_manager', real_name='李经理', phone='13800000003', role_id=role_map['manager'], status=1),
            User(username='zhao_finance', real_name='赵财务', phone='13800000004', role_id=role_map['finance'], status=1),
            User(username='chen_parts', real_name='陈配件', phone='13800000005', role_id=role_map['parts_manager'], status=1),
        ]
        for u in users_data:
            u.set_password('123456')
        db.session.add_all(users_data)
        db.session.flush()
        user_map = {u.username: u.id for u in users_data}
        print("✅ 用户创建完成")

        # ========== 3. 员工 ==========
        employees_data = [
            Employee(employee_no='EMP001', name='张管理', gender=1, phone='13800000001', department='管理层', position='总经理', employee_type='manager', level='高级', base_salary=15000, hourly_rate=0, user_id=user_map['admin']),
            Employee(employee_no='EMP002', name='王顾问', gender=1, phone='13800000002', department='服务部', position='高级服务顾问', employee_type='service', level='高级', base_salary=8000, hourly_rate=0, user_id=user_map['wang_advisor']),
            Employee(employee_no='EMP003', name='李经理', gender=1, phone='13800000003', department='服务部', position='服务经理', employee_type='manager', level='高级', base_salary=12000, hourly_rate=0, user_id=user_map['li_manager']),
            Employee(employee_no='EMP004', name='刘技师A', gender=1, phone='13800000006', department='维修车间', position='高级技师', employee_type='technician', level='高级', base_salary=6000, hourly_rate=180),
            Employee(employee_no='EMP005', name='孙技师B', gender=1, phone='13800000007', department='维修车间', position='中级技师', employee_type='technician', level='中级', base_salary=5000, hourly_rate=150),
            Employee(employee_no='EMP006', name='周技师C', gender=1, phone='13800000008', department='维修车间', position='初级技师', employee_type='technician', level='初级', base_salary=4000, hourly_rate=120),
            Employee(employee_no='EMP007', name='吴技师D', gender=0, phone='13800000009', department='维修车间', position='中级技师', employee_type='technician', level='中级', base_salary=5000, hourly_rate=150),
            Employee(employee_no='EMP008', name='赵财务', gender=0, phone='13800000004', department='财务部', position='财务主管', employee_type='manager', level='高级', base_salary=7000, hourly_rate=0, user_id=user_map['zhao_finance']),
            Employee(employee_no='EMP009', name='陈配件', gender=1, phone='13800000005', department='配件部', position='配件主管', employee_type='manager', level='高级', base_salary=6000, hourly_rate=0, user_id=user_map['chen_parts']),
        ]
        db.session.add_all(employees_data)
        db.session.flush()
        emp_map = {e.employee_no: e.id for e in employees_data}
        techs = [e for e in employees_data if e.employee_type == 'technician']
        print("✅ 员工创建完成")

        # ========== 4. 客户 ==========
        customer_names = [
            ('陈先生', 1, '个人'), ('李女士', 0, '个人'), ('王先生', 1, '个人'),
            ('张女士', 0, '个人'), ('刘先生', 1, '个人'), ('赵女士', 0, '个人'),
            ('孙先生', 1, '个人'), ('周女士', 0, '个人'), ('吴先生', 1, '个人'),
            ('郑女士', 0, '个人'), ('钱先生', 1, '个人'), ('冯女士', 0, '个人'),
            ('华顺物流公司', 1, '企业'), ('通达运输公司', 1, '企业'),
        ]
        customers_data = []
        for i, (name, gender, ctype) in enumerate(customer_names):
            c = Customer(
                customer_no=f'CUS{20240001+i}',
                name=name,
                phone=f'139{random.randint(10000000, 99999999)}',
                gender=gender,
                customer_type=2 if ctype == '企业' else 1,
                company_name=name if ctype == '企业' else None,
                vip_level=random.choice([0, 0, 0, 1, 1, 2, 3]),
                total_spending=random.uniform(500, 50000),
                points=random.randint(0, 5000),
                address=f'XX市XX区XX路{random.randint(1,200)}号',
                status=1,
                created_by=user_map['wang_advisor'],
                created_at=datetime.now() - timedelta(days=random.randint(30, 365))
            )
            customers_data.append(c)
        db.session.add_all(customers_data)
        db.session.flush()
        cust_map = {c.customer_no: c.id for c in customers_data}
        print("✅ 客户创建完成")

        # ========== 5. 车辆 ==========
        brands = ['宝马', '奔驰', '奥迪', '大众', '丰田', '本田', '比亚迪', '特斯拉', '蔚来', '理想']
        models_map = {
            '宝马': ['3系', '5系', 'X3', 'X5'], '奔驰': ['C级', 'E级', 'GLC', 'S级'],
            '奥迪': ['A4L', 'A6L', 'Q5L', 'Q7'], '大众': ['帕萨特', '迈腾', '途观L', '探岳'],
            '丰田': ['凯美瑞', 'RAV4', '汉兰达', '卡罗拉'], '本田': ['雅阁', 'CR-V', '思域', '飞度'],
            '比亚迪': ['汉', '唐', '宋PLUS', '海豹'], '特斯拉': ['Model 3', 'Model Y', 'Model S'],
            '蔚来': ['ES6', 'ET5', 'ES8'], '理想': ['L7', 'L8', 'L9']
        }
        colors = ['白色', '黑色', '银色', '红色', '蓝色', '灰色']
        plates_prefix = ['京A', '京B', '京C', '京D', '京E', '京F', '京G', '京H']

        vehicles_data = []
        for i, cust in enumerate(customers_data):
            num_vehicles = random.randint(1, 2)
            for j in range(num_vehicles):
                brand = random.choice(brands)
                model = random.choice(models_map[brand])
                v = Vehicle(
                    vehicle_no=f'V{20240001+i*10+j}',
                    customer_id=cust.id,
                    plate_number=f'{random.choice(plates_prefix)}{random.randint(10000,99999)}',
                    vin='LSVAU' + ''.join([str(random.randint(0,9)) for _ in range(14)]),
                    brand=brand, model=model,
                    year=random.randint(2019, 2025),
                    color=random.choice(colors),
                    mileage=random.randint(5000, 80000),
                    status=1,
                    created_at=datetime.now() - timedelta(days=random.randint(30, 365))
                )
                vehicles_data.append(v)
        db.session.add_all(vehicles_data)
        db.session.flush()
        veh_map = {v.vehicle_no: v.id for v in vehicles_data}
        print("✅ 车辆创建完成")

        # ========== 6. 配件分类和供应商 ==========
        categories = [
            PartsCategory(name='发动机配件', code='ENGINE', parent_id=0, level=1),
            PartsCategory(name='底盘配件', code='CHASSIS', parent_id=0, level=1),
            PartsCategory(name='电气系统', code='ELECTRICAL', parent_id=0, level=1),
            PartsCategory(name='车身配件', code='BODY', parent_id=0, level=1),
            PartsCategory(name='保养件', code='MAINT', parent_id=0, level=1),
        ]
        db.session.add_all(categories)
        db.session.flush()
        cat_map = {c.code: c.id for c in categories}

        suppliers = [
            Supplier(name='华晨汽配供应链', code='SUP001', contact_person='马经理', phone='021-55556666', address='上海市嘉定区汽配城A区', credit_level=5),
            Supplier(name='中德汽车零部件', code='SUP002', contact_person='黄总', phone='010-66667777', address='北京市朝阳区汽配城B区', credit_level=4),
            Supplier(name='南方汽配批发中心', code='SUP003', contact_person='林经理', phone='020-88889999', address='广州市白云区汽配城', credit_level=3),
        ]
        db.session.add_all(suppliers)
        db.session.flush()
        sup_map = {s.code: s.id for s in suppliers}

        # ========== 7. 配件库存 ==========
        parts_data = [
            ('ENG001', '机油滤清器', 'ENGINE', '博世', '通用型', '个', 25, 45, 80, 10),
            ('ENG002', '空气滤清器', 'ENGINE', '马勒', '通用型', '个', 35, 65, 50, 10),
            ('ENG003', '火花塞', 'ENGINE', 'NGK', '铱金', '支', 30, 60, 120, 20),
            ('ENG004', '正时皮带', 'ENGINE', '盖茨', '通用型', '条', 120, 220, 30, 5),
            ('CHA001', '刹车片（前）', 'CHASSIS', '博世', '陶瓷', '套', 150, 280, 40, 8),
            ('CHA002', '刹车片（后）', 'CHASSIS', '博世', '陶瓷', '套', 120, 230, 35, 8),
            ('CHA003', '刹车盘（前）', 'CHASSIS', 'ATE', '通风盘', '个', 280, 450, 20, 5),
            ('CHA004', '减震器', 'CHASSIS', 'KYB', '前减', '支', 350, 580, 15, 3),
            ('ELC001', '蓄电池', 'ELECTRICAL', '风帆', '60Ah', '个', 380, 550, 25, 5),
            ('ELC002', 'LED大灯总成', 'ELECTRICAL', '欧司朗', 'H7', '只', 450, 780, 10, 3),
            ('BDY001', '雨刮片', 'BODY', '博世', '通用型', '对', 40, 75, 60, 15),
            ('BDY002', '后视镜总成', 'BODY', '原厂', '电动折叠', '个', 500, 850, 8, 2),
            ('MNT001', '全合成机油 5W-30', 'MAINT', '美孚', '4L装', '桶', 180, 320, 100, 20),
            ('MNT002', '防冻液', 'MAINT', '巴斯夫', '红色 -35℃', '桶', 60, 110, 40, 10),
            ('MNT003', '空调滤清器', 'MAINT', '马勒', '活性炭', '个', 30, 55, 45, 10),
        ]
        parts_list = []
        for pno, name, cat_code, brand, model, unit, buy, sell, stock, min_s in parts_data:
            p = Part(
                part_no=pno, name=name, category_id=cat_map[cat_code],
                brand=brand, model=model, unit=unit,
                purchase_price=buy, selling_price=sell,
                stock_quantity=stock, min_stock=min_s, max_stock=stock*3,
                warehouse='主仓库', location=f'{cat_code}-A{random.randint(1,5)}-{random.randint(1,20)}',
                status=1
            )
            parts_list.append(p)
        db.session.add_all(parts_list)
        db.session.flush()
        part_map = {p.part_no: p.id for p in parts_list}
        # 让部分配件库存低于预警值
        parts_list[3].stock_quantity = 2  # 正时皮带
        parts_list[7].stock_quantity = 1  # 减震器
        parts_list[11].stock_quantity = 1  # 后视镜
        db.session.flush()
        print("✅ 配件创建完成")

        # ========== 8. 维修工单 ==========
        service_types = ['保养', '维修', '钣金', '喷漆', '检测']
        fault_descs = [
            '发动机异响，怠速不稳',
            '刹车偏软，需更换刹车片',
            '空调不制冷，检查冷媒',
            '常规保养，更换机油机滤',
            '底盘异响，检查悬挂系统',
            '变速箱换挡顿挫',
            '转向沉重，检查助力系统',
            '车身划痕修复',
            '大灯不亮，检查电路',
            '轮胎磨损严重，需要更换',
            '发动机故障灯亮',
            '雨刮器不工作',
            '电瓶亏电，无法启动',
            '定期保养5000公里',
            '事故维修，前保险杠更换',
        ]
        statuses = [0, 1, 2, 3, 4, 5, 6, 7]

        work_orders = []
        for i in range(25):
            cust = random.choice(customers_data)
            veh = random.choice([v for v in vehicles_data if v.customer_id == cust.id])
            status = random.choice(statuses)
            created = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))

            labor_cost = round(random.uniform(200, 3000), 2)
            parts_cost = round(random.uniform(100, 5000), 2)
            other_cost = round(random.uniform(0, 500), 2)
            actual_cost = round(labor_cost + parts_cost + other_cost, 2)
            discount_rate = random.choice([1, 1, 1, 0.95, 0.9, 0.85])
            discount_amount = round(actual_cost * (1 - discount_rate), 2)
            total_amount = round(actual_cost - discount_amount, 2)

            wo = WorkOrder(
                order_no=f'WO{created.strftime("%Y%m%d")}{10000 + i}',
                customer_id=cust.id, vehicle_id=veh.id,
                mileage=veh.mileage + random.randint(-1000, 5000),
                status=status,
                service_type=random.choice(service_types),
                fault_description=random.choice(fault_descs),
                estimated_cost=round(actual_cost * random.uniform(0.8, 1.2), 2),
                actual_cost=actual_cost,
                parts_cost=parts_cost,
                labor_cost=labor_cost,
                other_cost=other_cost,
                discount_rate=discount_rate,
                discount_amount=discount_amount,
                total_amount=total_amount,
                received_amount=round(total_amount, 2) if status >= 6 and random.random() > 0.2 else 0,
                is_paid=1 if status >= 6 and random.random() > 0.2 else 0,
                created_by=user_map['wang_advisor'],
                created_at=created,
            )
            if status >= 1:
                wo.confirmed_by = user_map['li_manager']
                wo.confirmed_at = created + timedelta(minutes=random.randint(10, 60))
            if status >= 2:
                wo.assigned_by = user_map['li_manager']
                wo.assigned_at = wo.confirmed_at + timedelta(minutes=random.randint(10, 30))
            if status >= 5:
                wo.completed_by = random.choice([t.id for t in techs])
                wo.completed_at = wo.assigned_at + timedelta(hours=random.randint(2, 24)) if wo.assigned_at else created + timedelta(hours=5)
            if status >= 6:
                wo.settled_by = user_map['zhao_finance']
                wo.settled_at = (wo.completed_at or created) + timedelta(minutes=random.randint(10, 60))

            work_orders.append(wo)
        db.session.add_all(work_orders)
        db.session.flush()
        wo_map = {wo.order_no: wo.id for wo in work_orders}
        print("✅ 工单创建完成")

        # ========== 9. 维修项目 ==========
        repair_items_list = [
            ('更换机油机滤', '保养', 1.5, 180),
            ('更换空气滤清器', '保养', 0.5, 60),
            ('更换刹车片', '维修', 2.0, 250),
            ('更换火花塞', '维修', 1.0, 150),
            ('空调系统检测加冷媒', '维修', 1.5, 200),
            ('更换正时皮带', '维修', 4.0, 500),
            ('底盘检查调整', '检测', 1.0, 120),
            ('全车电脑检测', '检测', 0.5, 80),
            ('更换雨刮片', '保养', 0.2, 30),
            ('更换蓄电池', '电气', 0.5, 80),
            ('钣金修复', '钣金', 6.0, 800),
            ('喷漆修复', '喷漆', 4.0, 600),
        ]

        for wo in work_orders:
            num_items = random.randint(1, 3)
            chosen = random.sample(repair_items_list, min(num_items, len(repair_items_list)))
            for item_name, cat, hours, price in chosen:
                tech = random.choice(techs)
                ri = RepairItem(
                    order_id=wo.id,
                    item_name=item_name, category=cat,
                    labor_hours=hours, labor_price=price,
                    labor_amount=round(hours * price, 2),
                    technician_id=tech.id, technician_name=tech.name,
                    status=2 if wo.status >= 5 else (1 if wo.status >= 3 else 0),
                    start_time=wo.confirmed_at if wo.confirmed_at else wo.created_at,
                    end_time=wo.completed_at if wo.completed_at else None,
                )
                db.session.add(ri)
        db.session.flush()
        print("✅ 维修项目创建完成")

        # ========== 10. 收款记录 ==========
        payment_methods = ['cash', 'wechat', 'alipay', 'bank']
        payment_method_names = {'cash': '现金', 'wechat': '微信', 'alipay': '支付宝', 'bank': '银行卡'}

        for wo in work_orders:
            if wo.is_paid:
                days_ago = random.randint(0, 25)
                pay = Payment(
                    payment_no=f'PAY{date.today() - timedelta(days=days_ago)}{random.randint(1000,9999)}',
                    order_id=wo.id,
                    customer_id=wo.customer_id,
                    amount=wo.total_amount,
                    payment_method=random.choice(payment_methods),
                    payment_type='repair',
                    payer_name=wo.customer.name if wo.customer else None,
                    status=1,
                    received_by=user_map['zhao_finance'],
                    received_at=wo.settled_at if wo.settled_at else datetime.now() - timedelta(days=days_ago),
                )
                db.session.add(pay)
        db.session.flush()
        print("✅ 收款记录创建完成")

        # ========== 11. 预约 ==========
        for i in range(8):
            cust = random.choice(customers_data[:10])
            veh = random.choice([v for v in vehicles_data if v.customer_id == cust.id])
            apt_date = date.today() + timedelta(days=random.randint(0, 7))
            apt = Appointment(
                appointment_no=f'APT{apt_date.strftime("%Y%m%d")}{random.randint(100,999)}',
                customer_id=cust.id, vehicle_id=veh.id,
                phone=cust.phone,
                appointment_date=apt_date,
                appointment_time=dt_time(random.randint(8,16), random.choice([0,30])),
                service_type=random.choice(service_types),
                description=random.choice(fault_descs[:5]),
                status=random.choice([0, 0, 1, 2, 3]),
                confirm_by=user_map['wang_advisor'] if random.random() > 0.5 else None,
                created_at=datetime.now() - timedelta(days=random.randint(0, 5))
            )
            db.session.add(apt)
        db.session.flush()
        print("✅ 预约创建完成")

        # ========== 12. 入库记录 ==========
        for i in range(5):
            in_date = datetime.now() - timedelta(days=random.randint(1, 30))
            inbound = PartsInbound(
                inbound_no=f'PI{in_date.strftime("%Y%m%d")}{random.randint(100,999)}',
                supplier_id=random.choice(list(sup_map.values())),
                total_amount=0, total_quantity=0,
                status=1, inbound_by=user_map['chen_parts'],
                inbound_at=in_date,
                remark='常规采购入库',
                created_by=user_map['chen_parts'],
                created_at=in_date,
            )
            db.session.add(inbound)
            db.session.flush()

            total_amt = 0
            total_qty = 0
            chosen_parts = random.sample(parts_list, random.randint(3, 6))
            for p in chosen_parts:
                qty = random.randint(5, 30)
                price = float(p.purchase_price)
                total = round(qty * price, 2)
                detail = PartsInboundDetail(
                    inbound_id=inbound.id, part_id=p.id,
                    quantity=qty, unit_price=price, total_price=total
                )
                db.session.add(detail)
                total_amt += total
                total_qty += qty

            inbound.total_amount = round(total_amt, 2)
            inbound.total_quantity = total_qty
        db.session.flush()
        print("✅ 入库记录创建完成")

        # ========== 13. 出库记录 ==========
        for wo in random.sample(work_orders, min(10, len(work_orders))):
            if wo.parts_cost and wo.parts_cost > 0:
                out_date = wo.confirmed_at or wo.created_at
                outbound = PartsOutbound(
                    outbound_no=f'PO{out_date.strftime("%Y%m%d")}{random.randint(100,999)}',
                    order_id=wo.id,
                    outbound_type='repair',
                    total_amount=0, total_quantity=0,
                    status=1, outbound_by=user_map['chen_parts'],
                    outbound_at=out_date,
                    remark=f'工单{wo.order_no}维修出库',
                    created_by=user_map['chen_parts'],
                    created_at=out_date,
                )
                db.session.add(outbound)
                db.session.flush()

                total_amt = 0
                total_qty = 0
                chosen_parts = random.sample(parts_list, random.randint(1, 3))
                for p in chosen_parts:
                    qty = random.randint(1, 4)
                    price = float(p.purchase_price)
                    total = round(qty * float(p.selling_price), 2)
                    detail = PartsOutboundDetail(
                        outbound_id=outbound.id, part_id=p.id,
                        quantity=qty, unit_price=price, total_price=total
                    )
                    db.session.add(detail)
                    total_amt += total
                    total_qty += qty

                outbound.total_amount = round(total_amt, 2)
                outbound.total_quantity = total_qty
        db.session.flush()
        print("✅ 出库记录创建完成")

        # ========== 14. 系统配置 ==========
        configs = [
            SystemConfig(config_key='shop_name', config_value='鑫达汽车4S店', config_type='string', description='店铺名称', group_name='basic'),
            SystemConfig(config_key='shop_address', config_value='北京市朝阳区建国路88号', config_type='string', description='店铺地址', group_name='basic'),
            SystemConfig(config_key='shop_phone', config_value='400-888-9999', config_type='string', description='联系电话', group_name='basic'),
            SystemConfig(config_key='default_labor_rate', config_value='200', config_type='number', description='默认工时单价', group_name='price'),
            SystemConfig(config_key='tax_rate', config_value='0.13', config_type='number', description='税率', group_name='price'),
            SystemConfig(config_key='stock_warning_enabled', config_value='true', config_type='boolean', description='库存预警', group_name='stock'),
            SystemConfig(config_key='backup_retention_days', config_value='30', config_type='number', description='备份保留天数', group_name='system'),
        ]
        db.session.add_all(configs)
        print("✅ 系统配置创建完成")

        # ========== 15. 操作日志 ==========
        log_actions = [
            ('login', 'auth', '用户登录'),
            ('create', 'customer', '创建客户'),
            ('create', 'work_order', '创建工单'),
            ('update', 'work_order', '更新工单状态'),
            ('create', 'payment', '创建收款'),
            ('create', 'inbound', '配件入库'),
        ]
        for i in range(20):
            action, module, desc = random.choice(log_actions)
            user = random.choice(users_data)
            log = OperationLog(
                user_id=user.id, username=user.username,
                action=action, module=module, description=desc,
                ip_address=f'192.168.1.{random.randint(1,255)}',
                created_at=datetime.now() - timedelta(days=random.randint(0, 15), hours=random.randint(0, 23))
            )
            db.session.add(log)
        print("✅ 操作日志创建完成")

        # ========== 提交 ==========
        db.session.commit()
        print("\n🎉 示例数据填充完成！")
        print(f"   角色: {len(roles_data)} 个")
        print(f"   用户: {len(users_data)} 个")
        print(f"   员工: {len(employees_data)} 个")
        print(f"   客户: {len(customers_data)} 个")
        print(f"   车辆: {len(vehicles_data)} 辆")
        print(f"   配件: {len(parts_list)} 种")
        print(f"   工单: {len(work_orders)} 个")
        print(f"   预约: 8 个")
        print(f"   入库: 5 单")
        print(f"   出库: ~10 单")
        print(f"   收款: {sum(1 for wo in work_orders if wo.is_paid)} 笔")

if __name__ == '__main__':
    seed()
