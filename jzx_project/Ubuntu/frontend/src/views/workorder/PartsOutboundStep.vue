<template>
  <div>
    <div class="page-header">
      <h2>配件出库</h2>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索工单号/车牌号" clearable style="width: 220px" @clear="loadData" @keyup.enter="loadData" />
      <el-select v-model="outboundFilter" placeholder="出库状态" clearable style="width: 140px" @change="loadData">
        <el-option label="都未出库" value="none_outbound" />
        <el-option label="无备件" value="no_parts" />
        <el-option label="部分出库" value="partial" />
        <el-option label="全部出库" value="all" />
      </el-select>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="loadData" />
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="order_no" label="工单号" width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="$open(`/work-orders/${row.id}?from=parts-outbound`)">{{ row.order_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="plate_number" label="车牌号" width="120" />
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="service_type" label="维修类别" width="100" />
      <el-table-column label="出库状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.parts_outbound_status === 'all'" type="success" size="small">全部出库</el-tag>
          <el-tag v-else-if="row.parts_outbound_status === 'partial'" type="warning" size="small">部分出库</el-tag>
          <el-tag v-else-if="row.parts_outbound_status === 'none_outbound'" type="info" size="small">都未出库</el-tag>
          <el-tag v-else type="info" size="small">无备件</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="维修进度" width="120" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.repair_confirmed" type="success" size="small" effect="plain">维修✓</el-tag>
          <el-tag v-else type="info" size="small" effect="plain">在修</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="parts_cost" label="配件费用" width="120" align="right">
        <template #default="{ row }">¥{{ Number(row.parts_cost || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="total_amount" label="总金额" width="120" align="right">
        <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="creator_name" label="操作人" width="100" align="center">
        <template #default="{ row }">{{ row.creator_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" :page-sizes="[10, 20, 50]"
                   layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const keyword = ref('')
const outboundFilter = ref('')
const dateRange = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize.value, status: 0, keyword: keyword.value }
    if (dateRange.value) { params.start_date = dateRange.value[0]; params.end_date = dateRange.value[1] }
    const res = await request.get('/work-orders/list', { params })
    let items = res.data.items || []
    // 前端过滤出库状态
    if (outboundFilter.value) {
      items = items.filter(i => i.parts_outbound_status === outboundFilter.value)
    }
    list.value = items
    total.value = res.data.total
  } finally { loading.value = false }
}

onMounted(loadData)
</script>
