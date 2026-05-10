from app.models.user import User, Role, OperationLog
from app.models.customer import Customer, Vehicle, Appointment
from app.models.work_order import WorkOrder, WorkOrderFlowLog, RepairItem, WorkOrderTechnician, WorkOrderPart, RepairItemTemplate
from app.models.parts import PartsCategory, Supplier, Part, PartsInbound, PartsInboundDetail, PartsOutbound, PartsOutboundDetail, StockMovement
from app.models.finance import Payment, Invoice
from app.models.employee import Employee, EmployeeLaborStat
from app.models.system import SystemConfig, BackupRecord
from app.models.dict import ClaimManufacturer, InsuranceCompany

__all__ = [
    'User', 'Role', 'OperationLog',
    'Customer', 'Vehicle', 'Appointment',
    'WorkOrder', 'WorkOrderFlowLog', 'RepairItem', 'WorkOrderTechnician', 'WorkOrderPart', 'RepairItemTemplate',
    'PartsCategory', 'Supplier', 'Part', 'PartsInbound', 'PartsInboundDetail',
    'PartsOutbound', 'PartsOutboundDetail', 'StockMovement',
    'Payment', 'Invoice',
    'Employee', 'EmployeeLaborStat',
    'SystemConfig', 'BackupRecord',
    'ClaimManufacturer', 'InsuranceCompany'
]
