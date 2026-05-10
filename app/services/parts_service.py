from datetime import datetime
from app.extensions import db
from app.models.parts import Part, PartsInbound, PartsInboundDetail, PartsOutbound, PartsOutboundDetail, StockMovement
from app.utils.helpers import generate_no, generate_seq_no

class PartsService:
    @staticmethod
    def inbound(data, user_id):
        """配件入库"""
        status = data.get('status', 1)  # 0=暂存, 1=确认入库
        inbound = PartsInbound(
            inbound_no=generate_seq_no('RU', PartsInbound, 'inbound_no'),
            supplier_id=data.get('supplier_id'),
            status=status,
            inbound_by=user_id,
            inbound_at=datetime.utcnow() if status == 1 else None,
            created_by=user_id,
            remark=data.get('remark'),
            invoice_type=data.get('invoice_type', '无发票'),
            tax_rate=data.get('tax_rate', 0)
        )
        db.session.add(inbound)

        total_amount = 0
        total_quantity = 0

        for item in data.get('items', []):
            part = Part.query.get(item['part_id'])
            if not part:
                continue

            qty = int(item['quantity'])
            price = round(float(item['unit_price']), 2)
            price_with_tax = round(float(item.get('unit_price_with_tax', 0)), 2)
            total = round(qty * price, 2)

            detail = PartsInboundDetail(
                inbound_id=inbound.id,
                part_id=part.id,
                quantity=qty,
                unit_price=price,
                unit_price_with_tax=price_with_tax,
                total_price=total,
                unit=item.get('unit', ''),
                location=item.get('location', '')
            )
            db.session.add(detail)

            # 确认入库时才更新库存
            if status == 1:
                # 更新库存 - 加权平均价
                old_qty = part.stock_quantity or 0
                old_price = float(part.purchase_price or 0)
                new_qty = old_qty + qty
                new_price = round((old_qty * old_price + qty * price) / new_qty, 2) if new_qty > 0 else price

                part.stock_quantity = new_qty
                part.purchase_price = new_price

                # 记录库存变动
                movement = StockMovement(
                    part_id=part.id,
                    movement_type='in',
                    reference_type='inbound',
                    reference_id=inbound.id,
                    quantity_before=old_qty,
                    quantity_change=qty,
                    quantity_after=new_qty,
                    price_before=old_price,
                    price_after=new_price,
                    operator_id=user_id,
                    remark=f'入库单号: {inbound.inbound_no}'
                )
                db.session.add(movement)

            total_amount += total
            total_quantity += qty

        inbound.total_amount = total_amount
        inbound.total_quantity = total_quantity
        db.session.commit()
        return inbound

    @staticmethod
    def update_inbound(id, data, user_id):
        """更新入库单（仅限暂存状态）"""
        inbound = PartsInbound.query.get_or_404(id)
        if inbound.status != 0:
            raise ValueError('只能修改暂存状态的入库单')

        status = data.get('status', 0)
        inbound.supplier_id = data.get('supplier_id')
        inbound.remark = data.get('remark')
        inbound.invoice_type = data.get('invoice_type', '无发票')
        inbound.tax_rate = data.get('tax_rate', 0)
        inbound.status = status
        if status == 1:
            inbound.inbound_at = datetime.utcnow()
            inbound.inbound_by = user_id

        # 删除旧明细
        PartsInboundDetail.query.filter_by(inbound_id=id).delete()

        total_amount = 0
        total_quantity = 0

        for item in data.get('items', []):
            part = Part.query.get(item['part_id'])
            if not part:
                continue

            qty = int(item['quantity'])
            price = round(float(item['unit_price']), 2)
            price_with_tax = round(float(item.get('unit_price_with_tax', 0)), 2)
            total = round(qty * price, 2)

            detail = PartsInboundDetail(
                inbound_id=inbound.id,
                part_id=part.id,
                quantity=qty,
                unit_price=price,
                unit_price_with_tax=price_with_tax,
                total_price=total,
                unit=item.get('unit', ''),
                location=item.get('location', '')
            )
            db.session.add(detail)

            # 确认入库时才更新库存
            if status == 1:
                old_qty = part.stock_quantity or 0
                old_price = float(part.purchase_price or 0)
                new_qty = old_qty + qty
                new_price = round((old_qty * old_price + qty * price) / new_qty, 2) if new_qty > 0 else price

                part.stock_quantity = new_qty
                part.purchase_price = new_price

                movement = StockMovement(
                    part_id=part.id,
                    movement_type='in',
                    reference_type='inbound',
                    reference_id=inbound.id,
                    quantity_before=old_qty,
                    quantity_change=qty,
                    quantity_after=new_qty,
                    price_before=old_price,
                    price_after=new_price,
                    operator_id=user_id,
                    remark=f'入库单号: {inbound.inbound_no}'
                )
                db.session.add(movement)

            total_amount += total
            total_quantity += qty

        inbound.total_amount = total_amount
        inbound.total_quantity = total_quantity
        db.session.commit()
        return inbound

    @staticmethod
    def outbound(data, user_id):
        """配件出库"""
        outbound = PartsOutbound(
            outbound_no=generate_seq_no('CHU', PartsOutbound, 'outbound_no'),
            order_id=data.get('order_id'),
            outbound_type=data.get('outbound_type', 'repair'),
            status=1,
            outbound_by=user_id,
            outbound_at=datetime.utcnow(),
            created_by=user_id,
            remark=data.get('remark')
        )
        db.session.add(outbound)

        total_amount = 0
        total_quantity = 0

        for item in data.get('items', []):
            part = Part.query.get(item['part_id'])
            qty = int(item['quantity'])
            if not part or part.stock_quantity < qty:
                continue

            price = float(part.purchase_price or 0)
            total = qty * float(part.selling_price or 0)

            detail = PartsOutboundDetail(
                outbound_id=outbound.id,
                part_id=part.id,
                quantity=qty,
                unit_price=price,
                total_price=total
            )
            db.session.add(detail)

            old_qty = part.stock_quantity
            part.stock_quantity = old_qty - qty

            movement = StockMovement(
                part_id=part.id,
                movement_type='out',
                reference_type='outbound',
                reference_id=outbound.id,
                quantity_before=old_qty,
                quantity_change=qty,
                quantity_after=old_qty - qty,
                price_before=price,
                price_after=price,
                operator_id=user_id,
                remark=f'出库单号: {outbound.outbound_no}'
            )
            db.session.add(movement)

            total_amount += total
            total_quantity += qty

        outbound.total_amount = total_amount
        outbound.total_quantity = total_quantity
        db.session.commit()
        return outbound

    @staticmethod
    def cancel_outbound(id):
        """取消出库单，回滚库存"""
        outbound = PartsOutbound.query.get_or_404(id)
        if outbound.status != 1:
            raise ValueError('只能取消已出库的单据')

        for detail in outbound.details.all():
            part = Part.query.get(detail.part_id)
            if part:
                old_qty = part.stock_quantity or 0
                qty = detail.quantity
                part.stock_quantity = old_qty + qty

                movement = StockMovement(
                    part_id=part.id,
                    movement_type='in',
                    reference_type='outbound_cancel',
                    reference_id=outbound.id,
                    quantity_before=old_qty,
                    quantity_change=qty,
                    quantity_after=old_qty + qty,
                    price_before=float(part.purchase_price or 0),
                    price_after=float(part.purchase_price or 0),
                    remark=f'取消出库单号: {outbound.outbound_no}'
                )
                db.session.add(movement)

        outbound.status = 2  # 已取消
        db.session.commit()
        return outbound

    @staticmethod
    def get_low_stock_parts():
        """获取库存预警配件"""
        return Part.query.filter(
            Part.status == 1,
            Part.stock_quantity <= Part.min_stock,
            Part.min_stock > 0
        ).all()
