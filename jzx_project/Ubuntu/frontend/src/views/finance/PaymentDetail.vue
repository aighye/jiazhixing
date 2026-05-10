<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>收款详情 - {{ detail.payment_no }}</h2>
      <el-button @click="goBack">返回</el-button>
    </div>

    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>收款信息</span>
          <div>
            <el-button v-if="detail.status === 0" type="primary" size="small" @click="openEdit">编辑</el-button>
            <el-button v-if="detail.status === 0" type="success" size="small" @click="handleConfirm">确认收款</el-button>
            <el-button v-if="detail.status === 1 && detail.payment_type !== 'refund'" type="danger" size="small" @click="handleRefund">退款</el-button>
          </div>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="收款单号">{{ detail.payment_no }}</el-descriptions-item>
        <el-descriptions-item label="收款金额">
          <span :style="{ fontWeight: 'bold', color: Number(detail.amount) < 0 ? '#f56c6c' : '#67c23a', fontSize: '16px' }">
            ¥{{ Number(detail.amount).toFixed(2) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="收款状态">
          <el-tag :type="orderPaymentStatusType" size="small">{{ orderPaymentStatusText }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="收款方式">{{ paymentMethodMap[detail.payment_method] || detail.payment_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="收款类型">{{ paymentTypeMap[detail.payment_type] || detail.payment_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="交款人">{{ detail.payer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="收款时间">{{ formatTime(detail.received_at) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(detail.created_at) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ detail.received_by_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="3">{{ detail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card v-if="detail.order_id" shadow="hover">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>关联工单</span>
          <el-button type="primary" link @click="router.push(`/work-orders/${detail.order_id}?from=payment-detail`)">查看工单详情</el-button>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="工单号">
          <el-link type="primary" @click="router.push(`/work-orders/${detail.order_id}?from=payment-detail`)">{{ detail.order_no || '-' }}</el-link>
        </el-descriptions-item>
        <el-descriptions-item label="车牌号">{{ detail.plate_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ detail.customer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工单状态">
          <el-tag v-if="detail.order_status_name" :type="orderStatusType" size="small">{{ detail.order_status_name }}</el-tag>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="工单应收">
          <span v-if="detail.order_total !== undefined">¥{{ detail.order_total.toFixed(2) }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="工单已收">
          <span v-if="detail.order_received !== undefined" :style="{ color: orderReceivedColor }">¥{{ detail.order_received.toFixed(2) }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="未收金额">
          <span :style="{ fontWeight: 'bold', color: orderUnpaid > 0 ? '#f56c6c' : '#67c23a' }">¥{{ orderUnpaid.toFixed(2) }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 编辑收款弹窗 -->
    <el-dialog v-model="showEdit" title="编辑收款单" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="金额" required>
          <el-input v-model="editForm.amount" type="number" />
        </el-form-item>
        <el-form-item label="收款方式" required>
          <el-select v-model="editForm.payment_method" style="width: 100%">
            <el-option label="现金" value="cash" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="银行卡" value="bank" />
          </el-select>
        </el-form-item>
        <el-form-item label="交款人">
          <el-input v-model="editForm.payer_name" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" :loading="editSaving" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

function goBack() {
  router.back()
}

const loading = ref(false)
const detail = ref({})
const showEdit = ref(false)
const editSaving = ref(false)
const editForm = reactive({ amount: '', payment_method: 'cash', payer_name: '', remark: '' })

const paymentMethodMap = { cash: '现金', wechat: '微信', alipay: '支付宝', bank: '银行卡' }
const paymentTypeMap = { repair: '维修', deposit: '定金', refund: '退款', other: '其他' }
const statusNames = { 0: '待确认', 1: '已确认', 2: '已退款' }

const statusTagType = computed(() => ({ 0: 'warning', 1: 'success', 2: 'danger' }[detail.value.status] || 'info'))
const statusText = computed(() => statusNames[detail.value.status] || '未知')
const orderStatusType = computed(() => detail.value.order_status === 1 ? 'success' : 'primary')

// 动态计算工单付款相关字段
const orderTotal = computed(() => Number(detail.value.order_total || 0))
const orderReceived = computed(() => Number(detail.value.order_received || 0))
const orderUnpaid = computed(() => Math.max(0, orderTotal.value - orderReceived.value))
const orderReceivedColor = computed(() => {
  if (orderReceived.value > orderTotal.value) return '#e6a23c' // 超收-橙色
  if (orderReceived.value > 0) return '#67c23a' // 有收款-绿色
  return '#909399' // 未收款-灰色
})
const orderPaymentStatusText = computed(() => {
  const total = orderTotal.value
  const received = orderReceived.value
  if (total <= 0) return '无需收款'
  if (received <= 0) return '未收款'
  if (received > total) return '超收'
  if (received >= total) return '收清'
  return '部分收款'
})
const orderPaymentStatusType = computed(() => {
  const total = orderTotal.value
  const received = orderReceived.value
  if (total <= 0) return 'info'
  if (received <= 0) return 'danger'
  if (received > total) return 'warning'
  if (received >= total) return 'success'
  return ''
})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const res = await request.get(`/finance/payments/${route.params.id}`)
    detail.value = res.data
  } finally { loading.value = false }
}

function openEdit() {
  editForm.amount = detail.value.amount
  editForm.payment_method = detail.value.payment_method
  editForm.payer_name = detail.value.payer_name
  editForm.remark = detail.value.remark
  showEdit.value = true
}

async function handleEdit() {
  if (!editForm.amount) return ElMessage.warning('请填写金额')
  editSaving.value = true
  try {
    await request.put(`/finance/payments/${route.params.id}`, editForm)
    ElMessage.success('收款单更新成功')
    showEdit.value = false
    loadData()
  } finally { editSaving.value = false }
}

async function handleConfirm() {
  try {
    await ElMessageBox.confirm('确认该笔收款？确认后将更新工单收款信息。', '确认收款', { type: 'info' })
  } catch { return }
  try {
    await request.post(`/finance/payments/${route.params.id}/confirm`)
    ElMessage.success('收款确认成功')
    loadData()
  } catch (e) { /* 错误已在拦截器中处理 */ }
}

async function handleRefund() {
  try {
    await ElMessageBox.confirm('确认退款该笔收款？将生成一张负值退款收款单。', '退款确认', { type: 'warning' })
  } catch { return }
  try {
    const res = await request.post(`/finance/payments/${route.params.id}/refund`)
    ElMessage.success('退款成功，已生成退款收款单')
    // 跳转到新生成的退款收款单详情
    if (res.data?.id) {
      router.push(`/finance/payments/${res.data.id}`)
    } else {
      loadData()
    }
  } catch (e) { /* 错误已在拦截器中处理 */ }
}

onMounted(loadData)
</script>

<style scoped>
:deep(.el-card) { margin-bottom: var(--space-lg); }
</style>
