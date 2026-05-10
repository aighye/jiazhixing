<template>
  <div>
    <div class="page-header">
      <h2>预约管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增预约
      </el-button>
    </div>

    <div class="search-bar">
      <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px" @change="loadData">
        <el-option label="待确认" :value="0" />
        <el-option label="已确认" :value="1" />
        <el-option label="已完成" :value="2" />
        <el-option label="已取消" :value="3" />
      </el-select>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="appointment_no" label="预约编号" width="180">
        <template #default="{ row }">
          <el-link type="primary" @click="$open(`/appointments/${row.id}?from=appointment-list`)">{{ row.appointment_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="plate_number" label="车牌号" width="120" />
      <el-table-column prop="phone" label="联系电话" width="130" />
      <el-table-column prop="appointment_date" label="预约日期" width="120" />
      <el-table-column prop="appointment_time" label="预约时间" width="100" />
      <el-table-column prop="service_type" label="服务类型" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType[row.status]" size="small">
            {{ ['待确认', '已确认', '已完成', '已取消'][row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="问题描述" show-overflow-tooltip />
      <el-table-column label="操作" fixed="right" width="280">
        <template #default="{ row }">
          <el-button v-if="row.status === 0" type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button v-if="row.status === 0" type="success" link size="small" @click="handleConfirm(row)">确认</el-button>
          <el-button v-if="row.status === 1" type="primary" link size="small" @click="handleToWorkOrder(row)">转工单</el-button>
          <el-button v-if="row.status === 0" type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          <el-button v-if="row.status === 0" type="warning" link size="small" @click="handleCancel(row)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" layout="total, sizes, prev, pager, next"
                   @size-change="loadData" @current-change="loadData" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑预约' : '新增预约'" width="550px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-form-item label="客户" required>
          <el-select v-model="form.customer_id" filterable style="width: 100%" @change="onCustomerChange">
            <el-option v-for="c in customerOptions" :key="c.id" :label="`${c.name} (${c.phone})`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="车辆" required>
          <el-select v-model="form.vehicle_id" style="width: 100%">
            <el-option v-for="v in vehicleOptions" :key="v.id" :label="v.plate_number" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="预约日期" required>
              <el-date-picker v-model="form.appointment_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预约时间" required>
              <el-time-picker v-model="form.appointment_time" format="HH:mm" value-format="HH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="服务类型">
          <el-input v-model="form.service_type" />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const statusFilter = ref(null)
const dialogVisible = ref(false)
const submitting = ref(false)
const editingId = ref(null)
const customerOptions = ref([])
const vehicleOptions = ref([])

const statusTagType = ['info', '', 'success', 'danger']

const form = reactive({
  customer_id: '', vehicle_id: '', phone: '', appointment_date: '', appointment_time: '', service_type: '', description: ''
})

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/customers/appointments/list', { params: { page: page.value, per_page: pageSize.value, status: statusFilter.value } })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadCustomers() {
  const res = await request.get('/customers/list', { params: { per_page: 1000 } })
  customerOptions.value = res.data.items
}

async function onCustomerChange(cid) {
  vehicleOptions.value = []
  if (!cid) return
  const res = await request.get('/customers/vehicles/list', { params: { customer_id: cid, per_page: 100 } })
  vehicleOptions.value = res.data.items
  const c = customerOptions.value.find(x => x.id === cid)
  if (c) form.phone = c.phone
}

function showDialog() {
  editingId.value = null
  Object.assign(form, { customer_id: '', vehicle_id: '', phone: '', appointment_date: '', appointment_time: '', service_type: '', description: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    customer_id: row.customer_id, vehicle_id: row.vehicle_id, phone: row.phone,
    appointment_date: row.appointment_date, appointment_time: row.appointment_time,
    service_type: row.service_type || '', description: row.description || ''
  })
  onCustomerChange(row.customer_id)
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.customer_id || !form.vehicle_id || !form.appointment_date) return ElMessage.warning('请填写必填项')
  submitting.value = true
  try {
    if (editingId.value) {
      await request.put(`/customers/appointments/${editingId.value}`, form)
      ElMessage.success('预约更新成功')
    } else {
      await request.post('/customers/appointments', form)
      ElMessage.success('预约创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

async function handleConfirm(row) {
  await request.put(`/customers/appointments/${row.id}/confirm`)
  ElMessage.success('已确认')
  loadData()
}

async function handleCancel(row) {
  const { value } = await ElMessageBox.prompt('请输入取消原因', '取消预约', {
    confirmButtonText: '确定取消',
    cancelButtonText: '返回',
    inputType: 'textarea',
    inputPlaceholder: '请输入取消预约说明',
    inputValidator: (v) => v && v.trim() ? true : '请填写取消原因'
  })
  await request.put(`/customers/appointments/${row.id}/cancel`, { remark: value })
  ElMessage.success('已取消')
  loadData()
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定删除此预约？', '提示', { type: 'warning' })
  await request.delete(`/customers/appointments/${row.id}`)
  ElMessage.success('已删除')
  loadData()
}

async function handleToWorkOrder(row) {
  await ElMessageBox.confirm('确定将此预约转为工单？', '转工单', { type: 'info' })
  const res = await request.post(`/customers/appointments/${row.id}/to-work-order`)
  ElMessage.success('已转为工单')
  loadData()
  router.push(`/work-orders/${res.data.id}`)
}

onMounted(() => { loadData(); loadCustomers() })
</script>

<style scoped>
/* Apple Design - Appointment List Page Styles */

/* Pagination spacing */
:deep(.el-pagination) {
  margin-top: var(--space-xl) !important;
  justify-content: flex-end;
}

/* Status filter width */
:deep(.search-bar .el-select) {
  width: 150px;
}
</style>
