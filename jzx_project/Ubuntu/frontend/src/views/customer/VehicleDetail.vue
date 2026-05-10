<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>车辆详情</h2>
      <div>
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="showEditDialog">编辑</el-button>
      </div>
    </div>

    <template v-if="vehicle">
      <!-- 基本信息 -->
      <el-card shadow="hover">
        <template #header>车辆基本信息</template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="车辆编号">{{ vehicle.vehicle_no }}</el-descriptions-item>
          <el-descriptions-item label="车牌号">
            <span class="plate-number-highlight">{{ vehicle.plate_number }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="车主">
            <el-link type="primary" @click="$open(`/customers/${vehicle.customer_id}?from=vehicle-detail`)">{{ vehicle.customer_name }}</el-link>
          </el-descriptions-item>
          <el-descriptions-item label="品牌">{{ vehicle.brand || '-' }}</el-descriptions-item>
          <el-descriptions-item label="车型">{{ vehicle.model || '-' }}</el-descriptions-item>
          <el-descriptions-item label="年款">{{ vehicle.year || '-' }}</el-descriptions-item>
          <el-descriptions-item label="颜色">{{ vehicle.color || '-' }}</el-descriptions-item>
          <el-descriptions-item label="当前里程">
            <span class="mileage-highlight">{{ vehicle.mileage?.toLocaleString() || 0 }} km</span>
          </el-descriptions-item>
          <el-descriptions-item label="发动机号">{{ vehicle.engine_no || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="VIN码" :span="2">{{ vehicle.vin || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="购车日期">{{ vehicle.purchase_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="保险到期">
            <el-tag :type="isExpiringSoon(vehicle.insurance_date) ? 'danger' : ''" size="small">
              {{ vehicle.insurance_date || '未填写' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="年检到期">
            <el-tag :type="isExpiringSoon(vehicle.inspection_date) ? 'danger' : ''" size="small">
              {{ vehicle.inspection_date || '未填写' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ vehicle.remark || '无' }}</el-descriptions-item>
          <el-descriptions-item label="录入时间">{{ formatTime(vehicle.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="操作人">{{ vehicle.creator_name || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 车主信息 -->
      <el-card shadow="hover" v-if="customer">
        <template #header>车主信息</template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="客户编号">{{ customer.customer_no }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ customer.name }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ customer.phone }}</el-descriptions-item>
          <el-descriptions-item label="客户类型">{{ customer.customer_type === 1 ? '个人' : '企业' }}</el-descriptions-item>
          <el-descriptions-item label="VIP等级">
            <el-tag v-if="customer.vip_level > 0" type="warning" size="small">VIP{{ customer.vip_level }}</el-tag>
            <span v-else>普通客户</span>
          </el-descriptions-item>
          <el-descriptions-item label="累计消费">¥{{ Number(customer.total_spending || 0).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="地址" :span="2">{{ customer.address || '未填写' }}</el-descriptions-item>
          <el-descriptions-item label="公司名称">{{ customer.company_name || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 维修记录 -->
      <el-card shadow="hover">
        <template #header>维修记录（{{ workOrders.length }} 条）</template>
        <el-table :data="workOrders" stripe>
          <el-table-column prop="order_no" label="工单号" width="200">
            <template #default="{ row }">
              <el-link type="primary" @click="$open(`/work-orders/${row.id}?from=vehicle-detail`)">{{ row.order_no }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="service_type" label="服务类型" width="100" />
          <el-table-column prop="status_name" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="mileage" label="进厂里程" width="110">
            <template #default="{ row }">{{ row.mileage?.toLocaleString() || '-' }} km</template>
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
    </template>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑车辆" width="650px">
      <el-form :model="editForm" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="车牌号"><el-input v-model="editForm.plate_number" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="品牌"><el-input v-model="editForm.brand" /></el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="年款"><el-input v-model="editForm.year" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="车型"><el-input v-model="editForm.model" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="颜色"><el-input v-model="editForm.color" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="里程"><el-input v-model="editForm.mileage" type="number" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="VIN"><el-input v-model="editForm.vin" /></el-form-item>
        <el-form-item label="发动机号"><el-input v-model="editForm.engine_no" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="保险到期">
              <el-date-picker v-model="editForm.insurance_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年检到期">
              <el-date-picker v-model="editForm.inspection_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="editForm.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
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
const vehicle = ref(null)
const customer = ref(null)
const workOrders = ref([])
const editDialogVisible = ref(false)
const saving = ref(false)

const editForm = reactive({
  plate_number: '', brand: '', model: '', year: '', color: '',
  mileage: 0, vin: '', engine_no: '',
  insurance_date: '', inspection_date: '', remark: ''
})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }
function getStatusType(s) { return ['info', '', 'success'][s] || '' }

function isExpiringSoon(dateStr) {
  if (!dateStr) return false
  const d = new Date(dateStr)
  const diff = (d - new Date()) / (1000 * 60 * 60 * 24)
  return diff >= 0 && diff <= 30
}

async function loadData() {
  loading.value = true
  try {
    const id = route.params.id
    // 获取车辆列表并找到对应车辆
    const vRes = await request.get('/customers/vehicles/list', { params: { per_page: 1000 } })
    vehicle.value = vRes.data.items.find(v => v.id === Number(id))

    if (vehicle.value) {
      // 获取车主信息
      const cRes = await request.get(`/customers/${vehicle.value.customer_id}`)
      customer.value = cRes.data

      // 获取该车辆关联的工单
      const woRes = await request.get('/work-orders/list', { params: { per_page: 100 } })
      workOrders.value = woRes.data.items.filter(wo => wo.vehicle_id === Number(id))
    }
  } finally {
    loading.value = false
  }
}

function showEditDialog() {
  if (!vehicle.value) return
  Object.assign(editForm, {
    plate_number: vehicle.value.plate_number,
    brand: vehicle.value.brand,
    model: vehicle.value.model,
    year: vehicle.value.year,
    color: vehicle.value.color,
    mileage: vehicle.value.mileage,
    vin: vehicle.value.vin,
    engine_no: vehicle.value.engine_no,
    insurance_date: vehicle.value.insurance_date,
    inspection_date: vehicle.value.inspection_date,
    remark: vehicle.value.remark
  })
  editDialogVisible.value = true
}

async function handleSave() {
  if (!/^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤川青藏琼宁][A-HJ-NP-Z][A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学警港澳]$/.test(editForm.plate_number)) return ElMessage.warning('请输入正确的车牌号')
  if (editForm.vin && !/^[A-HJ-NPR-Z0-9]{17}$/.test(editForm.vin)) return ElMessage.warning('VIN码应为17位字母数字（不含I、O、Q）')
  saving.value = true
  try {
    await request.put(`/customers/vehicles/${vehicle.value.id}`, editForm)
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
/* Apple Design - Vehicle Detail Page Styles */

/* Card spacing */
:deep(.el-card) {
  margin-bottom: var(--space-lg);
}

/* Plate number highlight */
.plate-number-highlight {
  font-size: 16px;
  font-weight: bold;
  color: var(--apple-text-primary);
}

/* Mileage highlight */
.mileage-highlight {
  font-weight: bold;
  color: var(--apple-text-primary);
}
</style>
