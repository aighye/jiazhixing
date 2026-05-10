<template>
  <div>
    <div class="page-header"><h2>操作日志</h2></div>

    <div class="search-bar">
      <el-input v-model="username" placeholder="用户名" clearable style="width: 150px" @clear="loadData" />
      <el-select v-model="module" placeholder="模块" clearable style="width: 150px" @change="loadData">
        <el-option label="认证" value="auth" />
        <el-option label="客户" value="customer" />
        <el-option label="工单" value="work_order" />
        <el-option label="配件" value="parts" />
        <el-option label="财务" value="finance" />
      </el-select>
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="username" label="用户" width="100" />
      <el-table-column prop="action" label="操作" width="100" />
      <el-table-column prop="module" label="模块" width="100" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="ip_address" label="IP" width="130" />
      <el-table-column prop="created_at" label="时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const list = ref([])
const loading = ref(false)
const username = ref('')
const module = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize.value }
    if (username.value) params.username = username.value
    if (module.value) params.module = module.value
    const res = await request.get('/system/logs', { params })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

onMounted(loadData)
</script>

<style scoped>
/* Apple Design - Log List Page Styles */

/* Pagination spacing */
:deep(.el-pagination) {
  margin-top: var(--space-xl) !important;
  justify-content: flex-end;
}

/* Search bar input width */
:deep(.search-bar .el-input),
:deep(.search-bar .el-select) {
  width: 180px;
}
</style>
