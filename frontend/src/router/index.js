import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customer/CustomerList.vue'),
        meta: { title: '客户管理', perm: 'customer:read' }
      },
      {
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/customer/CustomerDetail.vue'),
        meta: { title: '客户详情', perm: 'customer:read' }
      },
      {
        path: 'vehicles',
        name: 'Vehicles',
        component: () => import('@/views/customer/VehicleList.vue'),
        meta: { title: '车辆管理', perm: 'customer:read' }
      },
      {
        path: 'vehicles/:id',
        name: 'VehicleDetail',
        component: () => import('@/views/customer/VehicleDetail.vue'),
        meta: { title: '车辆详情', perm: 'customer:read' }
      },
      {
        path: 'appointments',
        name: 'Appointments',
        component: () => import('@/views/customer/AppointmentList.vue'),
        meta: { title: '预约管理', perm: 'customer:read' }
      },
      {
        path: 'appointments/:id',
        name: 'AppointmentDetail',
        component: () => import('@/views/customer/AppointmentDetail.vue'),
        meta: { title: '预约详情', perm: 'customer:read' }
      },
      {
        path: 'work-orders',
        name: 'WorkOrders',
        component: () => import('@/views/workorder/WorkOrderList.vue'),
        meta: { title: '工单管理', perm: 'work_order:read' }
      },
      {
        path: 'work-orders/parts-outbound',
        name: 'PartsOutboundStep',
        component: () => import('@/views/workorder/PartsOutboundStep.vue'),
        meta: { title: '配件出库', perm: 'work_order:read' }
      },
      {
        path: 'work-orders/:id',
        name: 'WorkOrderDetail',
        component: () => import('@/views/workorder/WorkOrderDetail.vue'),
        meta: { title: '工单详情', perm: 'work_order:read' }
      },
      {
        path: 'repair-items',
        name: 'RepairItems',
        component: () => import('@/views/workorder/RepairItemManage.vue'),
        meta: { title: '维修项目管理', perm: 'work_order:read' }
      },
      {
        path: 'parts',
        name: 'Parts',
        component: () => import('@/views/parts/PartsList.vue'),
        meta: { title: '配件管理', perm: 'parts:read' }
      },
      {
        path: 'parts/archive',
        name: 'PartArchive',
        component: () => import('@/views/parts/PartArchive.vue'),
        meta: { title: '配件档案', perm: 'parts:read' }
      },
      {
        path: 'parts/archive/:id',
        name: 'PartArchiveDetail',
        component: () => import('@/views/parts/PartArchiveDetail.vue'),
        meta: { title: '配件档案详情', perm: 'parts:read' }
      },
      {
        path: 'parts/inbound',
        name: 'PartsInbound',
        component: () => import('@/views/parts/InboundList.vue'),
        meta: { title: '入库管理', perm: 'parts:read' }
      },
      {
        path: 'parts/inbound/:id',
        name: 'InboundDetail',
        component: () => import('@/views/parts/InboundDetail.vue'),
        meta: { title: '入库单详情', perm: 'parts:read' }
      },
      {
        path: 'parts/suppliers',
        name: 'SupplierList',
        component: () => import('@/views/parts/SupplierList.vue'),
        meta: { title: '供应商管理', perm: 'parts:read' }
      },
      {
        path: 'parts/suppliers/:id',
        name: 'SupplierDetail',
        component: () => import('@/views/parts/SupplierDetail.vue'),
        meta: { title: '供应商详情', perm: 'parts:read' }
      },
      {
        path: 'finance/payments',
        name: 'Payments',
        component: () => import('@/views/finance/PaymentList.vue'),
        meta: { title: '收款管理', perm: 'finance:read' }
      },
      {
        path: 'finance/payments/:id',
        name: 'PaymentDetail',
        component: () => import('@/views/finance/PaymentDetail.vue'),
        meta: { title: '收款详情', perm: 'finance:read' }
      },
      {
        path: 'finance/invoices',
        name: 'Invoices',
        component: () => import('@/views/finance/InvoiceList.vue'),
        meta: { title: '发票管理', perm: 'finance:read' }
      },
      {
        path: 'finance/manufacturers',
        name: 'ClaimManufacturers',
        component: () => import('@/views/finance/ManufacturerList.vue'),
        meta: { title: '索赔厂家管理', perm: 'finance:read' }
      },
      {
        path: 'finance/manufacturers/:id',
        name: 'ManufacturerDetail',
        component: () => import('@/views/finance/ManufacturerDetail.vue'),
        meta: { title: '索赔厂家详情', perm: 'finance:read' }
      },
      {
        path: 'finance/insurances',
        name: 'InsuranceCompanies',
        component: () => import('@/views/finance/InsuranceList.vue'),
        meta: { title: '保险公司管理', perm: 'finance:read' }
      },
      {
        path: 'finance/insurances/:id',
        name: 'InsuranceDetail',
        component: () => import('@/views/finance/InsuranceDetail.vue'),
        meta: { title: '保险公司详情', perm: 'finance:read' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/report/ReportCenter.vue'),
        meta: { title: '报表中心', perm: 'report:read' }
      },
      {
        path: 'system/users',
        name: 'SystemUsers',
        component: () => import('@/views/system/UserManage.vue'),
        meta: { title: '用户管理', perm: 'system:user' }
      },
      {
        path: 'system/roles',
        name: 'SystemRoles',
        component: () => import('@/views/system/RoleManage.vue'),
        meta: { title: '角色管理', perm: 'system:role' }
      },
      {
        path: 'system/logs',
        name: 'SystemLogs',
        component: () => import('@/views/system/LogList.vue'),
        meta: { title: '操作日志', perm: 'system:log' }
      },
      {
        path: 'system/config',
        name: 'SystemConfig',
        component: () => import('@/views/system/SystemConfig.vue'),
        meta: { title: '系统配置', perm: 'system:config' }
      },
      {
        path: 'system/business',
        name: 'BusinessSettings',
        component: () => import('@/views/system/BusinessSettings.vue'),
        meta: { title: '业务设置', perm: 'system:config' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach(async (to, from, next) => {
  document.title = `${to.meta.title || ''} - 嘉之星企业管理系统`

  if (to.path === '/login') {
    next()
    return
  }

  const userStore = useUserStore()
  if (!userStore.isLoggedIn) {
    try {
      await userStore.fetchUserInfo()
    } catch {
      next('/login')
      return
    }
  }

  // 权限检查
  const requiredPerm = to.meta.perm
  if (requiredPerm && !userStore.hasPermission(requiredPerm)) {
    ElMessage.warning('您没有访问该页面的权限')
    next(false)
    return
  }

  next()
})

export default router
