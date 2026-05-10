<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>入库单详情</h2>
      <el-button @click="goBack">返回</el-button>
    </div>
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>单据信息</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="入库单号">{{ data.inbound_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ data.supplier_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="data.status === 1 ? 'success' : 'info'" size="small">{{ ['待入库', '已入库'][data.status] || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发票类型">{{ data.invoice_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="税率">{{ data.tax_rate ? data.tax_rate + '%' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="总数量">{{ data.total_quantity }}</el-descriptions-item>
        <el-descriptions-item label="不含税总金额">¥{{ noTaxTotal.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="总税额">¥{{ taxTotal.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="含税总金额">¥{{ withTaxTotal.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(data.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ data.creator_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="入库时间">{{ formatTime(data.inbound_at) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="1">{{ data.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <el-card shadow="hover">
      <template #header>入库明细</template>
      <el-table :data="data.details || []" stripe border size="small" show-summary :summary-method="getSummary">
        <el-table-column prop="part_no" label="配件编号" width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="$open(`/parts/archive/${row.part_id}?from=inbound-detail`)">{{ row.part_no }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="part_name" label="配件名称" min-width="140" />
        <el-table-column prop="unit" label="单位" width="70" align="center">
          <template #default="{ row }">{{ row.unit || '-' }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column label="含税单价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.unit_price_with_tax || calcWithTaxPrice(row.unit_price)).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="不含税单价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.unit_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="不含税总价" width="120" align="right">
          <template #default="{ row }">¥{{ (Number(row.quantity) * Number(row.unit_price)).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="含税总价" width="120" align="right">
          <template #default="{ row }">¥{{ (Number(row.quantity) * Number(row.unit_price_with_tax || calcWithTaxPrice(row.unit_price))).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="税额" width="100" align="right">
          <template #default="{ row }">¥{{ (Number(row.quantity) * Number(row.unit_price_with_tax || calcWithTaxPrice(row.unit_price)) - Number(row.quantity) * Number(row.unit_price)).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="location" label="库位" width="100">
          <template #default="{ row }">{{ row.location || '-' }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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

const taxRate = computed(() => (Number(data.value.tax_rate) || 0) / 100)

function calcWithTaxPrice(unitPrice) {
  return Number(unitPrice || 0) * (1 + taxRate.value)
}

const noTaxTotal = computed(() => {
  return (data.value.details || []).reduce((sum, d) => sum + Number(d.quantity || 0) * Number(d.unit_price || 0), 0)
})

const withTaxTotal = computed(() => {
  return noTaxTotal.value * (1 + taxRate.value)
})

const taxTotal = computed(() => {
  return withTaxTotal.value - noTaxTotal.value
})

function getSummary({ columns, data }) {
  const sums = []
  columns.forEach((col, index) => {
    if (index === 0) { sums[index] = '合计'; return }
    if (index === 1) { sums[index] = ''; return }
    if (index === 2) { sums[index] = ''; return }
    if (col.property === 'quantity') {
      sums[index] = data.reduce((s, r) => s + Number(r.quantity || 0), 0)
    } else if (col.label === '不含税总价') {
      sums[index] = '¥' + data.reduce((s, r) => s + Number(r.quantity || 0) * Number(r.unit_price || 0), 0).toFixed(2)
    } else if (col.label === '含税总价') {
      sums[index] = '¥' + data.reduce((s, r) => s + Number(r.quantity || 0) * Number(r.unit_price || 0) * (1 + taxRate.value), 0).toFixed(2)
    } else if (col.label === '税额') {
      const noTax = data.reduce((s, r) => s + Number(r.quantity || 0) * Number(r.unit_price || 0), 0)
      const withTax = noTax * (1 + taxRate.value)
      sums[index] = '¥' + (withTax - noTax).toFixed(2)
    } else {
      sums[index] = ''
    }
  })
  return sums
}

async function loadData() {
  loading.value = true
  try {
    const res = await request.get(`/parts/inbound/${route.params.id}`)
    data.value = res.data
  } finally { loading.value = false }
}

onMounted(loadData)
</script>
