<template>
  <div>
    <div class="page-header">
      <h2>出库管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新建出库单
      </el-button>
    </div>

    <!-- 搜索筛选栏 -->
    <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center;">
      <el-input v-model="searchKeyword" placeholder="搜索出库单号" clearable style="width: 220px;" @clear="loadData" @keyup.enter="loadData" />
      <el-select v-model="filterType" placeholder="出库类型" clearable style="width: 140px;" @change="loadData">
        <el-option label="维修出库" value="repair" />
        <el-option label="退库" value="return" />
        <el-option label="报废" value="scrap" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px;" @change="loadData">
        <el-option label="待出库" :value="0" />
        <el-option label="已出库" :value="1" />
      </el-select>
      <el-button type="primary" @click="loadData">查询</el-button>
      <el-button @click="resetFilter">重置</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="outbound_no" label="出库单号" width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="viewDetail(row)">{{ row.outbound_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="出库类型" width="110">
        <template #default="{ row }">
          <el-tag :type="typeTagMap[row.outbound_type]?.type || 'info'" size="small">
            {{ typeTagMap[row.outbound_type]?.label || row.outbound_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_quantity" label="总数量" width="90" align="center" />
      <el-table-column label="总金额" width="120" align="right">
        <template #default="{ row }">¥{{ Number(row.total_amount).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'warning'" size="small">{{ ['待出库', '已出库'][row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="outbound_by_name" label="出库人" width="100" />
      <el-table-column label="出库时间" width="160">
        <template #default="{ row }">{{ formatTime(row.outbound_at) }}</template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="100" align="center">
        <template #default="{ row }">{{ row.creator_name || '-' }}</template>
      </el-table-column>
      <el-table-column label="创建时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="140" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="viewDetail(row)">详情</el-button>
          <el-button v-if="row.status === 0" type="danger" link size="small" @click="handleCancel(row)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <!-- 新建出库单 -->
    <el-dialog v-model="dialogVisible" title="新建出库单" width="900px" top="5vh">
      <el-form :model="form" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="出库类型">
              <el-select v-model="form.outbound_type" style="width: 100%">
                <el-option label="维修出库" value="repair" />
                <el-option label="退库" value="return" />
                <el-option label="报废" value="scrap" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联工单">
              <el-input v-model="form.order_id" placeholder="工单ID（可选，留空为独立出库）" type="number" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
        <el-divider>出库明细</el-divider>
        <el-table :data="form.items" border size="small" style="width: 100%;">
          <el-table-column label="配件" min-width="240">
            <template #default="{ row }">
              <el-select v-model="row.part_id" filterable placeholder="选择配件" style="width: 100%;" @change="onPartChange(row)">
                <el-option v-for="p in partOptions" :key="p.id"
                  :label="`${p.part_no} - ${p.name} (库存:${p.stock_quantity})`"
                  :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="单位" width="70" align="center">
            <template #default="{ row }">{{ row.unit || '-' }}</template>
          </el-table-column>
          <el-table-column label="数量" width="100">
            <template #default="{ row }">
              <el-input v-model="row.quantity" type="number" size="small" placeholder="数量" />
            </template>
          </el-table-column>
          <el-table-column label="单价(加权)" width="120" align="right">
            <template #default="{ row }">{{ Number(row.unit_price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="小计" width="120" align="right">
            <template #default="{ row }">{{ ((Number(row.quantity) || 0) * (Number(row.unit_price) || 0)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button type="danger" :icon="Delete" circle size="small" @click="form.items.splice($index, 1)" />
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" plain @click="form.items.push({ part_id: '', unit: '', quantity: 1, unit_price: 0 })" style="margin-top: 10px;">添加配件</el-button>
        <div style="margin-top: 12px; text-align: right; color: #606266;">
          合计数量：<b>{{ formTotalQty }}</b> &nbsp;&nbsp;
          合计金额：<b style="color: #f56c6c;">¥{{ formTotalAmount.toFixed(2) }}</b>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认出库</el-button>
      </template>
    </el-dialog>

    <!-- 出库详情对话框 -->
    <el-dialog v-model="detailVisible" title="出库单详情" width="900px" top="5vh">
      <template v-if="currentDetail">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="出库单号">{{ currentDetail.outbound_no }}</el-descriptions-item>
          <el-descriptions-item label="出库类型">
            <el-tag :type="typeTagMap[currentDetail.outbound_type]?.type || 'info'" size="small">
              {{ typeTagMap[currentDetail.outbound_type]?.label || currentDetail.outbound_type }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentDetail.status === 1 ? 'success' : 'warning'" size="small">{{ ['待出库', '已出库'][currentDetail.status] }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总数量">{{ currentDetail.total_quantity }}</el-descriptions-item>
          <el-descriptions-item label="总金额">¥{{ Number(currentDetail.total_amount).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="出库时间">{{ formatTime(currentDetail.outbound_at) || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ currentDetail.creator_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentDetail.remark || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>出库明细</el-divider>
        <el-table :data="currentDetail.details || []" border size="small" style="width: 100%;">
          <el-table-column prop="part_no" label="配件编号" width="140" />
          <el-table-column prop="part_name" label="配件名称" min-width="140" />
          <el-table-column prop="quantity" label="数量" width="80" align="center" />
          <el-table-column label="单价" width="110" align="right">
            <template #default="{ row }">¥{{ Number(row.unit_price).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="小计" width="120" align="right">
            <template #default="{ row }">¥{{ Number(row.total_price).toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const typeTagMap = {
  repair: { label: '维修出库', type: '' },
  return: { label: '退库', type: 'warning' },
  scrap:  { label: '报废', type: 'danger' }
}

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const currentDetail = ref(null)
const submitting = ref(false)
const partOptions = ref([])

// 搜索筛选
const searchKeyword = ref('')
const filterType = ref('')
const filterStatus = ref('')

const form = reactive({ order_id: '', outbound_type: 'repair', remark: '', items: [{ part_id: '', unit: '', quantity: 1, unit_price: 0 }] })

const formTotalQty = computed(() => form.items.reduce((s, i) => s + (Number(i.quantity) || 0), 0))
const formTotalAmount = computed(() => form.items.reduce((s, i) => s + (Number(i.quantity) || 0) * (Number(i.unit_price) || 0), 0))

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

function resetFilter() {
  searchKeyword.value = ''
  filterType.value = ''
  filterStatus.value = ''
  page.value = 1
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize.value }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterType.value !== '' && filterType.value !== null) params.outbound_type = filterType.value
    if (filterStatus.value !== '' && filterStatus.value !== null) params.status = filterStatus.value
    const res = await request.get('/parts/outbound/list', { params })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadParts() {
  const res = await request.get('/parts/list', { params: { per_page: 1000 } })
  partOptions.value = res.data.items
}

function onPartChange(row) {
  const part = partOptions.value.find(p => p.id === row.part_id)
  if (part) {
    row.unit = part.unit || ''
    row.unit_price = part.purchase_price || 0
  }
}

function showDialog() {
  Object.assign(form, { order_id: '', outbound_type: 'repair', remark: '', items: [{ part_id: '', unit: '', quantity: 1, unit_price: 0 }] })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.items.length || !form.items[0].part_id) return ElMessage.warning('请添加配件')
  // 校验每行数量
  for (const item of form.items) {
    if (!item.part_id) return ElMessage.warning('请为每行选择配件')
    if (!item.quantity || Number(item.quantity) <= 0) return ElMessage.warning('出库数量必须大于0')
    const part = partOptions.value.find(p => p.id === item.part_id)
    if (part && Number(item.quantity) > part.stock_quantity) {
      return ElMessage.warning(`配件 ${part.name} 库存不足（当前库存: ${part.stock_quantity}）`)
    }
  }
  submitting.value = true
  try {
    await request.post('/parts/outbound', form)
    ElMessage.success('出库成功')
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

async function viewDetail(row) {
  const res = await request.get(`/parts/outbound/${row.id}`)
  currentDetail.value = res.data
  detailVisible.value = true
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm('确定要取消该出库单吗？取消后库存将回滚。', '确认取消', { type: 'warning' })
    await request.put(`/parts/outbound/${row.id}`, { status: 2 })
    ElMessage.success('出库单已取消')
    loadData()
  } catch (e) { /* cancelled */ }
}

onMounted(() => { loadData(); loadParts() })
</script>
