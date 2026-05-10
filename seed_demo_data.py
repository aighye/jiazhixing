"""嘉之星管理系统 - 示例数据初始化脚本"""
from app import create_app
from app.extensions import db
from app.models.customer import Customer, Vehicle
from app.models.parts import PartsCategory, Supplier, Part
from app.models.user import User, Role
from app.models.work_order import RepairItemTemplate
from datetime import datetime, date
import json

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin_id = admin.id if admin else 1

    # ========== 配件分类 ==========
    print("创建配件分类...")
    categories_data = [
        {"name": "发动机配件", "code": "ENGINE", "parent_id": 0, "level": 1, "sort": 1},
        {"name": "制动系统", "code": "BRAKE", "parent_id": 0, "level": 1, "sort": 2},
        {"name": "电气系统", "code": "ELECTRIC", "parent_id": 0, "level": 1, "sort": 3},
        {"name": "底盘悬挂", "code": "CHASSIS", "parent_id": 0, "level": 1, "sort": 4},
        {"name": "车身外观", "code": "BODY", "parent_id": 0, "level": 1, "sort": 5},
        {"name": "内饰精品", "code": "INTERIOR", "parent_id": 0, "level": 1, "sort": 6},
        {"name": "油液滤芯", "code": "FILTER", "parent_id": 0, "level": 1, "sort": 7},
        {"name": "空调系统", "code": "AC", "parent_id": 0, "level": 1, "sort": 8},
    ]
    categories = []
    for c in categories_data:
        existing = PartsCategory.query.filter_by(code=c["code"]).first()
        if not existing:
            cat = PartsCategory(**c, status=1)
            db.session.add(cat)
            categories.append(cat)
        else:
            categories.append(existing)
    db.session.flush()

    # ========== 供应商 ==========
    print("创建供应商...")
    suppliers_data = [
        {"name": "博世贸易（上海）有限公司", "code": "SUP-BOSCH", "contact_person": "王建国", "phone": "021-61806000", "email": "sales@bosch.com.cn", "address": "上海市浦东新区陆家嘴", "bank_name": "中国银行上海分行", "bank_account": "6228480031234567890", "credit_level": 5, "remark": "全球知名汽车零部件供应商"},
        {"name": "电装（中国）投资有限公司", "code": "SUP-DENSO", "contact_person": "李明辉", "phone": "010-65908888", "email": "info@denso.com.cn", "address": "北京市朝阳区建国路", "bank_name": "工商银行北京分行", "bank_account": "6222021234567890123", "credit_level": 5, "remark": "日本电装中国总部"},
        {"name": "广州本田汽车零部件有限公司", "code": "SUP-HONDA", "contact_person": "陈伟强", "phone": "020-82218888", "email": "parts@honda-guangzhou.com", "address": "广州市黄埔区", "bank_name": "建设银行广州分行", "bank_account": "6227001234567890456", "credit_level": 4, "remark": "本田原厂件供应商"},
        {"name": "一汽大众零部件供应中心", "code": "SUP-FAW-VW", "contact_person": "张志远", "phone": "0431-85998888", "email": "parts@faw-vw.com", "address": "长春市汽车产业开发区", "bank_name": "农业银行长春分行", "bank_account": "6228481234567890789", "credit_level": 4, "remark": "大众原厂件供应"},
        {"name": "浙江万向精工有限公司", "code": "SUP-WANXIANG", "contact_person": "赵德明", "phone": "0571-82888888", "email": "sales@wanxiang.com", "address": "杭州市萧山区", "bank_name": "招商银行杭州分行", "bank_account": "6225881234567890123", "credit_level": 3, "remark": "底盘件专业供应商"},
    ]
    suppliers = []
    for s in suppliers_data:
        existing = Supplier.query.filter_by(code=s["code"]).first()
        if not existing:
            sup = Supplier(**s, status=1)
            db.session.add(sup)
            suppliers.append(sup)
        else:
            suppliers.append(existing)
    db.session.flush()

    # ========== 配件档案 ==========
    print("创建配件档案...")
    parts_data = [
        {"part_no": "PJ-ENG-001", "name": "机油滤清器", "pinyin_code": "JYLQ", "brand": "博世", "specification": "F026407005", "unit": "个", "purchase_price": 18.00, "selling_price": 35.00, "network_price": 30.00, "stock_quantity": 120, "min_stock": 20, "max_stock": 200, "safety_stock": 15, "min_package_qty": 10, "warehouse": "备件库", "location": "A-01-01", "factory_code": "W914/4", "origin": "国产", "applicable_vehicle": "通用", "category1": "油液滤芯", "category2": "滤清器"},
        {"part_no": "PJ-ENG-002", "name": "空气滤清器", "pinyin_code": "KQLQ", "brand": "曼牌", "specification": "C27030", "unit": "个", "purchase_price": 35.00, "selling_price": 68.00, "network_price": 58.00, "stock_quantity": 80, "min_stock": 15, "max_stock": 150, "safety_stock": 10, "min_package_qty": 5, "warehouse": "备件库", "location": "A-01-02", "factory_code": "1H0129620", "origin": "进口", "applicable_vehicle": "大众系列", "category1": "油液滤芯", "category2": "滤清器"},
        {"part_no": "PJ-ENG-003", "name": "火花塞", "pinyin_code": "HHS", "brand": "NGK", "specification": "PFR7S8EG", "unit": "支", "purchase_price": 28.00, "selling_price": 55.00, "network_price": 48.00, "stock_quantity": 200, "min_stock": 40, "max_stock": 400, "safety_stock": 30, "min_package_qty": 4, "warehouse": "备件库", "location": "A-02-01", "factory_code": "SILZKR8B8S", "origin": "日本", "applicable_vehicle": "本田系列", "category1": "发动机配件", "category2": "点火系统"},
        {"part_no": "PJ-BRK-001", "name": "前刹车片", "pinyin_code": "QSC", "brand": "博世", "specification": "BC956", "unit": "套", "purchase_price": 120.00, "selling_price": 240.00, "network_price": 210.00, "stock_quantity": 45, "min_stock": 10, "max_stock": 80, "safety_stock": 8, "min_package_qty": 1, "warehouse": "备件库", "location": "B-01-01", "factory_code": "06D698151F", "origin": "国产", "applicable_vehicle": "大众系列", "category1": "制动系统", "category2": "刹车片"},
        {"part_no": "PJ-BRK-002", "name": "后刹车片", "pinyin_code": "HSC", "brand": "博世", "specification": "BC905", "unit": "套", "purchase_price": 95.00, "selling_price": 190.00, "network_price": 165.00, "stock_quantity": 38, "min_stock": 10, "max_stock": 60, "safety_stock": 8, "min_package_qty": 1, "warehouse": "备件库", "location": "B-01-02", "factory_code": "06D698521", "origin": "国产", "applicable_vehicle": "大众系列", "category1": "制动系统", "category2": "刹车片"},
        {"part_no": "PJ-BRK-003", "name": "刹车盘（前）", "pinyin_code": "QSCP", "brand": "TRW", "specification": "DF4391", "unit": "个", "purchase_price": 180.00, "selling_price": 360.00, "network_price": 320.00, "stock_quantity": 22, "min_stock": 5, "max_stock": 40, "safety_stock": 4, "min_package_qty": 1, "warehouse": "备件库", "location": "B-02-01", "factory_code": "5C0615301A", "origin": "国产", "applicable_vehicle": "大众系列", "category1": "制动系统", "category2": "刹车盘"},
        {"part_no": "PJ-ELC-001", "name": "蓄电池", "pinyin_code": "XDC", "brand": "风帆", "specification": "6-QW-60", "unit": "个", "purchase_price": 280.00, "selling_price": 520.00, "network_price": 460.00, "stock_quantity": 15, "min_stock": 5, "max_stock": 30, "safety_stock": 3, "min_package_qty": 1, "warehouse": "备件库", "location": "C-01-01", "factory_code": "12V60Ah", "origin": "国产", "applicable_vehicle": "通用", "category1": "电气系统", "category2": "蓄电池"},
        {"part_no": "PJ-ELC-002", "name": "远光灯泡", "pinyin_code": "YGDP", "brand": "飞利浦", "specification": "H7 12V55W", "unit": "个", "purchase_price": 15.00, "selling_price": 30.00, "network_price": 25.00, "stock_quantity": 150, "min_stock": 30, "max_stock": 300, "safety_stock": 20, "min_package_qty": 10, "warehouse": "备件库", "location": "C-02-01", "factory_code": "12972PRC", "origin": "国产", "applicable_vehicle": "通用", "category1": "电气系统", "category2": "灯泡"},
        {"part_no": "PJ-CHS-001", "name": "减震器（前）", "pinyin_code": "QJZQ", "brand": "萨克斯", "specification": "313421", "unit": "支", "purchase_price": 320.00, "selling_price": 620.00, "network_price": 550.00, "stock_quantity": 12, "min_stock": 4, "max_stock": 20, "safety_stock": 3, "min_package_qty": 1, "warehouse": "备件库", "location": "D-01-01", "factory_code": "5C0413023B", "origin": "德国", "applicable_vehicle": "大众系列", "category1": "底盘悬挂", "category2": "减震器"},
        {"part_no": "PJ-FLR-001", "name": "5W-30全合成机油", "pinyin_code": "JY", "brand": "嘉实多", "specification": "4L装", "unit": "桶", "purchase_price": 168.00, "selling_price": 328.00, "network_price": 288.00, "stock_quantity": 60, "min_stock": 15, "max_stock": 100, "safety_stock": 10, "min_package_qty": 6, "warehouse": "油液库", "location": "E-01-01", "factory_code": "EDGE5W30", "origin": "进口", "applicable_vehicle": "通用", "category1": "油液滤芯", "category2": "机油"},
        {"part_no": "PJ-FLR-002", "name": "防冻液", "pinyin_code": "FDY", "brand": "百适通", "specification": "4L装", "unit": "桶", "purchase_price": 65.00, "selling_price": 128.00, "network_price": 108.00, "stock_quantity": 40, "min_stock": 10, "max_stock": 80, "safety_stock": 8, "min_package_qty": 4, "warehouse": "油液库", "location": "E-01-02", "factory_code": "P-OAT", "origin": "进口", "applicable_vehicle": "通用", "category1": "油液滤芯", "category2": "防冻液"},
        {"part_no": "PJ-FLR-003", "name": "变速箱油", "pinyin_code": "BSXY", "brand": "爱信", "specification": "1L装", "unit": "瓶", "purchase_price": 55.00, "selling_price": 108.00, "network_price": 95.00, "stock_quantity": 50, "min_stock": 10, "max_stock": 100, "safety_stock": 8, "min_package_qty": 12, "warehouse": "油液库", "location": "E-02-01", "factory_code": "AFW+", "origin": "日本", "applicable_vehicle": "通用", "category1": "油液滤芯", "category2": "变速箱油"},
        {"part_no": "PJ-BDY-001", "name": "前保险杠", "pinyin_code": "QBXG", "brand": "原厂", "specification": "喷漆件", "unit": "个", "purchase_price": 680.00, "selling_price": 1380.00, "network_price": 1200.00, "stock_quantity": 5, "min_stock": 2, "max_stock": 10, "safety_stock": 1, "min_package_qty": 1, "warehouse": "车身库", "location": "F-01-01", "factory_code": "5C0807221A", "origin": "国产", "applicable_vehicle": "大众系列", "category1": "车身外观", "category2": "保险杠"},
        {"part_no": "PJ-AC-001", "name": "空调滤清器", "pinyin_code": "KTLQ", "brand": "曼牌", "specification": "CUK2202", "unit": "个", "purchase_price": 42.00, "selling_price": 85.00, "network_price": 72.00, "stock_quantity": 90, "min_stock": 20, "max_stock": 150, "safety_stock": 15, "min_package_qty": 5, "warehouse": "备件库", "location": "A-01-03", "factory_code": "5Q0129620", "origin": "进口", "applicable_vehicle": "大众系列", "category1": "空调系统", "category2": "滤清器"},
        {"part_no": "PJ-INT-001", "name": "车载空气净化器", "pinyin_code": "KJHQ", "brand": "3M", "specification": "PN38803", "unit": "台", "purchase_price": 180.00, "selling_price": 368.00, "network_price": 320.00, "stock_quantity": 8, "min_stock": 3, "max_stock": 20, "safety_stock": 2, "min_package_qty": 1, "warehouse": "精品库", "boutique_location": "G-01-01", "origin": "国产", "applicable_vehicle": "通用", "category1": "内饰精品", "category2": "净化器"},
    ]
    parts = []
    for i, p in enumerate(parts_data):
        existing = Part.query.filter_by(part_no=p["part_no"]).first()
        if not existing:
            cat_idx = min(i, len(categories) - 1)
            part = Part(
                category_id=categories[cat_idx].id,
                status=1,
                **p
            )
            db.session.add(part)
            parts.append(part)
        else:
            parts.append(existing)
    db.session.flush()

    # ========== 保险公司 ==========
    print("创建保险公司...")
    from app.models.dict import InsuranceCompany, ClaimManufacturer
    insurance_data = [
        {"name": "中国人民财产保险", "code": "INS-PICC", "contact_person": "刘保险", "contact_phone": "95518", "remark": "人保财险，合作紧密"},
        {"name": "中国平安财产保险", "code": "INS-PINGAN", "contact_person": "张理赔", "contact_phone": "95511", "remark": "平安产险"},
        {"name": "中国太平洋财产保险", "code": "INS-CPIC", "contact_person": "王定损", "contact_phone": "95500", "remark": "太保产险"},
        {"name": "中国人寿财产保险", "code": "INS-CLIC", "contact_person": "赵服务", "contact_phone": "95519", "remark": "国寿财险"},
    ]
    for ins in insurance_data:
        existing = InsuranceCompany.query.filter_by(code=ins["code"]).first()
        if not existing:
            ic = InsuranceCompany(status=1, **ins)
            db.session.add(ic)
    db.session.flush()

    # ========== 索赔厂家 ==========
    print("创建索赔厂家...")
    claim_data = [
        {"name": "一汽-大众汽车有限公司", "code": "CLM-FAW-VW", "contact_person": "孙索赔", "contact_phone": "0431-85990000", "remark": "大众品牌索赔"},
        {"name": "广汽本田汽车有限公司", "code": "CLM-GHAC", "contact_person": "周保修", "contact_phone": "020-82218888", "remark": "本田品牌索赔"},
        {"name": "上汽通用汽车有限公司", "code": "CLM-SGM", "contact_person": "吴质保", "contact_phone": "021-28902888", "remark": "别克/雪佛兰品牌索赔"},
        {"name": "北京奔驰汽车有限公司", "code": "CLM-BBAC", "contact_person": "郑保修", "contact_phone": "010-67828888", "remark": "奔驰品牌索赔"},
    ]
    for clm in claim_data:
        existing = ClaimManufacturer.query.filter_by(code=clm["code"]).first()
        if not existing:
            cm = ClaimManufacturer(status=1, **clm)
            db.session.add(cm)
    db.session.flush()

    # ========== 用户 ==========
    print("创建用户...")
    roles = {r.code: r.id for r in Role.query.all()}
    users_data = [
        {"username": "manager", "real_name": "李经理", "phone": "13800000001", "email": "manager@jzx.com", "role_id": roles.get("manager", 2), "department": "售后服务部", "position": "服务经理", "employee_type": "正式", "employee_no": "EMP001", "level": "高级", "title": "服务经理"},
        {"username": "advisor1", "real_name": "王顾问", "phone": "13800000002", "email": "advisor1@jzx.com", "role_id": roles.get("advisor", 3), "department": "售后服务部", "position": "服务顾问", "employee_type": "正式", "employee_no": "EMP002", "level": "中级", "title": "服务顾问"},
        {"username": "advisor2", "real_name": "陈顾问", "phone": "13800000003", "email": "advisor2@jzx.com", "role_id": roles.get("advisor", 3), "department": "售后服务部", "position": "服务顾问", "employee_type": "正式", "employee_no": "EMP003", "level": "初级", "title": "服务顾问"},
        {"username": "tech1", "real_name": "张师傅", "phone": "13800000004", "email": "tech1@jzx.com", "role_id": roles.get("technician", 4), "department": "维修车间", "position": "主修技师", "employee_type": "正式", "employee_no": "EMP004", "level": "高级", "title": "技师组长"},
        {"username": "tech2", "real_name": "刘师傅", "phone": "13800000005", "email": "tech2@jzx.com", "role_id": roles.get("technician", 4), "department": "维修车间", "position": "维修技师", "employee_type": "正式", "employee_no": "EMP005", "level": "中级", "title": "维修技师"},
        {"username": "tech3", "real_name": "黄师傅", "phone": "13800000006", "email": "tech3@jzx.com", "role_id": roles.get("technician", 4), "department": "维修车间", "position": "维修技师", "employee_type": "合同", "employee_no": "EMP006", "level": "初级", "title": "维修技师"},
        {"username": "parts_mgr", "real_name": "赵仓管", "phone": "13800000007", "email": "parts@jzx.com", "role_id": roles.get("parts_manager", 5), "department": "配件部", "position": "配件主管", "employee_type": "正式", "employee_no": "EMP007", "level": "高级", "title": "配件主管"},
        {"username": "finance1", "real_name": "孙会计", "phone": "13800000008", "email": "finance@jzx.com", "role_id": roles.get("finance", 6), "department": "财务部", "position": "财务专员", "employee_type": "正式", "employee_no": "EMP008", "level": "中级", "title": "会计"},
    ]
    for u in users_data:
        existing = User.query.filter_by(username=u["username"]).first()
        if not existing:
            user = User(
                gender=1, status=1, base_salary=0, hourly_rate=0,
                entry_date=date(2024, 1, 1),
                **u
            )
            user.set_password('123456')
            db.session.add(user)
    db.session.flush()

    # ========== 客户 ==========
    print("创建客户...")
    customers_data = [
        {"customer_no": "CUS-2024-001", "name": "张伟", "phone": "13901001001", "email": "zhangwei@qq.com", "gender": 1, "birthday": date(1985, 3, 15), "address": "北京市朝阳区建国路88号", "customer_type": 1, "vip_level": 2, "total_spending": 12580.00, "points": 1258, "remark": "老客户，定期保养"},
        {"customer_no": "CUS-2024-002", "name": "李娜", "phone": "13901001002", "email": "lina@163.com", "gender": 2, "birthday": date(1990, 7, 22), "address": "北京市海淀区中关村大街1号", "customer_type": 1, "vip_level": 1, "total_spending": 5680.00, "points": 568, "remark": ""},
        {"customer_no": "CUS-2024-003", "name": "王强", "phone": "13901001003", "email": "wangqiang@gmail.com", "gender": 1, "birthday": date(1978, 11, 8), "address": "北京市丰台区南三环西路16号", "customer_type": 2, "company_name": "北京万达科技有限公司", "vip_level": 3, "total_spending": 38900.00, "points": 3890, "remark": "公司车队客户，多台车辆"},
        {"customer_no": "CUS-2024-004", "name": "陈芳", "phone": "13901001004", "email": "chenfang@qq.com", "gender": 2, "birthday": date(1995, 1, 30), "address": "北京市西城区金融街9号", "customer_type": 1, "vip_level": 0, "total_spending": 1280.00, "points": 128, "remark": "新客户"},
        {"customer_no": "CUS-2024-005", "name": "刘洋", "phone": "13901001005", "email": "liuyang@outlook.com", "gender": 1, "birthday": date(1982, 5, 18), "address": "北京市东城区东直门内大街", "customer_type": 1, "vip_level": 2, "total_spending": 18760.00, "points": 1876, "remark": "推荐客户3位"},
        {"customer_no": "CUS-2024-006", "name": "赵敏", "phone": "13901001006", "email": "zhaomin@126.com", "gender": 2, "birthday": date(1988, 9, 12), "address": "北京市昌平区回龙观", "customer_type": 1, "vip_level": 1, "total_spending": 7350.00, "points": 735, "remark": ""},
        {"customer_no": "CUS-2024-007", "name": "孙鹏", "phone": "13901001007", "email": "sunpeng@qq.com", "gender": 1, "birthday": date(1975, 12, 25), "address": "北京市通州区新华大街", "customer_type": 2, "company_name": "顺达物流有限公司", "vip_level": 3, "total_spending": 52300.00, "points": 5230, "remark": "物流公司，维修频繁"},
        {"customer_no": "CUS-2024-008", "name": "周婷", "phone": "13901001008", "email": "zhouting@sina.com", "gender": 2, "birthday": date(1992, 4, 6), "address": "北京市大兴区黄村", "customer_type": 1, "vip_level": 0, "total_spending": 0, "points": 0, "remark": "首次到店"},
    ]
    customers = []
    for c in customers_data:
        existing = Customer.query.filter_by(customer_no=c["customer_no"]).first()
        if not existing:
            cust = Customer(status=1, created_by=admin_id, **c)
            db.session.add(cust)
            customers.append(cust)
        else:
            customers.append(existing)
    db.session.flush()

    # ========== 车辆 ==========
    print("创建车辆...")
    vehicles_data = [
        {"vehicle_no": "VCL-2024-001", "customer_id": None, "plate_number": "京A·88888", "vin": "LFV2A21K9G3010001", "brand": "大众", "model": "迈腾 380TSI", "year": 2023, "color": "极地白", "engine_no": "EA888G0123", "purchase_date": date(2023, 3, 15), "mileage": 28000, "insurance_date": date(2025, 3, 14), "inspection_date": date(2027, 3, 14), "remark": "定期保养客户"},
        {"vehicle_no": "VCL-2024-002", "customer_id": None, "plate_number": "京B·66666", "vin": "LHGCM8869G200002", "brand": "本田", "model": "雅阁 260TURBO", "year": 2022, "color": "星曜黑", "engine_no": "L15BN3002", "purchase_date": date(2022, 6, 20), "mileage": 35000, "insurance_date": date(2025, 6, 19), "inspection_date": date(2026, 6, 19), "remark": ""},
        {"vehicle_no": "VCL-2024-003", "customer_id": None, "plate_number": "京C·12345", "vin": "LFV3A28C0G3030003", "brand": "大众", "model": "帕萨特 330TSI", "year": 2021, "color": "钛金灰", "engine_no": "EA888G0456", "purchase_date": date(2021, 8, 10), "mileage": 52000, "insurance_date": date(2025, 8, 9), "inspection_date": date(2025, 8, 9), "remark": "公司用车"},
        {"vehicle_no": "VCL-2024-004", "customer_id": None, "plate_number": "京D·77777", "vin": "LSGPC54U9GF100004", "brand": "别克", "model": "君威 552T", "year": 2023, "color": "墨玉黑", "engine_no": "LFV00789", "purchase_date": date(2023, 11, 1), "mileage": 12000, "insurance_date": date(2025, 10, 31), "inspection_date": date(2027, 10, 31), "remark": "新车主"},
        {"vehicle_no": "VCL-2024-005", "customer_id": None, "plate_number": "京E·99999", "vin": "WVWZZZ3CZWE005005", "brand": "大众", "model": "途观L 380TSI", "year": 2020, "color": "玄武灰", "engine_no": "EA888G0789", "purchase_date": date(2020, 2, 28), "mileage": 68000, "insurance_date": date(2025, 2, 27), "inspection_date": date(2025, 2, 27), "remark": "出保车辆"},
        {"vehicle_no": "VCL-2024-006", "customer_id": None, "plate_number": "京F·33333", "vin": "LHGGM6660G0600006", "brand": "本田", "model": "CR-V 240TURBO", "year": 2022, "color": "彩晶黑", "engine_no": "L15BL006", "purchase_date": date(2022, 12, 15), "mileage": 22000, "insurance_date": date(2025, 12, 14), "inspection_date": date(2026, 12, 14), "remark": ""},
        {"vehicle_no": "VCL-2024-007", "customer_id": None, "plate_number": "京G·55555", "vin": "LFV2A21K5K3070007", "brand": "大众", "model": "速腾 280TSI", "year": 2024, "color": "海贝金", "engine_no": "EA211G011", "purchase_date": date(2024, 5, 8), "mileage": 5000, "insurance_date": date(2026, 5, 7), "inspection_date": date(2028, 5, 7), "remark": "新车首保"},
        {"vehicle_no": "VCL-2024-008", "customer_id": None, "plate_number": "京H·11111", "vin": "WBAJB1105CJ800008", "brand": "奔驰", "model": "C260L", "year": 2021, "color": "曜岩黑", "engine_no": "M2648008", "purchase_date": date(2021, 4, 22), "mileage": 45000, "insurance_date": date(2025, 4, 21), "inspection_date": date(2025, 4, 21), "remark": "高端客户"},
        {"vehicle_no": "VCL-2024-009", "customer_id": None, "plate_number": "京J·22222", "vin": "LSVAU2180N2090009", "brand": "大众", "model": "朗逸 1.5L", "year": 2023, "color": "谦雅紫", "engine_no": "EA211G022", "purchase_date": date(2023, 7, 10), "mileage": 18000, "insurance_date": date(2025, 7, 9), "inspection_date": date(2027, 7, 9), "remark": ""},
        {"vehicle_no": "VCL-2024-010", "customer_id": None, "plate_number": "京K·44444", "vin": "LHGCM6660L0100010", "brand": "本田", "model": "思域 240TURBO", "year": 2024, "color": "闪烈黄", "engine_no": "L15C8010", "purchase_date": date(2024, 9, 5), "mileage": 3000, "insurance_date": date(2026, 9, 4), "inspection_date": date(2028, 9, 4), "remark": "首保未做"},
    ]

    # Assign customer_id to vehicles
    for i, v in enumerate(vehicles_data):
        cust_idx = min(i, len(customers) - 1)
        v["customer_id"] = customers[cust_idx].id

    vehicles = []
    for v in vehicles_data:
        existing = Vehicle.query.filter_by(vehicle_no=v["vehicle_no"]).first()
        if not existing:
            veh = Vehicle(status=1, created_by=admin_id, **v)
            db.session.add(veh)
            vehicles.append(veh)
        else:
            vehicles.append(existing)
    db.session.flush()

    # ========== 维修项目模板 ==========
    print("创建维修项目模板...")
    templates_data = [
        {"item_name": "小保养（更换机油机滤）", "item_code": "WX-001", "category": "保养", "charge_type": "工时", "repair_category": "常规保养", "labor_hours": 1.0, "labor_price": 120.00, "description": "更换机油、机油滤清器，全车检查", "sort_order": 1},
        {"item_name": "大保养（更换机油三滤）", "item_code": "WX-002", "category": "保养", "charge_type": "工时", "repair_category": "常规保养", "labor_hours": 2.0, "labor_price": 240.00, "description": "更换机油、机滤、空滤、空调滤，全车检查", "sort_order": 2},
        {"item_name": "更换刹车片（前）", "item_code": "WX-003", "category": "制动", "charge_type": "工时", "repair_category": "制动维修", "labor_hours": 1.5, "labor_price": 180.00, "description": "更换前轮刹车片", "sort_order": 3},
        {"item_name": "更换刹车片（后）", "item_code": "WX-004", "category": "制动", "charge_type": "工时", "repair_category": "制动维修", "labor_hours": 1.5, "labor_price": 180.00, "description": "更换后轮刹车片", "sort_order": 4},
        {"item_name": "更换刹车盘（前）", "item_code": "WX-005", "category": "制动", "charge_type": "工时", "repair_category": "制动维修", "labor_hours": 2.0, "labor_price": 280.00, "description": "更换前轮刹车盘", "sort_order": 5},
        {"item_name": "更换蓄电池", "item_code": "WX-006", "category": "电气", "charge_type": "工时", "repair_category": "电气维修", "labor_hours": 0.5, "labor_price": 60.00, "description": "更换蓄电池，检测充电系统", "sort_order": 6},
        {"item_name": "更换火花塞", "item_code": "WX-007", "category": "发动机", "charge_type": "工时", "repair_category": "发动机维修", "labor_hours": 1.0, "labor_price": 120.00, "description": "更换全部火花塞", "sort_order": 7},
        {"item_name": "更换减震器（前单侧）", "item_code": "WX-008", "category": "底盘", "charge_type": "工时", "repair_category": "底盘维修", "labor_hours": 2.0, "labor_price": 300.00, "description": "更换前减震器", "sort_order": 8},
        {"item_name": "更换防冻液", "item_code": "WX-009", "category": "保养", "charge_type": "工时", "repair_category": "常规保养", "labor_hours": 1.0, "labor_price": 100.00, "description": "更换防冻液，排气检查", "sort_order": 9},
        {"item_name": "更换变速箱油", "item_code": "WX-010", "category": "保养", "charge_type": "工时", "repair_category": "常规保养", "labor_hours": 1.5, "labor_price": 200.00, "description": "更换变速箱油，检查变速箱", "sort_order": 10},
        {"item_name": "空调系统清洗", "item_code": "WX-011", "category": "空调", "charge_type": "工时", "repair_category": "空调维修", "labor_hours": 1.0, "labor_price": 150.00, "description": "空调管路清洗、杀菌、除味", "sort_order": 11},
        {"item_name": "更换前保险杠", "item_code": "WX-012", "category": "钣金", "charge_type": "工时", "repair_category": "钣金喷漆", "labor_hours": 4.0, "labor_price": 600.00, "description": "拆卸更换前保险杠，喷漆", "sort_order": 12},
        {"item_name": "四轮定位", "item_code": "WX-013", "category": "底盘", "charge_type": "工时", "repair_category": "底盘维修", "labor_hours": 1.0, "labor_price": 200.00, "description": "四轮定位检测调整", "sort_order": 13},
        {"item_name": "电脑诊断", "item_code": "WX-014", "category": "电气", "charge_type": "工时", "repair_category": "电气维修", "labor_hours": 0.5, "labor_price": 80.00, "description": "OBD电脑诊断，故障码读取", "sort_order": 14},
        {"item_name": "更换轮胎（单条）", "item_code": "WX-015", "category": "轮胎", "charge_type": "工时", "repair_category": "轮胎服务", "labor_hours": 0.5, "labor_price": 50.00, "description": "更换轮胎，动平衡", "sort_order": 15},
    ]
    for t in templates_data:
        existing = db.session.execute(
            db.text("SELECT id FROM repair_item_templates WHERE item_code=:code"),
            {"code": t["item_code"]}
        ).first()
        if not existing:
            db.session.execute(db.text(
                "INSERT INTO repair_item_templates (name, item_name, item_code, category, charge_type, repair_category, "
                "labor_hours, labor_price, description, status, sort_order, created_by) "
                "VALUES (:item_name, :item_name, :item_code, :category, :charge_type, :repair_category, "
                ":labor_hours, :labor_price, :description, 1, :sort_order, :created_by)"
            ), {**t, "created_by": admin_id})
    db.session.flush()

    # ========== 字典数据 ==========
    print("创建字典数据...")
    dict_data = [
        {"dict_type": "service_type", "dict_label": "常规保养", "dict_value": "常规保养", "sort": 1},
        {"dict_type": "service_type", "dict_label": "故障维修", "dict_value": "故障维修", "sort": 2},
        {"dict_type": "service_type", "dict_label": "事故维修", "dict_value": "事故维修", "sort": 3},
        {"dict_type": "service_type", "dict_label": "索赔维修", "dict_value": "索赔维修", "sort": 4},
        {"dict_type": "service_type", "dict_label": "年检", "dict_value": "年检", "sort": 5},
        {"dict_type": "payment_method", "dict_label": "现金", "dict_value": "cash", "sort": 1},
        {"dict_type": "payment_method", "dict_label": "微信", "dict_value": "wechat", "sort": 2},
        {"dict_type": "payment_method", "dict_label": "支付宝", "dict_value": "alipay", "sort": 3},
        {"dict_type": "payment_method", "dict_label": "银行卡", "dict_value": "bank_card", "sort": 4},
        {"dict_type": "payment_method", "dict_label": "保险理赔", "dict_value": "insurance", "sort": 5},
        {"dict_type": "vehicle_brand", "dict_label": "大众", "dict_value": "大众", "sort": 1},
        {"dict_type": "vehicle_brand", "dict_label": "本田", "dict_value": "本田", "sort": 2},
        {"dict_type": "vehicle_brand", "dict_label": "别克", "dict_value": "别克", "sort": 3},
        {"dict_type": "vehicle_brand", "dict_label": "奔驰", "dict_value": "奔驰", "sort": 4},
        {"dict_type": "vehicle_brand", "dict_label": "宝马", "dict_value": "宝马", "sort": 5},
        {"dict_type": "vehicle_brand", "dict_label": "丰田", "dict_value": "丰田", "sort": 6},
    ]
    for d in dict_data:
        existing = db.session.execute(
            db.text("SELECT id FROM dict_items WHERE dict_type=:t AND dict_value=:v"),
            {"t": d["dict_type"], "v": d["dict_value"]}
        ).first()
        if not existing:
            db.session.execute(db.text(
                "INSERT INTO dict_items (dict_type, dict_label, dict_value, sort, status) "
                "VALUES (:dict_type, :dict_label, :dict_value, :sort, 1)"
            ), d)

    db.session.commit()
    print("\n✅ 示例数据创建完成！")
    print(f"  - 配件分类: {len(categories_data)} 条")
    print(f"  - 供应商: {len(suppliers_data)} 条")
    print(f"  - 配件档案: {len(parts_data)} 条")
    print(f"  - 保险公司: {len(insurance_data)} 条")
    print(f"  - 索赔厂家: {len(claim_data)} 条")
    print(f"  - 用户: {len(users_data)} 条")
    print(f"  - 客户: {len(customers_data)} 条")
    print(f"  - 车辆: {len(vehicles_data)} 条")
    print(f"  - 维修项目模板: {len(templates_data)} 条")
    print(f"  - 字典数据: {len(dict_data)} 条")
