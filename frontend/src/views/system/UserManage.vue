<template>
  <div>
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增用户
      </el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="real_name" label="姓名" width="100" />
      <el-table-column prop="department" label="部门" width="100" />
      <el-table-column prop="title" label="职称" width="100" />
      <el-table-column prop="level" label="等级" width="80" />
      <el-table-column prop="base_salary" label="基本工资" width="100" align="right">
        <template #default="{ row }">¥{{ Number(row.base_salary || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="employee_type" label="员工类型" width="100">
        <template #default="{ row }">{{ employeeTypeMap[row.employee_type] || row.employee_type || '-' }}</template>
      </el-table-column>
      <el-table-column prop="role" label="角色" width="120" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_login" label="最后登录" width="160">
        <template #default="{ row }">{{ formatTime(row.last_login) }}</template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="180">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="showDialog(row)">编辑</el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">禁用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用户' : '新增用户'" width="650px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="用户名" required>
              <el-input v-model="form.username" :disabled="!!editingId" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码" :required="!editingId">
              <el-input v-model="form.password" type="password" show-password :placeholder="editingId ? '留空不修改' : '请输入密码'" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名" required>
              <el-input v-model="form.real_name" />
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
              <el-select v-model="form.employee_type" style="width: 100%" clearable placeholder="选择类型">
                <el-option label="技师" value="technician" />
                <el-option label="服务顾问" value="service" />
                <el-option label="管理" value="manager" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="级别">
              <el-input v-model="form.level" placeholder="如：高级/中级/初级" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称">
              <el-input v-model="form.title" placeholder="如：高级工程师" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="角色" required>
              <el-select v-model="form.role_id" style="width: 100%">
                <el-option v-for="r in roleOptions" :key="r.id" :label="r.name" :value="r.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号">
              <el-input v-model="form.employee_no" placeholder="员工工号" />
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
import { ElMessage, ElMessageBox } from 'element-plus'

const employeeTypeMap = { technician: '技师', service: '服务顾问', manager: '管理' }

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const roleOptions = ref([])

const form = reactive({
  username: '', password: '', real_name: '', phone: '', role_id: '',
  gender: 0, id_card: '', department: '', position: '',
  employee_type: '', level: '', title: '', employee_no: ''
})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/system/users', { params: { page: page.value, per_page: pageSize.value } })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadRoles() {
  const res = await request.get('/system/roles')
  roleOptions.value = res.data
}

function showDialog(row) {
  editingId.value = row ? row.id : null
  Object.assign(form, {
    username: '', password: '', real_name: '', phone: '', role_id: '',
    gender: 0, id_card: '', department: '', position: '',
    employee_type: '', level: '', title: '', employee_no: ''
  })
  if (row) Object.assign(form, row)
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.username || !form.real_name || !form.role_id) return ElMessage.warning('请填写必填项')
  submitting.value = true
  try {
    if (editingId.value) {
      await request.put(`/system/users/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/system/users', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定禁用该用户？', '提示', { type: 'warning' })
  await request.delete(`/system/users/${row.id}`)
  ElMessage.success('已禁用')
  loadData()
}

onMounted(() => { loadData(); loadRoles() })
</script>

<style scoped>
/* Apple Design - User Management Page Styles */

/* Pagination spacing */
:deep(.el-pagination) {
  margin-top: var(--space-xl) !important;
  justify-content: flex-end;
}
</style>
