<template>
  <div>
    <div class="page-header">
      <h2>车辆管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增车辆
      </el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索车牌号/VIN/品牌" clearable style="width: 250px" @clear="loadData" @keyup.enter="loadData" />
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="vehicle_no" label="车辆编号" width="180">
        <template #default="{ row }">
          <el-link type="primary" @click="$open(`/vehicles/${row.id}?from=vehicle-list`)">{{ row.vehicle_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="plate_number" label="车牌号" width="120" />
      <el-table-column prop="customer_name" label="车主" width="100" />
      <el-table-column prop="brand" label="品牌" width="80" />
      <el-table-column prop="model" label="车型" width="100" />
      <el-table-column prop="year" label="年款" width="70" />
      <el-table-column prop="color" label="颜色" width="70" />
      <el-table-column prop="mileage" label="里程(km)" width="100" />
      <el-table-column prop="creator_name" label="操作人" width="100" align="center">
        <template #default="{ row }">{{ row.creator_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="140" align="center">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="showDialog(row)" style="min-width: 60px;">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" :page-sizes="[10, 20, 50]"
                   layout="total, sizes, prev, pager, next"
                   @size-change="loadData" @current-change="loadData" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑车辆' : '新增车辆'" width="650px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="车牌号" required>
              <el-input v-model="form.plate_number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车主" required>
              <el-select v-model="form.customer_id" filterable style="width: 100%">
                <el-option v-for="c in customerOptions" :key="c.id" :label="`${c.name} (${c.phone})`" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="品牌">
              <el-input v-model="form.brand" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="车型">
              <el-input v-model="form.model" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="年款">
              <el-input v-model="form.year" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="颜色">
              <el-input v-model="form.color" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="里程">
              <el-input v-model="form.mileage" type="number" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="VIN">
              <el-input v-model="form.vin" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
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
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const customerOptions = ref([])

const form = reactive({
  customer_id: '', plate_number: '', brand: '', model: '', year: '', color: '',
  mileage: 0, vin: '', remark: ''
})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/customers/vehicles/list', { params: { page: page.value, per_page: pageSize.value, keyword: keyword.value } })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadCustomers() {
  const res = await request.get('/customers/list', { params: { per_page: 1000 } })
  customerOptions.value = res.data.items
}

function showDialog(row) {
  editingId.value = row ? row.id : null
  Object.assign(form, { customer_id: '', plate_number: '', brand: '', model: '', year: '', color: '', mileage: 0, vin: '', remark: '' })
  if (row) Object.assign(form, row)
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.plate_number || !form.customer_id) return ElMessage.warning('请填写必填项')
  if (!/^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤川青藏琼宁][A-HJ-NP-Z][A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学警港澳]$/.test(form.plate_number)) return ElMessage.warning('请输入正确的车牌号')
  if (form.vin && !/^[A-HJ-NPR-Z0-9]{17}$/.test(form.vin)) return ElMessage.warning('VIN码应为17位字母数字（不含I、O、Q）')
  submitting.value = true
  try {
    if (editingId.value) {
      await request.put(`/customers/vehicles/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/customers/vehicles', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

onMounted(() => { loadData(); loadCustomers() })
</script>

<style scoped>
/* Apple Design - Vehicle List Page Styles */

/* Pagination spacing */
:deep(.el-pagination) {
  margin-top: var(--space-xl) !important;
  justify-content: flex-end;
}

/* Search input width */
:deep(.search-bar .el-input) {
  width: 250px;
}
</style>
