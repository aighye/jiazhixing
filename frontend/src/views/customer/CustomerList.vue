<template>
  <div>
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增客户
      </el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索客户名/手机号/编号" clearable style="width: 250px" @clear="loadData" @keyup.enter="loadData" />
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="customer_no" label="客户编号" width="180">
        <template #default="{ row }">
          <el-link type="primary" @click="$open(`/customers/${row.id}?from=customer-list`)">{{ row.customer_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="gender" label="性别" width="70">
        <template #default="{ row }">{{ ['', '男', '女'][row.gender] || '未知' }}</template>
      </el-table-column>
      <el-table-column prop="customer_type" label="类型" width="80">
        <template #default="{ row }">{{ row.customer_type === 1 ? '个人' : '企业' }}</template>
      </el-table-column>
      <el-table-column prop="vip_level" label="VIP" width="60">
        <template #default="{ row }">
          <el-tag v-if="row.vip_level > 0" type="warning" size="small">VIP{{ row.vip_level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_spending" label="累计消费" width="120">
        <template #default="{ row }">¥{{ Number(row.total_spending || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="vehicle_count" label="车辆数" width="80" />
      <el-table-column prop="creator_name" label="操作人" width="100" align="center">
        <template #default="{ row }">{{ row.creator_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="160">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button type="primary" link size="small" @click="showDialog(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" :page-sizes="[10, 20, 50]"
                   layout="total, sizes, prev, pager, next"
                   @size-change="loadData" @current-change="loadData" />

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑客户' : '新增客户'" width="600px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名" required>
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" required>
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender" style="width: 100%">
                <el-option label="未知" :value="0" />
                <el-option label="男" :value="1" />
                <el-option label="女" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户类型">
              <el-select v-model="form.customer_type" style="width: 100%">
                <el-option label="个人" :value="1" />
                <el-option label="企业" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
        </el-form-item>
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
import { ElMessage, ElMessageBox } from 'element-plus'

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
  name: '', phone: '', email: '', gender: 0, customer_type: 1, address: '', remark: ''
})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/customers/list', { params: { page: page.value, per_page: pageSize.value, keyword: keyword.value } })
    list.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function showDialog(row) {
  editingId.value = row ? row.id : null
  Object.assign(form, { name: '', phone: '', email: '', gender: 0, customer_type: 1, address: '', remark: '' })
  if (row) Object.assign(form, row)
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.name || !form.phone) return ElMessage.warning('请填写必填项')
  submitting.value = true
  try {
    if (editingId.value) {
      await request.put(`/customers/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/customers', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定删除该客户？', '提示', { type: 'warning' })
  await request.delete(`/customers/${row.id}`)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
/* Apple Design - Customer List Page Styles */

/* Pagination spacing */
:deep(.el-pagination) {
  margin-top: var(--space-xl) !important;
  justify-content: flex-end;
}

/* Search input width */
:deep(.search-bar .el-input) {
  width: 250px;
}

/* Table actions spacing */
.table-actions {
  display: flex;
  gap: var(--space-xs);
}
</style>
