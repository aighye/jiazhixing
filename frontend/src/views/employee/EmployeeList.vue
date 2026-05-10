<template>
  <div>
    <div class="page-header">
      <h2>员工管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增员工
      </el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索姓名/工号/手机" clearable style="width: 250px" @clear="loadData" @keyup.enter="loadData" />
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="employee_no" label="工号" width="160" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="gender" label="性别" width="70">
        <template #default="{ row }">{{ ['', '男', '女'][row.gender] || '未知' }}</template>
      </el-table-column>
      <el-table-column prop="department" label="部门" width="100" />
      <el-table-column prop="position" label="职位" width="100" />
      <el-table-column prop="employee_type" label="类型" width="100">
        <template #default="{ row }">{{ { technician: '技师', service: '服务顾问', manager: '管理' }[row.employee_type] || row.employee_type }}</template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="base_salary" label="基本工资" width="100">
        <template #default="{ row }">¥{{ Number(row.base_salary).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '在职' : '离职' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="140">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="showDialog(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" :page-sizes="[10, 20, 50]"
                   layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑员工' : '新增员工'" width="600px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名" required>
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender" style="width: 100%">
                <el-option label="未知" :value="0" />
                <el-option label="男" :value="1" />
                <el-option label="女" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号">
              <el-input v-model="form.id_card" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="部门">
              <el-input v-model="form.department" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位">
              <el-input v-model="form.position" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="员工类型">
              <el-select v-model="form.employee_type" style="width: 100%">
                <el-option label="技师" value="technician" />
                <el-option label="服务顾问" value="service" />
                <el-option label="管理" value="manager" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="级别">
              <el-input v-model="form.level" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="基本工资">
              <el-input v-model="form.base_salary" type="number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工时单价">
              <el-input v-model="form.hourly_rate" type="number" />
            </el-form-item>
          </el-col>
        </el-row>
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

const form = reactive({
  name: '', gender: 0, phone: '', id_card: '', department: '', position: '',
  employee_type: '', level: '', base_salary: 0, hourly_rate: 0
})

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/employees/list', { params: { page: page.value, per_page: pageSize.value, keyword: keyword.value } })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

function showDialog(row) {
  editingId.value = row ? row.id : null
  Object.assign(form, { name: '', gender: 0, phone: '', id_card: '', department: '', position: '', employee_type: '', level: '', base_salary: 0, hourly_rate: 0 })
  if (row) Object.assign(form, row)
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.name) return ElMessage.warning('请填写姓名')
  submitting.value = true
  try {
    if (editingId.value) {
      await request.put(`/employees/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/employees', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

onMounted(loadData)
</script>

<style scoped>
/* Apple Design - Employee List Page Styles */

/* Pagination spacing */
:deep(.el-pagination) {
  margin-top: var(--space-xl) !important;
  justify-content: flex-end;
}

/* Search bar input width */
:deep(.search-bar .el-input) {
  width: 250px;
}
</style>
