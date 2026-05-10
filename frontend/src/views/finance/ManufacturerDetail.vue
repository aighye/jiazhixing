<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>索赔厂家详情</h2>
      <el-button @click="goBack">返回列表</el-button>
    </div>

    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>基本信息</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="厂家编码">{{ detail.code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="厂家名称">{{ detail.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status === 1 ? 'success' : 'info'" size="small">
            {{ detail.status_name }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="联系人">{{ detail.contact_person || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>备注</template>
      <div style="color: #606266;">{{ detail.remark || '无' }}</div>
    </el-card>

    <el-card shadow="hover">
      <template #header>工单明细</template>
      <el-table :data="workOrders" stripe v-loading="woLoading" style="width: 100%">
        <el-table-column prop="order_no" label="工单号" width="170">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/work-orders/${row.id}`)">{{ row.order_no }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="plate_number" label="车牌号" width="120" />
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column label="维修类别" width="100">
          <template #default="{ row }">{{ row.category_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="woStatusType(row.status)" size="small">{{ row.status_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="总金额" width="120" align="right">
          <template #default="{ row }">¥{{ (row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="操作人" width="100" />
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ row.created_at || '-' }}</template>
        </el-table-column>
      </el-table>
      <div v-if="woTotal > 0" style="margin-top: 16px; display: flex; justify-content: flex-end;">
        <el-pagination
          v-model:current-page="woPage"
          :total="woTotal"
          :page-size="10"
          layout="total, prev, pager, next"
          @current-change="loadWorkOrders"
        />
      </div>
      <el-empty v-if="!woLoading && workOrders.length === 0" description="暂无关联工单" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const detail = ref({})

const workOrders = ref([])
const woLoading = ref(false)
const woTotal = ref(0)
const woPage = ref(1)

async function loadDetail() {
  loading.value = true
  try {
    const res = await request.get(`/dict/manufacturers/${route.params.id}`)
    detail.value = res.data || {}
  } catch (e) {
    console.error('加载索赔厂家详情失败:', e)
  } finally {
    loading.value = false
  }
}

async function loadWorkOrders() {
  woLoading.value = true
  try {
    const res = await request.get(`/dict/manufacturers/${route.params.id}/work-orders`, {
      params: { page: woPage.value, per_page: 10 }
    })
    workOrders.value = res.data?.items || []
    woTotal.value = res.data?.total || 0
  } catch (e) {
    console.error('加载工单列表失败:', e)
  } finally {
    woLoading.value = false
  }
}

function woStatusType(status) {
  const map = { 0: 'info', 1: 'warning', 2: 'success', 3: 'success', 4: 'success', 5: 'info' }
  return map[status] || 'info'
}

function goBack() {
  router.push('/finance/manufacturers')
}

onMounted(() => { loadDetail(); loadWorkOrders() })
</script>
