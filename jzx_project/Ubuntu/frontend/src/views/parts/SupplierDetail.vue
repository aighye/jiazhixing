<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>供应商详情</h2>
      <el-button @click="goBack">返回列表</el-button>
    </div>

    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>基本信息</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="供应商编码">{{ detail.code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="供应商名称">{{ detail.name }}</el-descriptions-item>
        <el-descriptions-item label="信用等级">
          <el-rate v-model="detail.credit_level" disabled :max="5" />
        </el-descriptions-item>
        <el-descriptions-item label="联系人">{{ detail.contact_person || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ detail.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status === 1 ? 'success' : 'danger'" size="small">
            {{ detail.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="3">{{ detail.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开户银行">{{ detail.bank_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="银行账号" :span="2">{{ detail.bank_account || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="3">{{ detail.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="hover">
      <template #header>入库单明细</template>
      <el-table :data="inbounds" stripe v-loading="inboundsLoading" style="width: 100%">
        <el-table-column prop="inbound_no" label="入库单号" width="160">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/parts/inbound/${row.id}`)">{{ row.inbound_no }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="总数量" width="100" align="center">
          <template #default="{ row }">{{ row.total_quantity || 0 }}</template>
        </el-table-column>
        <el-table-column label="总金额" width="130" align="right">
          <template #default="{ row }">¥{{ (row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="发票类型" width="100" align="center">
          <template #default="{ row }">{{ row.invoice_type || '无发票' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="inboundStatusType(row.status)" size="small">{{ inboundStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inbound_by_name" label="入库人" width="100" />
        <el-table-column label="入库时间" width="170">
          <template #default="{ row }">{{ row.inbound_at || '-' }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
      </el-table>
      <div v-if="inboundsTotal > 0" style="margin-top: 16px; display: flex; justify-content: flex-end;">
        <el-pagination
          v-model:current-page="inboundsPage"
          :total="inboundsTotal"
          :page-size="10"
          layout="total, prev, pager, next"
          @current-change="loadInbounds"
        />
      </div>
      <el-empty v-if="!inboundsLoading && inbounds.length === 0" description="暂无入库记录" />
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

const inbounds = ref([])
const inboundsLoading = ref(false)
const inboundsTotal = ref(0)
const inboundsPage = ref(1)

async function loadDetail() {
  loading.value = true
  try {
    const res = await request.get(`/suppliers/${route.params.id}`)
    detail.value = res.data
  } finally {
    loading.value = false
  }
}

async function loadInbounds() {
  inboundsLoading.value = true
  try {
    const res = await request.get(`/suppliers/${route.params.id}/inbounds`, {
      params: { page: inboundsPage.value, per_page: 10 }
    })
    inbounds.value = res.data.items
    inboundsTotal.value = res.data.total
  } finally {
    inboundsLoading.value = false
  }
}

function inboundStatusName(status) {
  const map = { 0: '待入库', 1: '已入库', 2: '已取消' }
  return map[status] || '未知'
}

function inboundStatusType(status) {
  const map = { 0: 'warning', 1: 'success', 2: 'info' }
  return map[status] || 'info'
}

function goBack() {
  router.push('/parts/suppliers')
}

onMounted(() => { loadDetail(); loadInbounds() })
</script>
