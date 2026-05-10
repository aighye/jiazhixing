<template>
  <div>
    <div class="page-header">
      <h2>供应商管理</h2>
      <el-button type="primary" @click="openAdd">
        <el-icon><Plus /></el-icon> 新增供应商
      </el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索名称/编码/联系人/电话" clearable style="width: 280px" @clear="loadData" @keyup.enter="loadData" />
      <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px" @change="loadData">
        <el-option label="启用" :value="1" />
        <el-option label="停用" :value="0" />
      </el-select>
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading" style="width: 100%">
      <el-table-column prop="code" label="供应商编码" width="130">
        <template #default="{ row }">
          <el-link type="primary" @click="$router.push(`/parts/suppliers/${row.id}`)">{{ row.code || '-' }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="供应商名称" min-width="160" />
      <el-table-column prop="contact_person" label="联系人" width="100" />
      <el-table-column prop="phone" label="联系电话" width="130" />
      <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
      <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
      <el-table-column label="信用等级" width="90" align="center">
        <template #default="{ row }">
          <el-rate v-model="row.credit_level" disabled :max="5" style="height: 20px;" />
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
          <el-popconfirm title="确定删除此供应商？" @confirm="handleDelete(row)">
            <template #reference>
              <el-button type="danger" link size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="perPage"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑供应商' : '新增供应商'" width="600px" @close="resetForm">
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="供应商名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入供应商名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商编码" prop="code">
              <el-input v-model="form.code" placeholder="请输入编码（唯一）" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-input v-model="form.contact_person" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="form.phone" placeholder="请输入电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="信用等级">
              <el-rate v-model="form.credit_level" :max="5" show-text :texts="['很差','差','一般','好','很好']" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开户银行">
              <el-input v-model="form.bank_name" placeholder="请输入开户银行" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账号">
              <el-input v-model="form.bank_account" placeholder="请输入银行账号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="form.status">
                <el-radio :value="1">启用</el-radio>
                <el-radio :value="0">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const list = ref([])
const keyword = ref('')
const statusFilter = ref(null)
const page = ref(1)
const perPage = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const editId = ref(null)

const form = reactive({
  name: '',
  code: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  bank_name: '',
  bank_account: '',
  credit_level: 3,
  status: 1,
  remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }]
}

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/suppliers/list', {
      params: { page: page.value, per_page: perPage.value, keyword: keyword.value, status: statusFilter.value }
    })
    list.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, { name: '', code: '', contact_person: '', phone: '', email: '', address: '', bank_name: '', bank_account: '', credit_level: 3, status: 1, remark: '' })
  editId.value = null
  isEdit.value = false
}

function openAdd() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, {
    name: row.name,
    code: row.code || '',
    contact_person: row.contact_person || '',
    phone: row.phone || '',
    email: row.email || '',
    address: row.address || '',
    bank_name: row.bank_name || '',
    bank_account: row.bank_account || '',
    credit_level: row.credit_level || 3,
    status: row.status,
    remark: row.remark || ''
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (formRef.value) await formRef.value.validate().catch(() => false)
  if (!form.name.trim()) return ElMessage.warning('请输入供应商名称')

  submitting.value = true
  try {
    if (isEdit.value) {
      await request.put(`/suppliers/${editId.value}`, form)
      ElMessage.success('供应商更新成功')
    } else {
      await request.post('/suppliers', form)
      ElMessage.success('供应商创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await request.delete(`/suppliers/${row.id}`)
    ElMessage.success('供应商已删除')
    loadData()
  } catch (e) {
    // error handled by interceptor
  }
}

onMounted(() => { loadData() })
</script>
