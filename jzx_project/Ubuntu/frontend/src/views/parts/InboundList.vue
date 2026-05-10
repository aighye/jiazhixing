<template>
  <div>
    <div class="page-header">
      <h2>入库管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新建入库单
      </el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="inbound_no" label="入库单号" width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="viewDetail(row)">{{ row.inbound_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="supplier_name" label="供应商" width="150" />
      <el-table-column prop="total_quantity" label="总数量" width="100" />
      <el-table-column prop="total_amount" label="总金额" width="120">
        <template #default="{ row }">¥{{ Number(row.total_amount).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ ['待入库', '已入库'][row.status] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="inbound_at" label="入库时间" width="160">
        <template #default="{ row }">{{ formatTime(row.inbound_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="100">
        <template #default="{ row }">
          <el-button v-if="row.status === 0" type="primary" link size="small" @click="editInbound(row)">修改</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <!-- 新建入库单 -->
    <el-dialog v-model="dialogVisible" title="新建入库单" width="1200px" top="5vh">
      <el-form :model="form" label-width="100px">
        <el-form-item label="供应商">
          <el-select v-model="form.supplier_id" filterable clearable placeholder="请选择" style="width: 100%">
            <el-option v-for="s in supplierOptions" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="4">
            <el-form-item label="发票类型">
              <el-select v-model="form.invoice_type" style="width: 100%;" @change="onInvoiceTypeChange">
                <el-option label="专票" value="专票" />
                <el-option label="普票" value="普票" />
                <el-option label="无发票" value="无发票" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="税率(%)">
              <el-input v-model="form.tax_rate" placeholder="税率" type="number" @input="onTaxRateChange" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="总数量">
              <el-input :model-value="totalQuantity" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="不含税总金额">
              <el-input :model-value="'¥' + totalAmountNoTax.toFixed(2)" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="总税额">
              <el-input :model-value="'¥' + (totalAmountWithTax - totalAmountNoTax).toFixed(2)" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="含税总金额">
              <el-input :model-value="'¥' + totalAmountWithTax.toFixed(2)" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
        <el-divider>入库明细</el-divider>
        <el-table :data="form.items" border size="small" style="width: 100%;">
          <el-table-column label="配件" min-width="200">
            <template #default="{ row }">
              <el-select v-model="row.part_id" filterable placeholder="选择配件" style="width: 100%;" @change="onPartChange(row)">
                <el-option v-for="p in partOptions" :key="p.id" :label="`${p.part_no} - ${p.name}`" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="单位" width="70" align="center">
            <template #default="{ row }">{{ row.unit || '-' }}</template>
          </el-table-column>
          <el-table-column label="数量" width="90">
            <template #default="{ row }">
              <el-input v-model="row.quantity" type="number" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="含税单价" width="120">
            <template #default="{ row }">
              <el-input v-model="row.unit_price_with_tax" type="number" size="small" @input="calcNoTaxPrice(row)" @blur="row.unit_price_with_tax = Number(Number(row.unit_price_with_tax).toFixed(2))" />
            </template>
          </el-table-column>
          <el-table-column label="不含税单价" width="120" align="right">
            <template #default="{ row }">{{ Number(row.unit_price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="不含税总价" width="120" align="right">
            <template #default="{ row }">{{ ((Number(row.quantity) || 0) * (Number(row.unit_price) || 0)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="含税总价" width="120" align="right">
            <template #default="{ row }">{{ ((Number(row.quantity) || 0) * (Number(row.unit_price_with_tax) || 0)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="税额" width="100" align="right">
            <template #default="{ row }">{{ ((Number(row.quantity) || 0) * (Number(row.unit_price_with_tax) || 0) - (Number(row.quantity) || 0) * (Number(row.unit_price) || 0)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="库位" width="120">
            <template #default="{ row }">
              <el-input v-model="row.location" size="small" placeholder="库位" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button type="danger" :icon="Delete" circle size="small" @click="form.items.splice($index, 1)" />
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" plain @click="form.items.push({ part_id: '', unit: '', quantity: 1, unit_price: 0, unit_price_with_tax: 0, location: '' })" style="margin-top: 10px;">添加配件</el-button>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="success" :loading="submitting" @click="handleSubmit('draft')">暂存</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit('confirm')">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 编辑入库单弹窗 -->
    <el-dialog v-model="editVisible" title="修改入库单" width="1200px" top="5vh">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="供应商">
          <el-select v-model="editForm.supplier_id" filterable clearable placeholder="请选择" style="width: 100%">
            <el-option v-for="s in supplierOptions" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="4">
            <el-form-item label="发票类型">
              <el-select v-model="editForm.invoice_type" style="width: 100%;" @change="onEditInvoiceTypeChange">
                <el-option label="专票" value="专票" />
                <el-option label="普票" value="普票" />
                <el-option label="无发票" value="无发票" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="税率(%)">
              <el-input v-model="editForm.tax_rate" placeholder="税率" type="number" @input="onEditTaxRateChange" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="总数量">
              <el-input :model-value="editTotalQuantity" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="不含税总金额">
              <el-input :model-value="'¥' + editTotalAmountNoTax.toFixed(2)" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="总税额">
              <el-input :model-value="'¥' + (editTotalAmountWithTax - editTotalAmountNoTax).toFixed(2)" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="含税总金额">
              <el-input :model-value="'¥' + editTotalAmountWithTax.toFixed(2)" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" />
        </el-form-item>
        <el-divider>入库明细</el-divider>
        <el-table :data="editForm.items" border size="small" style="width: 100%;">
          <el-table-column label="配件" min-width="200">
            <template #default="{ row }">
              <el-select v-model="row.part_id" filterable placeholder="选择配件" style="width: 100%;" @change="onEditPartChange(row)">
                <el-option v-for="p in partOptions" :key="p.id" :label="`${p.part_no} - ${p.name}`" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="单位" width="70" align="center">
            <template #default="{ row }">{{ row.unit || '-' }}</template>
          </el-table-column>
          <el-table-column label="数量" width="90">
            <template #default="{ row }">
              <el-input v-model="row.quantity" type="number" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="含税单价" width="120">
            <template #default="{ row }">
              <el-input v-model="row.unit_price_with_tax" type="number" size="small" @input="calcEditNoTaxPrice(row)" @blur="row.unit_price_with_tax = Number(Number(row.unit_price_with_tax).toFixed(2))" />
            </template>
          </el-table-column>
          <el-table-column label="不含税单价" width="120" align="right">
            <template #default="{ row }">{{ Number(row.unit_price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="不含税总价" width="120" align="right">
            <template #default="{ row }">{{ ((Number(row.quantity) || 0) * (Number(row.unit_price) || 0)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="含税总价" width="120" align="right">
            <template #default="{ row }">{{ ((Number(row.quantity) || 0) * (Number(row.unit_price_with_tax) || 0)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="税额" width="100" align="right">
            <template #default="{ row }">{{ ((Number(row.quantity) || 0) * (Number(row.unit_price_with_tax) || 0) - (Number(row.quantity) || 0) * (Number(row.unit_price) || 0)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="库位" width="120">
            <template #default="{ row }">
              <el-input v-model="row.location" size="small" placeholder="库位" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button type="danger" :icon="Delete" circle size="small" @click="editForm.items.splice($index, 1)" />
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" plain @click="editForm.items.push({ part_id: '', unit: '', quantity: 1, unit_price: 0, unit_price_with_tax: 0, location: '' })" style="margin-top: 10px;">添加配件</el-button>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="success" :loading="submitting" @click="handleUpdate('draft')">暂存</el-button>
        <el-button type="primary" :loading="submitting" @click="handleUpdate('confirm')">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="入库详情" width="1200px" top="5vh">
      <template v-if="currentDetail">
        <el-descriptions :column="5" border size="small">
          <el-descriptions-item label="入库单号">{{ currentDetail.inbound_no }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ currentDetail.supplier_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发票类型">{{ currentDetail.invoice_type || '无发票' }}</el-descriptions-item>
          <el-descriptions-item label="税率(%)">{{ currentDetail.tax_rate || 0 }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentDetail.status === 1 ? 'success' : 'info'" size="small">{{ currentDetail.status === 1 ? '已入库' : '暂存' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总数量">{{ currentDetail.total_quantity }}</el-descriptions-item>
          <el-descriptions-item label="不含税总金额">¥{{ Number(currentDetail.total_amount || 0).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="总税额">¥{{ (Number(currentDetail.total_amount || 0) * (1 + (Number(currentDetail.tax_rate) || 0) / 100) - Number(currentDetail.total_amount || 0)).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="含税总金额">¥{{ (Number(currentDetail.total_amount || 0) * (1 + (Number(currentDetail.tax_rate) || 0) / 100)).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="入库时间">{{ currentDetail.inbound_at ? currentDetail.inbound_at.replace('T', ' ').substring(0, 16) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ currentDetail.remark || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>入库明细</el-divider>
        <el-table :data="currentDetail.details || []" border size="small" style="width: 100%;">
          <el-table-column prop="part_no" label="配件编号" min-width="120" />
          <el-table-column prop="part_name" label="配件名称" min-width="120" />
          <el-table-column label="单位" width="70" align="center">
            <template #default="{ row }">{{ row.unit || '-' }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="70" align="center" />
          <el-table-column label="不含税单价" width="110" align="right">
            <template #default="{ row }">{{ Number(row.unit_price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="含税单价" width="110" align="right">
            <template #default="{ row }">{{ Number(row.unit_price_with_tax || row.unit_price * (1 + (Number(currentDetail.tax_rate) || 0) / 100)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="不含税总价" width="110" align="right">
            <template #default="{ row }">{{ Number(row.total_price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="含税总价" width="110" align="right">
            <template #default="{ row }">{{ (Number(row.quantity || 0) * Number(row.unit_price_with_tax || row.unit_price * (1 + (Number(currentDetail.tax_rate) || 0) / 100))).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="税额" width="100" align="right">
            <template #default="{ row }">{{ (Number(row.quantity || 0) * Number(row.unit_price_with_tax || row.unit_price * (1 + (Number(currentDetail.tax_rate) || 0) / 100)) - Number(row.total_price || 0)).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="库位" width="100">
            <template #default="{ row }">{{ row.location || '-' }}</template>
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
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const editVisible = ref(false)
const currentDetail = ref(null)
const submitting = ref(false)
const supplierOptions = ref([])
const partOptions = ref([])
const editForm = reactive({ id: null, supplier_id: '', remark: '', invoice_type: '无发票', tax_rate: 0, items: [] })

const editTotalQuantity = computed(() => {
  return editForm.items.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0)
})
const editTotalAmountNoTax = computed(() => {
  return editForm.items.reduce((sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unit_price) || 0), 0)
})
const editTotalAmountWithTax = computed(() => {
  const rate = 1 + (Number(editForm.tax_rate) || 0) / 100
  return editTotalAmountNoTax.value * rate
})

const totalQuantity = computed(() => {
  return form.items.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0)
})
const totalAmountNoTax = computed(() => {
  return form.items.reduce((sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unit_price) || 0), 0)
})
const totalAmountWithTax = computed(() => {
  const rate = 1 + (Number(form.tax_rate) || 0) / 100
  return totalAmountNoTax.value * rate
})

const form = reactive({ supplier_id: '', remark: '', invoice_type: '专票', tax_rate: 13, items: [{ part_id: '', unit: '', quantity: 1, unit_price: 0, unit_price_with_tax: 0, location: '' }] })

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/parts/inbound/list', { params: { page: page.value, per_page: pageSize.value } })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadOptions() {
  const [sRes, pRes] = await Promise.all([
    request.get('/parts/suppliers'),
    request.get('/parts/list', { params: { per_page: 1000 } })
  ])
  supplierOptions.value = sRes.data
  partOptions.value = pRes.data.items
}

function onInvoiceTypeChange(val) {
  form.tax_rate = val === '专票' ? 13 : 0
  form.items.forEach(item => calcNoTaxPrice(item))
}

function onTaxRateChange() {
  form.items.forEach(item => calcNoTaxPrice(item))
}

function calcNoTaxPrice(row) {
  const rate = 1 + (Number(form.tax_rate) || 0) / 100
  row.unit_price = Math.round((Number(row.unit_price_with_tax) || 0) / rate * 100) / 100
}

function onPartChange(row) {
  const part = partOptions.value.find(p => p.id === row.part_id)
  if (part) {
    row.unit = part.unit || ''
    // 含税单价自动获取配件档案中的入库单价（含税）
    const rate = 1 + (Number(form.tax_rate) || 0) / 100
    row.unit_price_with_tax = part.latest_inbound_price_with_tax || 0
    row.unit_price = Math.round((Number(row.unit_price_with_tax) || 0) / rate * 100) / 100
  }
}

function showDialog() {
  Object.assign(form, { supplier_id: '', remark: '', invoice_type: '专票', tax_rate: 13, items: [{ part_id: '', unit: '', quantity: 1, unit_price: 0, unit_price_with_tax: 0, location: '' }] })
  dialogVisible.value = true
}

async function handleSubmit(action) {
  if (!form.supplier_id) return ElMessage.warning('请选择供应商')
  if (!form.items.length || !form.items[0].part_id) return ElMessage.warning('请添加配件')
  submitting.value = true
  try {
    const payload = { ...form, status: action === 'confirm' ? 1 : 0 }
    await request.post('/parts/inbound', payload)
    ElMessage.success(action === 'confirm' ? '入库成功' : '暂存成功')
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

async function viewDetail(row) {
  const res = await request.get(`/parts/inbound/${row.id}`)
  currentDetail.value = res.data
  detailVisible.value = true
}

async function editInbound(row) {
  const res = await request.get(`/parts/inbound/${row.id}`)
  const data = res.data
  editForm.id = data.id
  editForm.supplier_id = data.supplier_id
  editForm.remark = data.remark || ''
  editForm.invoice_type = data.invoice_type || '无发票'
  editForm.tax_rate = data.tax_rate || 0
  editForm.items = (data.details || []).map(d => ({
    part_id: d.part_id,
    unit: d.unit || '',
    quantity: d.quantity,
    unit_price: d.unit_price,
    unit_price_with_tax: Math.round(d.unit_price * (1 + (Number(data.tax_rate) || 0) / 100) * 100) / 100,
    location: d.location || ''
  }))
  editVisible.value = true
}

function onEditInvoiceTypeChange(val) {
  editForm.tax_rate = val === '专票' ? 13 : 0
  editForm.items.forEach(item => calcEditNoTaxPrice(item))
}

function onEditTaxRateChange() {
  editForm.items.forEach(item => calcEditNoTaxPrice(item))
}

function calcEditNoTaxPrice(row) {
  const rate = 1 + (Number(editForm.tax_rate) || 0) / 100
  row.unit_price = Math.round((Number(row.unit_price_with_tax) || 0) / rate * 100) / 100
}

function onEditPartChange(row) {
  const part = partOptions.value.find(p => p.id === row.part_id)
  if (part) {
    row.unit = part.unit || ''
    // 含税单价自动获取配件档案中的入库单价（含税）
    const rate = 1 + (Number(editForm.tax_rate) || 0) / 100
    row.unit_price_with_tax = part.latest_inbound_price_with_tax || 0
    row.unit_price = Math.round((Number(row.unit_price_with_tax) || 0) / rate * 100) / 100
  }
}

async function handleUpdate(action) {
  if (!editForm.items.length || !editForm.items[0].part_id) return ElMessage.warning('请添加配件')
  submitting.value = true
  try {
    const payload = { ...editForm, status: action === 'confirm' ? 1 : 0 }
    await request.put(`/parts/inbound/${editForm.id}`, payload)
    ElMessage.success(action === 'confirm' ? '入库成功' : '暂存成功')
    editVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

onMounted(() => { loadData(); loadOptions() })
</script>
