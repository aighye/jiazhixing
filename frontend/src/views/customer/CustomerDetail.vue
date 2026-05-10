<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>客户详情</h2>
      <div>
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="showEditDialog">编辑</el-button>
      </div>
    </div>

    <template v-if="customer">
      <!-- 基本信息 -->
      <el-card shadow="hover">
        <template #header>基本信息</template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="客户编号">{{ customer.customer_no }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ customer.name }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ customer.phone }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ ['', '男', '女'][customer.gender] || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="客户类型">{{ customer.customer_type === 1 ? '个人' : '企业' }}</el-descriptions-item>
          <el-descriptions-item label="VIP等级">
            <el-tag v-if="customer.vip_level > 0" type="warning" size="small">VIP{{ customer.vip_level }}</el-tag>
            <span v-else>普通客户</span>
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ customer.email || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ customer.id_card || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="公司名称">{{ customer.company_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="地址" :span="2">{{ customer.address || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ customer.remark || '无' }}</el-descriptions-item>
          <el-descriptions-item label="累计消费">
            <span class="spending-amount">¥{{ Number(customer.total_spending || 0).toFixed(2) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="积分">{{ customer.points || 0 }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ formatTime(customer.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="操作人">{{ customer.creator_name || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 车辆信息 -->
      <el-card shadow="hover">
        <template #header>
          <div class="card-header-flex">
            <span>名下车辆（{{ vehicles.length }} 辆）</span>
            <el-button type="primary" size="small" @click="showAddVehicle = true">添加车辆</el-button>
          </div>
        </template>
        <el-table :data="vehicles" stripe>
          <el-table-column prop="vehicle_no" label="车辆编号" width="150" />
          <el-table-column prop="plate_number" label="车牌号" width="120" />
          <el-table-column prop="brand" label="品牌" width="80" />
          <el-table-column prop="model" label="车型" width="100" />
          <el-table-column prop="year" label="年款" width="70" />
          <el-table-column prop="color" label="颜色" width="70" />
          <el-table-column prop="mileage" label="里程(km)" width="100">
            <template #default="{ row }">{{ row.mileage?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="vin" label="VIN码" width="200" show-overflow-tooltip />
          <el-table-column prop="insurance_date" label="保险到期" width="110">
            <template #default="{ row }">{{ row.insurance_date || '-' }}</template>
          </el-table-column>
          <el-table-column prop="inspection_date" label="年检到期" width="110">
            <template #default="{ row }">{{ row.inspection_date || '-' }}</template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 维修记录 -->
      <el-card shadow="hover">
        <template #header>维修记录</template>
        <el-table :data="workOrders" stripe>
          <el-table-column prop="order_no" label="工单号" width="200">
            <template #default="{ row }">
              <el-link type="primary" @click="$open(`/work-orders/${row.id}?from=customer-detail`)">{{ row.order_no }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="plate_number" label="车牌号" width="120" />
          <el-table-column prop="service_type" label="服务类型" width="100" />
          <el-table-column prop="status_name" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="金额" width="110">
            <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="is_paid" label="付款" width="70">
            <template #default="{ row }">
              <el-tag :type="row.is_paid ? 'success' : 'danger'" size="small">{{ row.is_paid ? '已付' : '未付' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="fault_description" label="故障描述" show-overflow-tooltip />
          <el-table-column prop="creator_name" label="操作人" width="100" align="center">
            <template #default="{ row }">{{ row.creator_name || '-' }}</template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 预约记录 -->
      <el-card shadow="hover" v-if="appointments.length > 0">
        <template #header>预约记录</template>
        <el-table :data="appointments" stripe>
          <el-table-column prop="appointment_no" label="预约编号" width="180" />
          <el-table-column prop="plate_number" label="车牌号" width="120" />
          <el-table-column prop="appointment_date" label="预约日期" width="120" />
          <el-table-column prop="appointment_time" label="预约时间" width="100" />
          <el-table-column prop="service_type" label="服务类型" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="['info', '', 'success', 'danger'][row.status]" size="small">
                {{ ['待确认', '已确认', '已完成', '已取消'][row.status] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="问题描述" show-overflow-tooltip />
        </el-table>
      </el-card>
    </template>

    <!-- 编辑客户对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑客户" width="600px">
      <el-form :model="editForm" label-width="80px" class="dialog-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名"><el-input v-model="editForm.name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号"><el-input v-model="editForm.phone" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="editForm.gender" style="width:100%">
                <el-option label="未知" :value="0" />
                <el-option label="男" :value="1" />
                <el-option label="女" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户类型">
              <el-select v-model="editForm.customer_type" style="width:100%">
                <el-option label="个人" :value="1" />
                <el-option label="企业" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱"><el-input v-model="editForm.email" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="editForm.address" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="editForm.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加车辆对话框 -->
    <el-dialog v-model="showAddVehicle" title="添加车辆" width="650px">
      <el-form :model="vehicleForm" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="车牌号" required><el-input v-model="vehicleForm.plate_number" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="品牌"><el-input v-model="vehicleForm.brand" /></el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="年款"><el-input v-model="vehicleForm.year" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="车型"><el-input v-model="vehicleForm.model" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="颜色"><el-input v-model="vehicleForm.color" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="里程"><el-input v-model="vehicleForm.mileage" type="number" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="VIN"><el-input v-model="vehicleForm.vin" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="vehicleForm.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddVehicle = false">取消</el-button>
        <el-button type="primary" :loading="addingVehicle" @click="handleAddVehicle">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

function goBack() {
  router.back()
}
const loading = ref(false)
const customer = ref(null)
const vehicles = ref([])
const workOrders = ref([])
const appointments = ref([])
const editDialogVisible = ref(false)
const saving = ref(false)
const showAddVehicle = ref(false)
const addingVehicle = ref(false)

const editForm = reactive({ name: '', phone: '', email: '', gender: 0, customer_type: 1, address: '', remark: '' })
const vehicleForm = reactive({ plate_number: '', brand: '', model: '', year: '', color: '', mileage: 0, vin: '', remark: '' })

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }
function getStatusType(s) { return ['info', '', 'success'][s] || '' }

async function loadData() {
  loading.value = true
  try {
    const id = route.params.id
    const custRes = await request.get(`/customers/${id}`)
    customer.value = custRes.data
    vehicles.value = custRes.data.vehicles || []

    // 独立加载工单和预约，避免一个失败导致整个页面崩溃
    try {
      const woRes = await request.get('/work-orders/list', { params: { per_page: 100, keyword: '' } })
      workOrders.value = woRes.data.items.filter(wo => wo.customer_id === Number(id))
    } catch (e) {
      console.warn('加载工单列表失败:', e)
      workOrders.value = []
    }

    try {
      const aptRes = await request.get('/customers/appointments/list', { params: { per_page: 100 } })
      appointments.value = aptRes.data.items.filter(a => a.customer_id === Number(id))
    } catch (e) {
      console.warn('加载预约列表失败:', e)
      appointments.value = []
    }
  } catch (e) {
    ElMessage.error('加载客户信息失败')
  } finally {
    loading.value = false
  }
}

function showEditDialog() {
  if (!customer.value) return
  Object.assign(editForm, {
    name: customer.value.name,
    phone: customer.value.phone,
    email: customer.value.email,
    gender: customer.value.gender,
    customer_type: customer.value.customer_type,
    address: customer.value.address,
    remark: customer.value.remark
  })
  editDialogVisible.value = true
}

async function handleSave() {
  if (!/^1[3-9]\d{9}$/.test(editForm.phone)) return ElMessage.warning('请输入正确的手机号')
  saving.value = true
  try {
    await request.put(`/customers/${customer.value.id}`, editForm)
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}

async function handleAddVehicle() {
  if (!vehicleForm.plate_number) return ElMessage.warning('请填写车牌号')
  if (!/^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤川青藏琼宁][A-HJ-NP-Z][A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学警港澳]$/.test(vehicleForm.plate_number)) return ElMessage.warning('请输入正确的车牌号')
  if (vehicleForm.vin && !/^[A-HJ-NPR-Z0-9]{17}$/.test(vehicleForm.vin)) return ElMessage.warning('VIN码应为17位字母数字（不含I、O、Q）')
  addingVehicle.value = true
  try {
    await request.post('/customers/vehicles', { ...vehicleForm, customer_id: customer.value.id })
    ElMessage.success('车辆添加成功')
    showAddVehicle.value = false
    Object.assign(vehicleForm, { plate_number: '', brand: '', model: '', year: '', color: '', mileage: 0, vin: '', remark: '' })
    loadData()
  } finally {
    addingVehicle.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
/* Apple Design - Customer Detail Page Styles */

/* Card spacing */
:deep(.el-card) {
  margin-bottom: var(--space-lg);
}

:deep(.el-card + .el-card) {
  margin-top: var(--space-lg);
}

/* Spending amount highlight */
.spending-amount {
  font-size: 16px;
  font-weight: bold;
  color: var(--apple-blue);
}

/* Card header flex layout */
.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
