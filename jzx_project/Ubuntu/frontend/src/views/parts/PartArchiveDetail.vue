<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>配件档案详情</h2>
      <el-button @click="goBack">返回</el-button>
    </div>

    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>基本信息</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="配件编码">{{ part.part_no }}</el-descriptions-item>
        <el-descriptions-item label="配件名称">{{ part.name }}</el-descriptions-item>
        <el-descriptions-item label="拼音简码">{{ part.pinyin_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="单位">{{ part.unit || '-' }}</el-descriptions-item>
        <el-descriptions-item label="原厂编码">{{ part.factory_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="位置码">{{ part.location_code || '-' }}</el-descriptions-item>
        <el-descriptions-item label="库位编码">{{ part.warehouse_location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ part.brand || '-' }}</el-descriptions-item>
        <el-descriptions-item label="规格型号">{{ part.specification || '-' }}</el-descriptions-item>
        <el-descriptions-item label="适用车系">{{ part.applicable_vehicle || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>价格与库存</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="不含税成本单价">¥{{ Number(part.purchase_price || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="含税成本单价">¥{{ latestInboundPriceWithTax }}</el-descriptions-item>
        <el-descriptions-item label="参考销售单价（含税）">¥{{ Number(part.selling_price || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="当前库存">{{ part.stock_quantity }}</el-descriptions-item>
        <el-descriptions-item label="库龄(天)">{{ part.stock_age || 0 }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="part.discontinued ? 'danger' : 'success'" size="small">{{ part.discontinued ? '停用' : '启用' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="库存上限">{{ part.max_stock }}</el-descriptions-item>
        <el-descriptions-item label="库存下限">{{ part.min_stock }}</el-descriptions-item>
        <el-descriptions-item label="安全库存">{{ part.safety_stock }}</el-descriptions-item>
        <el-descriptions-item label="最小包装量">{{ part.min_package_qty }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="hover" style="margin-bottom: 20px;" v-if="part.archive_remark">
      <template #header>备注</template>
      <div style="white-space: pre-wrap;">{{ part.archive_remark }}</div>
    </el-card>

    <!-- 入库记录 -->
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>入库记录</template>
      <el-table :data="inboundRecords" stripe v-loading="recordsLoading" max-height="350" show-summary :summary-method="getInboundSummary">
        <el-table-column prop="ref_no" label="入库单号" width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="$open(`/parts/inbound/${row.ref_id}?from=archive-detail`)">{{ row.ref_no }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column label="不含税单价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.unit_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="不含税总价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.total_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="含税单价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.unit_price_with_tax || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="含税总价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.total_price_with_tax || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="税额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.tax_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" width="100" align="center">
          <template #default="{ row }">{{ row.operator_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" min-width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!recordsLoading && inboundRecords.length === 0" description="暂无入库记录" :image-size="60" />
    </el-card>

    <!-- 工单出库记录 -->
    <el-card shadow="hover">
      <template #header>工单出库记录</template>
      <el-table :data="workOrderRecords" stripe v-loading="recordsLoading" max-height="350" show-summary :summary-method="getOutboundSummary">
        <el-table-column prop="ref_no" label="工单号" width="200">
          <template #default="{ row }">
            <el-link v-if="row.ref_no" type="primary" @click="$open(`/work-orders/${row.ref_id}?from=archive-detail`)">{{ row.ref_no }}</el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.type === '工单出库'" type="danger" size="small">出库</el-tag>
            <el-tag v-else type="warning" size="small">回退</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column label="不含税单价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.unit_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="不含税总价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.total_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="含税单价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.unit_price_with_tax || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="含税总价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.total_price_with_tax || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="税额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.tax_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="operator_name" label="操作人" width="100" align="center">
          <template #default="{ row }">{{ row.operator_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" min-width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!recordsLoading && workOrderRecords.length === 0" description="暂无工单出库记录" :image-size="60" />
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
const recordsLoading = ref(false)
const part = ref({})
const inboundRecords = ref([])
const workOrderRecords = ref([])

const latestInbound = computed(() => inboundRecords.value[0] || {})
const latestInboundPriceWithTax = computed(() => {
  // 加权平均含税单价 = Σ(含税单价 × 数量) / Σ(数量)
  const records = inboundRecords.value
  if (!records.length) return '0.00'
  let totalAmountWithTax = 0
  let totalQty = 0
  for (const r of records) {
    const qty = Number(r.quantity) || 0
    const priceWithTax = Number(r.unit_price_with_tax) || 0
    totalAmountWithTax += priceWithTax * qty
    totalQty += qty
  }
  return totalQty > 0 ? (totalAmountWithTax / totalQty).toFixed(2) : '0.00'
})
const latestInboundTotalNoTax = computed(() => {
  // 所有入库单不含税总价加总
  return inboundRecords.value.reduce((sum, r) => sum + (Number(r.total_price) || 0), 0).toFixed(2)
})
const latestInboundTotalWithTax = computed(() => {
  // 所有入库单含税总价加总
  return inboundRecords.value.reduce((sum, r) => sum + (Number(r.total_price_with_tax) || 0), 0).toFixed(2)
})
const latestInboundTaxAmount = computed(() => {
  // 所有入库单总税额加总
  return inboundRecords.value.reduce((sum, r) => sum + (Number(r.tax_amount) || 0), 0).toFixed(2)
})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

function getInboundSummary({ columns, data }) {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '小计'; return }
    if (idx === 1) { sums[idx] = data.reduce((s, r) => s + (r.quantity || 0), 0); return }
    if (idx === 2) { sums[idx] = '-'; return }
    if (idx === 3) { sums[idx] = '¥' + data.reduce((s, r) => s + Number(r.total_price || 0), 0).toFixed(2); return }
    if (idx === 4) { sums[idx] = '-'; return }
    if (idx === 5) { sums[idx] = '¥' + data.reduce((s, r) => s + Number(r.total_price_with_tax || 0), 0).toFixed(2); return }
    if (idx === 6) { sums[idx] = '¥' + data.reduce((s, r) => s + Number(r.tax_amount || 0), 0).toFixed(2); return }
    sums[idx] = ''
  })
  return sums
}

function getOutboundSummary({ columns, data }) {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '小计'; return }
    if (idx === 1) { sums[idx] = ''; return }
    if (idx === 2) { sums[idx] = data.reduce((s, r) => s + (r.quantity || 0), 0); return }
    if (idx === 3) { sums[idx] = '-'; return }
    if (idx === 4) { sums[idx] = '¥' + data.reduce((s, r) => s + Number(r.total_price || 0), 0).toFixed(2); return }
    if (idx === 5) { sums[idx] = '-'; return }
    if (idx === 6) { sums[idx] = '¥' + data.reduce((s, r) => s + Number(r.total_price_with_tax || 0), 0).toFixed(2); return }
    if (idx === 7) { sums[idx] = '¥' + data.reduce((s, r) => s + Number(r.tax_amount || 0), 0).toFixed(2); return }
    sums[idx] = ''
  })
  return sums
}

async function loadData() {
  loading.value = true
  recordsLoading.value = true
  try {
    const id = route.params.id
    const [partRes, recordsRes] = await Promise.all([
      request.get(`/parts/${id}`),
      request.get(`/parts/${id}/stock-records`)
    ])
    part.value = partRes.data
    const allRecords = recordsRes.data || []
    inboundRecords.value = allRecords.filter(r => r.type === '入库')
    workOrderRecords.value = allRecords.filter(r => r.type === '工单出库' || r.type === '工单出库回退')
  } finally {
    loading.value = false
    recordsLoading.value = false
  }
}

onMounted(loadData)
</script>
