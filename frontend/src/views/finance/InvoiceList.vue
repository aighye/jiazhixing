<template>
  <div>
    <div class="page-header">
      <h2>发票管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新开发票
      </el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="invoice_no" label="发票号" width="200" />
      <el-table-column prop="title" label="发票抬头" width="200" />
      <el-table-column prop="invoice_type" label="类型" width="80">
        <template #default="{ row }">{{ row.invoice_type === 'normal' ? '普通' : '专用' }}</template>
      </el-table-column>
      <el-table-column prop="amount" label="金额" width="120">
        <template #default="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="tax_amount" label="税额" width="100">
        <template #default="{ row }">¥{{ Number(row.tax_amount).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="['info', 'success', 'danger'][row.status]" size="small">
            {{ ['待开票', '已开票', '已作废'][row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="操作人" width="100" align="center">
        <template #default="{ row }">{{ row.creator_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="100">
        <template #default="{ row }">
          <el-button v-if="row.status === 0" type="success" link size="small" @click="handleIssue(row)">开具</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <el-dialog v-model="dialogVisible" title="新开发票" width="500px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-form-item label="抬头" required>
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="税号">
          <el-input v-model="form.tax_no" />
        </el-form-item>
        <el-form-item label="工单ID">
          <el-input v-model="form.order_id" type="number" />
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input v-model="form.amount" type="number" />
        </el-form-item>
        <el-form-item label="税额">
          <el-input v-model="form.tax_amount" type="number" />
        </el-form-item>
        <el-form-item label="发票类型">
          <el-select v-model="form.invoice_type" style="width: 100%">
            <el-option label="普通发票" value="normal" />
            <el-option label="专用发票" value="special" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">创建</el-button>
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
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const submitting = ref(false)

const form = reactive({ title: '', tax_no: '', order_id: '', amount: '', tax_amount: 0, invoice_type: 'normal' })

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/finance/invoices', { params: { page: page.value, per_page: pageSize.value } })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

function showDialog() {
  Object.assign(form, { title: '', tax_no: '', order_id: '', amount: '', tax_amount: 0, invoice_type: 'normal' })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.title || !form.amount) return ElMessage.warning('请填写必填项')
  submitting.value = true
  try {
    await request.post('/finance/invoices', form)
    ElMessage.success('发票创建成功')
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

async function handleIssue(row) {
  await request.put(`/finance/invoices/${row.id}/issue`)
  ElMessage.success('发票已开具')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
/* Apple Design - Invoice List Page Styles */

/* Pagination spacing */
:deep(.el-pagination) {
  margin-top: var(--space-xl) !important;
  justify-content: flex-end;
}
</style>
