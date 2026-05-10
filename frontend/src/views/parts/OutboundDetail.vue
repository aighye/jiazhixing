<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>出库单详情</h2>
      <el-button @click="goBack">返回</el-button>
    </div>
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>单据信息</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="出库单号">{{ data.outbound_no }}</el-descriptions-item>
        <el-descriptions-item label="出库类型">{{ data.outbound_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="总数量">{{ data.total_quantity }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ Number(data.total_amount).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ ['待出库', '已出库'][data.status] || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(data.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ data.creator_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ data.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <el-card shadow="hover">
      <template #header>出库明细</template>
      <el-table :data="data.details || []" stripe>
        <el-table-column prop="part_no" label="配件编号" width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="$open(`/parts/archive/${row.part_id}?from=outbound-detail`)">{{ row.part_no }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="part_name" label="配件名称" min-width="140" />
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column prop="unit_price" label="单价" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.unit_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_price" label="小计" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.total_price).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

function goBack() {
  router.back()
}
const loading = ref(false)
const data = ref({})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const res = await request.get(`/parts/outbound/${route.params.id}`)
    data.value = res.data
  } finally { loading.value = false }
}

onMounted(loadData)
</script>
