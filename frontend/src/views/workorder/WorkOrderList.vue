<template>
  <div>
    <div class="page-header">
      <h2>{{ pageTitle }}</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新建工单
      </el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索工单号/车牌号" clearable style="width: 220px" @clear="loadData" @keyup.enter="loadData" />
      <el-select v-if="!route.query.status" v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="onStatusFilterChange">
        <el-option v-for="(name, val) in statusNames" :key="val" :label="name" :value="Number(val)" />
      </el-select>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="loadData" />
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="order_no" label="工单号" width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="goToDetail(row)">{{ row.order_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="plate_number" label="车牌号" width="120" />
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="service_type" label="维修类别" width="100" />
      <el-table-column prop="status_name" label="工单状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_amount" label="总金额" width="100">
        <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="payment_status" label="收款状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="paymentStatusType(row.payment_status)" size="small">{{ row.payment_status || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="操作人" width="100" align="center">
        <template #default="{ row }">{{ row.creator_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" :page-sizes="[10, 20, 50]"
                   layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <!-- 新建工单对话框 -->
    <el-dialog v-model="dialogVisible" title="新建工单" width="600px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-form-item label="客户" required>
          <el-select v-model="form.customer_id" filterable style="width: 100%" @change="onCustomerChange">
            <el-option v-for="c in customerOptions" :key="c.id" :label="`${c.name} (${c.phone})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="车辆" required>
          <el-select v-model="form.vehicle_id" style="width: 100%">
            <el-option v-for="v in vehicleOptions" :key="v.id" :label="`${v.plate_number} (${v.brand} ${v.model})`" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="进厂里程">
          <el-input v-model="form.mileage" type="number" />
        </el-form-item>
        <el-form-item label="维修类别">
          <el-select v-model="form.service_type" style="width: 100%">
            <el-option v-for="rc in repairCategoryList" :key="rc.id" :label="rc.name" :value="rc.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="维修项目或故障描述">
          <el-input v-model="form.fault_description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="预估费用">
          <el-input v-model="form.estimated_cost" type="number" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const statusNames = { 0: '在修', 1: '结算' }

function paymentStatusType(status) {
  const map = { '无需收款': 'info', '未收款': 'danger', '部分收款': '', '收清': 'success', '超收': 'warning' }
  return map[status] || 'info'
}

function goToDetail(row) {
  const path = `/work-orders/${row.id}`
  const query = {}
  if (statusFilter.value === 0) query.from = 'repair'
  else if (statusFilter.value === 1) query.from = 'settlement'
  router.push({ path, query })
}

const list = ref([])
const loading = ref(false)
const keyword = ref('')
const statusFilter = ref(null)
const dateRange = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const submitting = ref(false)
const customerOptions = ref([])
const vehicleOptions = ref([])
const repairCategoryList = ref([])

const form = reactive({
  customer_id: '', vehicle_id: '', mileage: '', service_type: '保养', fault_description: '', estimated_cost: ''
})

// 动态页面标题
const pageTitle = computed(() => {
  if (statusFilter.value !== null && statusFilter.value !== '' && statusNames[statusFilter.value]) {
    return `工单管理 - ${statusNames[statusFilter.value]}`
  }
  return '工单管理'
})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }
function getStatusType(s) {
  return s === 1 ? 'success' : 'primary'
}

// 状态筛选下拉变更时，同步更新 URL query
function onStatusFilterChange() {
  page.value = 1
  if (statusFilter.value !== null && statusFilter.value !== '') {
    router.replace({ query: { status: statusFilter.value } })
  } else {
    router.replace({ query: {} })
  }
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize.value, keyword: keyword.value }
    if (statusFilter.value !== null && statusFilter.value !== '') params.status = statusFilter.value
    if (dateRange.value) { params.start_date = dateRange.value[0]; params.end_date = dateRange.value[1] }
    const res = await request.get('/work-orders/list', { params })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadCustomers() {
  const res = await request.get('/customers/list', { params: { per_page: 1000 } })
  customerOptions.value = res.data.items
}

async function loadRepairCategories() {
  try {
    const res = await request.get('/system/dict-items', { params: { type: 'repair_category' } })
    repairCategoryList.value = (res.data || []).filter(i => i.status === 1)
  } catch (e) { console.error('加载维修类别失败', e) }
}

async function onCustomerChange(cid) {
  vehicleOptions.value = []
  if (!cid) return
  const res = await request.get('/customers/vehicles/list', { params: { customer_id: cid, per_page: 100 } })
  vehicleOptions.value = res.data.items
}

function showDialog() {
  Object.assign(form, { customer_id: '', vehicle_id: '', mileage: '', service_type: '保养', fault_description: '', estimated_cost: '' })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.customer_id || !form.vehicle_id) return ElMessage.warning('请填写必填项')
  submitting.value = true
  try {
    await request.post('/work-orders', form)
    ElMessage.success('工单创建成功')
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

async function handleStatus(row, newStatus) {
  await request.put(`/work-orders/${row.id}/status`, { status: newStatus })
  ElMessage.success('状态更新成功')
  loadData()
}

async function handleParallelConfirm(row, step) {
  const label = step === 'repair_confirmed' ? '维修完成' : '配件出库完成'
  await request.put(`/work-orders/${row.id}/status`, { status: 1, remark: step })
  ElMessage.success(`${label}确认成功，两个步骤均完成后将自动进入完工`)
  loadData()
}

// 监听路由 query 变化（从侧边栏菜单点击时触发）
watch(() => route.query.status, (newStatus) => {
  if (newStatus !== undefined && newStatus !== null) {
    statusFilter.value = Number(newStatus)
  } else {
    statusFilter.value = null
  }
  page.value = 1
  loadData()
})

onMounted(() => {
  // 初始化时从路由 query 读取 status
  if (route.query.status !== undefined) {
    statusFilter.value = Number(route.query.status)
  }
  loadData()
  loadCustomers()
  loadRepairCategories()
})
</script>
