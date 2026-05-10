<template>
  <div>
    <div class="page-header">
      <h2>收款管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增收款
      </el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索工单号/客户" clearable style="width: 200px" @clear="loadData" @keyup.enter="loadData" />
      <el-select v-model="statusFilter" placeholder="工单状态" clearable style="width: 130px" @change="loadData">
        <el-option label="在修" :value="0" />
        <el-option label="结算" :value="1" />
      </el-select>
      <el-select v-model="payStatusFilter" placeholder="收款状态" clearable style="width: 130px" @change="loadData">
        <el-option label="无需收款" value="无需收款" />
        <el-option label="未收款" value="未收款" />
        <el-option label="部分收款" value="部分收款" />
        <el-option label="收清" value="收清" />
        <el-option label="超收" value="超收" />
      </el-select>
      <el-select v-model="methodFilter" placeholder="支付方式" clearable style="width: 130px" @change="loadData">
        <el-option label="现金" value="cash" />
        <el-option label="微信" value="wechat" />
        <el-option label="支付宝" value="alipay" />
        <el-option label="银行卡" value="bank" />
      </el-select>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="loadData" />
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading" show-summary :summary-method="getSummary">
      <el-table-column prop="payment_no" label="收款单号" width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="router.push(`/finance/payments/${row.id}?from=payment-list`)">{{ row.payment_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="order_no" label="工单号" width="180">
        <template #default="{ row }">
          <el-link v-if="row.order_no" type="primary" @click="router.push(`/work-orders/${row.order_id}?from=payment-list`)">{{ row.order_no }}</el-link>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="plate_number" label="车牌号" width="110" />
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="order_status_name" label="工单状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.order_status_name" :type="orderStatusTagType(row.order_status)" size="small">{{ row.order_status_name }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="金额" width="120" align="right">
        <template #default="{ row }">
          <span :style="{ fontWeight: 'bold', color: Number(row.amount) < 0 ? '#f56c6c' : '#67c23a' }">¥{{ Number(row.amount).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="payment_method" label="支付方式" width="100">
        <template #default="{ row }">{{ paymentMethodMap[row.payment_method] || row.payment_method || '-' }}</template>
      </el-table-column>
      <el-table-column prop="payer_name" label="交款人" width="100" />
      <el-table-column prop="payment_status" label="工单收款状态" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="paymentStatusType(row.payment_status)" size="small">{{ row.payment_status || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="收款单状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="{ 0: 'warning', 1: 'success', 2: 'danger' }[row.status] || 'info'" size="small">{{ { 0: '待确认', 1: '已确认', 2: '已退款' }[row.status] || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <el-dialog v-model="dialogVisible" title="新增收款" width="550px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-form-item label="选择工单" required>
          <el-select v-model="form.order_id" filterable placeholder="请选择工单" style="width: 100%" @change="onOrderChange">
            <el-option v-for="o in orderOptions" :key="o.id" :label="`${o.order_no} - ${o.customer_name} (${o.plate_number || '-'}) ¥${Number(o.total_amount).toFixed(2)}`" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户">
          <el-input :model-value="selectedOrder?.customer_name || ''" disabled />
        </el-form-item>
        <el-form-item label="应收金额">
          <el-input :model-value="selectedOrder ? `¥${Number(selectedOrder.total_amount).toFixed(2)}` : ''" disabled />
        </el-form-item>
        <el-form-item label="已收金额">
          <el-input :model-value="selectedOrder ? `¥${Number(selectedOrder.actual_received || 0).toFixed(2)}` : ''" disabled />
        </el-form-item>
        <el-form-item label="未收金额">
          <el-input :model-value="selectedOrder ? `¥${unpaidAmount.toFixed(2)}` : ''" disabled />
        </el-form-item>
        <el-form-item label="收款金额" required>
          <el-input v-model="form.amount" type="number" :placeholder="unpaidAmount > 0 ? `默认: ${unpaidAmount}` : ''" />
        </el-form-item>
        <el-form-item label="支付方式" required>
          <el-select v-model="form.payment_method" style="width: 100%">
            <el-option label="现金" value="cash" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="银行卡" value="bank" />
          </el-select>
        </el-form-item>
        <el-form-item label="交款人">
          <el-input v-model="form.payer_name" :placeholder="selectedOrder?.customer_name || ''" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">创建收款单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const router = useRouter()

const list = ref([])
const loading = ref(false)
const keyword = ref('')
const dateRange = ref(null)
const methodFilter = ref(null)
const statusFilter = ref(null)
const payStatusFilter = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const submitting = ref(false)
const orderOptions = ref([])
const selectedOrder = ref(null)
const unpaidAmount = computed(() => {
  if (!selectedOrder.value) return 0
  return Math.max(0, Number(selectedOrder.value.total_amount || 0) - Number(selectedOrder.value.actual_received || 0))
})

const form = reactive({ order_id: '', customer_id: '', amount: '', payment_method: 'cash', payer_name: '', remark: '' })

const paymentMethodMap = { cash: '现金', wechat: '微信', alipay: '支付宝', bank: '银行卡' }

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

function getSummary({ columns }) {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (col.property === 'amount') {
      const total = list.value.reduce((s, r) => s + Number(r.amount || 0), 0)
      sums[idx] = `¥${total.toFixed(2)}`
    } else {
      sums[idx] = ''
    }
  })
  return sums
}

function paymentStatusType(status) {
  const map = { '无需收款': 'info', '未收款': 'danger', '部分收款': '', '收清': 'success', '超收': 'warning' }
  return map[status] || 'info'
}

function orderStatusTagType(status) {
  return status === 1 ? 'success' : 'primary'
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value !== null && statusFilter.value !== '') params.order_status = statusFilter.value
    if (payStatusFilter.value) params.payment_status = payStatusFilter.value
    if (methodFilter.value) params.payment_method = methodFilter.value
    if (dateRange.value) { params.start_date = dateRange.value[0]; params.end_date = dateRange.value[1] }
    const res = await request.get('/finance/payments', { params })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadOrders() {
  const res = await request.get('/work-orders/list', { params: { per_page: 1000 } })
  orderOptions.value = res.data.items
}

function onOrderChange(orderId) {
  selectedOrder.value = orderOptions.value.find(o => o.id === orderId) || null
  if (selectedOrder.value) {
    form.customer_id = selectedOrder.value.customer_id
    form.payer_name = selectedOrder.value.customer_name || ''
    form.amount = unpaidAmount.value > 0 ? unpaidAmount.value : ''
  }
}

function showDialog() {
  Object.assign(form, { order_id: '', customer_id: '', amount: '', payment_method: 'cash', payer_name: '', remark: '' })
  selectedOrder.value = null
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.order_id || !form.amount) return ElMessage.warning('请选择工单并填写金额')
  submitting.value = true
  try {
    await request.post('/finance/payments', form)
    ElMessage.success('收款单创建成功')
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

onMounted(() => { loadData(); loadOrders() })
</script>

<style scoped>
/* Apple Design - Payment List Page Styles */

/* Pagination spacing */
:deep(.el-pagination) {
  margin-top: var(--space-xl) !important;
  justify-content: flex-end;
}

/* Search bar input width */
:deep(.search-bar .el-input),
:deep(.search-bar .el-select) {
  width: 180px;
}

/* Amount display */
.amount-success {
  font-weight: bold;
  color: #34c759;
}
</style>
