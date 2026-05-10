"""Seed sample customers and vehicles data."""
from datetime import date
from app import create_app
from app.extensions import db
from app.models.customer import Customer, Vehicle

app = create_app()
with app.app_context():
    Vehicle.query.delete()
    Customer.query.delete()
    db.session.commit()

    customers_data = [
        {"name": "张伟", "phone": "13800138001", "customer_type": 1, "vip_level": 2,
         "total_spending": 25800, "points": 2580, "address": "北京市朝阳区建国路88号",
         "gender": 1, "birthday": date(1985, 3, 15), "company": None},
        {"name": "李娜", "phone": "13912345678", "customer_type": 1, "vip_level": 1,
         "total_spending": 8600, "points": 860, "address": "上海市浦东新区陆家嘴金融中心",
         "gender": 2, "birthday": date(1990, 7, 22), "company": None},
        {"name": "王强", "phone": "13698765432", "customer_type": 2, "vip_level": 0,
         "total_spending": 3200, "points": 320, "address": "广州市天河区天河路385号",
         "company": "华强贸易有限公司", "gender": 1, "birthday": date(1978, 11, 8)},
        {"name": "赵敏", "phone": "15855556666", "customer_type": 1, "vip_level": 3,
         "total_spending": 52000, "points": 5200, "address": "深圳市南山区科技园南区",
         "gender": 2, "birthday": date(1992, 5, 30), "company": None},
        {"name": "刘洋", "phone": "17788889999", "customer_type": 1, "vip_level": 0,
         "total_spending": 1500, "points": 150, "address": "成都市锦江区红星路三段",
         "gender": 1, "birthday": date(1995, 9, 12), "company": None},
        {"name": "陈秀英", "phone": "15033334444", "customer_type": 1, "vip_level": 1,
         "total_spending": 6800, "points": 680, "address": "杭州市西湖区文三路478号",
         "gender": 2, "birthday": date(1988, 2, 18), "company": None},
        {"name": "孙浩然", "phone": "18677778888", "customer_type": 2, "vip_level": 2,
         "total_spending": 18500, "points": 1850, "address": "武汉市洪山区珞喻路1037号",
         "company": "浩然建筑装饰工程公司", "gender": 1, "birthday": date(1982, 6, 25)},
        {"name": "周丽萍", "phone": "13566667777", "customer_type": 1, "vip_level": 0,
         "total_spending": 2800, "points": 280, "address": "南京市鼓楼区中山北路200号",
         "gender": 2, "birthday": date(1993, 12, 3), "company": None},
        {"name": "吴建国", "phone": "18922223333", "customer_type": 2, "vip_level": 1,
         "total_spending": 9200, "points": 920, "address": "西安市雁塔区长安南路",
         "company": "建国物流有限公司", "gender": 1, "birthday": date(1975, 8, 20)},
        {"name": "黄晓雪", "phone": "15344445555", "customer_type": 1, "vip_level": 0,
         "total_spending": 1200, "points": 120, "address": "长沙市岳麓区麓山南路",
         "gender": 2, "birthday": date(1997, 4, 10), "company": None},
        {"name": "马俊杰", "phone": "18711112222", "customer_type": 1, "vip_level": 2,
         "total_spending": 16800, "points": 1680, "address": "郑州市金水区花园路66号",
         "gender": 1, "birthday": date(1986, 10, 5), "company": None},
        {"name": "林小燕", "phone": "15988889999", "customer_type": 1, "vip_level": 0,
         "total_spending": 3500, "points": 350, "address": "厦门市思明区湖滨南路",
         "gender": 2, "birthday": date(1994, 7, 28), "company": None},
    ]

    customers = []
    for i, c in enumerate(customers_data):
        customer = Customer(
            customer_no=f"C20260509{str(i+1).zfill(3)}",
            name=c["name"],
            phone=c["phone"],
            email=f"customer{i+1}@example.com",
            gender=c["gender"],
            birthday=c["birthday"],
            address=c["address"],
            customer_type=c["customer_type"],
            company_name=c.get("company"),
            vip_level=c["vip_level"],
            total_spending=c["total_spending"],
            points=c["points"],
            remark="优质客户，定期保养" if c["vip_level"] >= 1 else "",
            status=1,
            created_by=1,
        )
        db.session.add(customer)
        customers.append(customer)

    db.session.flush()
    print(f"Added {len(customers)} customers")

    vehicles_data = [
        {"plate": "京A·88888", "brand": "宝马", "model": "530Li", "year": 2023,
         "color": "碳黑色", "vin": "LBVKY5108PSX00001", "engine": "B48B20G", "mileage": 18500},
        {"plate": "京A·66666", "brand": "奔驰", "model": "E300L", "year": 2022,
         "color": "北极白", "vin": "LE4ZG8DB5NL00002", "engine": "M264", "mileage": 32000},
        {"plate": "粤B·12345", "brand": "奥迪", "model": "A6L", "year": 2024,
         "color": "传奇黑", "vin": "LFV3A24G0P3000003", "engine": "DKW", "mileage": 8200},
        {"plate": "粤B·99999", "brand": "保时捷", "model": "Cayenne", "year": 2023,
         "color": "细花白", "vin": "WP1AA29Y38KA00004", "engine": "DCB", "mileage": 12500},
        {"plate": "川A·77777", "brand": "大众", "model": "帕萨特", "year": 2021,
         "color": "玄武黑", "vin": "LSVCH6A49MN00005", "engine": "DPL", "mileage": 45000},
        {"plate": "浙A·55555", "brand": "特斯拉", "model": "Model Y", "year": 2023,
         "color": "珍珠白", "vin": "LRWYGCFJ4PC00006", "engine": "EV", "mileage": 22000},
        {"plate": "鄂A·33333", "brand": "别克", "model": "GL8 ES陆尊", "year": 2022,
         "color": "琥珀金", "vin": "LSGUL83L5NG00007", "engine": "LXH", "mileage": 58000},
        {"plate": "苏A·22222", "brand": "本田", "model": "雅阁", "year": 2024,
         "color": "星月白", "vin": "LHGCR2643R2000008", "engine": "L15C", "mileage": 6300},
        {"plate": "陕A·11111", "brand": "丰田", "model": "汉兰达", "year": 2021,
         "color": "珍珠白", "vin": "LVGDN56A9MG00009", "engine": "8AR", "mileage": 62000},
        {"plate": "湘A·44444", "brand": "比亚迪", "model": "汉EV", "year": 2024,
         "color": "极光蓝", "vin": "LC0CE6CBXR0000010", "engine": "EV", "mileage": 5100},
        {"plate": "豫A·77777", "brand": "奥迪", "model": "Q5L", "year": 2022,
         "color": "天云灰", "vin": "LFV3B28RXN5000011", "engine": "DKW", "mileage": 28000},
        {"plate": "闽D·88888", "brand": "MINI", "model": "Cooper S", "year": 2023,
         "color": "英伦绿", "vin": "WMWXM910XRWZ00012", "engine": "B48A20", "mileage": 15000},
        {"plate": "京B·12345", "brand": "宝马", "model": "X5", "year": 2024,
         "color": "宝石青", "vin": "LX5VKY5108PSX00013", "engine": "B58B30", "mileage": 7200,
         "customer_idx": 0},
        {"plate": "沪A·34567", "brand": "奔驰", "model": "GLC 300", "year": 2023,
         "color": "皓沙银", "vin": "LE4WG8DB5NL00014", "engine": "M254", "mileage": 19500,
         "customer_idx": 1},
    ]

    import random
    vehicles = []
    for i, v in enumerate(vehicles_data):
        cid = customers[v.get("customer_idx", i % len(customers))].id
        vehicle = Vehicle(
            vehicle_no=f"V20260509{str(i+1).zfill(3)}",
            customer_id=cid,
            plate_number=v["plate"],
            vin=v["vin"],
            brand=v["brand"],
            model=v["model"],
            year=v["year"],
            color=v["color"],
            engine_no=v["engine"],
            purchase_date=date(v["year"], random.randint(1, 6), random.randint(1, 28)),
            mileage=v["mileage"],
            insurance_date=date(2025, random.randint(1, 12), random.randint(1, 28)),
            inspection_date=date(v["year"] + 2, random.randint(1, 12), random.randint(1, 28)),
            status=1,
            created_by=1,
        )
        db.session.add(vehicle)
        vehicles.append(vehicle)

    db.session.commit()
    print(f"Added {len(vehicles)} vehicles")
    print("Sample data inserted successfully!")
