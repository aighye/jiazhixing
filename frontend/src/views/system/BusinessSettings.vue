<template>
  <div>
    <div class="page-header"><h2>业务设置</h2></div>

    <el-card v-loading="loading">
      <el-tabs v-model="activeTab">
        <!-- 业务参数 -->
        <el-tab-pane label="业务参数" name="params">
          <el-form :model="params" label-width="160px" style="max-width: 700px; margin-top: 16px;">
            <el-divider content-position="left">工单设置</el-divider>
            <el-form-item label="工单编号前缀">
              <el-input v-model="params.work_order_prefix" placeholder="如 WO" />
            </el-form-item>
            <el-form-item label="工单编号流水位数">
              <el-input-number v-model="params.work_order_seq_length" :min="4" :max="10" />
            </el-form-item>
            <el-form-item label="默认工时单价(元)">
              <el-input-number v-model="params.default_labor_rate" :min="0" :precision="2" />
            </el-form-item>

            <el-divider content-position="left">配件设置</el-divider>
            <el-form-item label="配件编号前缀">
              <el-input v-model="params.part_no_prefix" placeholder="如 P" />
            </el-form-item>
            <el-form-item label="默认税率(%)">
              <el-input-number v-model="params.default_tax_rate" :min="0" :max="100" :precision="2" />
            </el-form-item>
            <el-form-item label="库存预警开关">
              <el-switch v-model="params.stock_warning_enabled" active-value="true" inactive-value="false" />
            </el-form-item>
            <el-form-item label="库存预警阈值">
              <el-input-number v-model="params.stock_warning_threshold" :min="0" />
            </el-form-item>

            <el-divider content-position="left">客户设置</el-divider>
            <el-form-item label="客户编号前缀">
              <el-input v-model="params.customer_prefix" placeholder="如 C" />
            </el-form-item>
            <el-form-item label="默认积分比例">
              <el-input-number v-model="params.points_rate" :min="0" :precision="2" placeholder="消费1元得多少积分" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSaveParams">保存参数</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 业务字典 -->
        <el-tab-pane label="业务字典" name="dict">
          <div style="margin-bottom: 12px; display: flex; gap: 12px; flex-wrap: wrap;">
            <el-select v-model="currentDict" placeholder="选择字典类型" style="width: 180px;" @change="loadDictItems">
              <el-option v-for="d in dictTypes" :key="d.value" :label="d.label" :value="d.value" />
            </el-select>
            <el-button type="primary" size="small" @click="showDictDialog(null)">新增</el-button>
          </div>
          <el-table :data="dictItems" border size="small" max-height="450">
            <el-table-column prop="name" label="名称" min-width="150" />
            <el-table-column prop="code" label="编码" width="150" />
            <el-table-column prop="sort" label="排序" width="80" align="center" />
            <el-table-column prop="status" label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '启用' : '停用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="showDictDialog(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteDictItem(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 业务流程 -->
        <el-tab-pane label="业务流程" name="flow">
          <el-form :model="flowConfigs" label-width="200px" style="max-width: 700px; margin-top: 16px;">
            <el-divider content-position="left">工单流程</el-divider>
            <el-form-item label="自动进入在修">
              <el-switch v-model="flowConfigs.auto_start_repair" active-value="true" inactive-value="false" />
            </el-form-item>
            <el-form-item label="维修完成需所有配件出库">
              <el-switch v-model="flowConfigs.require_all_parts_out" active-value="true" inactive-value="false" />
            </el-form-item>
            <el-form-item label="出库完成自动进入完工">
              <el-switch v-model="flowConfigs.auto_complete_after_outbound" active-value="true" inactive-value="false" />
            </el-form-item>

            <el-divider content-position="left">配件流程</el-divider>
            <el-form-item label="添加配件时检查库存">
              <el-switch v-model="flowConfigs.check_stock_on_add" active-value="true" inactive-value="false" />
            </el-form-item>
            <el-form-item label="出库时检查库存">
              <el-switch v-model="flowConfigs.check_stock_on_outbound" active-value="true" inactive-value="false" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSaveFlow">保存流程配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 字典编辑弹窗 -->
    <el-dialog v-model="dictDialogVisible" :title="dictEditing ? '编辑字典项' : '新增字典项'" width="450px">
      <el-form :model="dictForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="dictForm.name" />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="dictForm.code" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="dictForm.sort" :min="0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="dictForm.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dictDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveDictItem">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const activeTab = ref('params')

// ========== 业务参数 ==========
const params = reactive({
  work_order_prefix: 'WO',
  work_order_seq_length: 7,
  default_labor_rate: 200,
  part_no_prefix: 'P',
  default_tax_rate: 13,
  stock_warning_enabled: 'true',
  stock_warning_threshold: 10,
  customer_prefix: 'C',
  points_rate: 1
})

// ========== 业务字典 ==========
const dictTypes = [
  { value: 'charge_type', label: '收款类型' },
  { value: 'fee_type', label: '收费类型' },
  { value: 'repair_category', label: '维修类别' },
  { value: 'service_type', label: '服务类型' },
  { value: 'vehicle_brand', label: '车辆品牌' },
  { value: 'payment_method', label: '付款方式' },
  { value: 'invoice_type', label: '发票类型' },
  { value: 'part_tax_rate', label: '配件销售税率' }
]
const currentDict = ref('charge_type')
const dictItems = ref([])
const dictDialogVisible = ref(false)
const dictEditing = ref(null)
const dictForm = reactive({ id: null, name: '', code: '', sort: 0, status: 1 })

// ========== 业务流程 ==========
const flowConfigs = reactive({
  auto_start_repair: 'false',
  require_all_parts_out: 'true',
  auto_complete_after_outbound: 'false',
  auto_start_payment: 'false',
  check_stock_on_add: 'false',
  check_stock_on_outbound: 'true'
})

// ========== 加载配置 ==========
async function loadConfigs() {
  loading.value = true
  try {
    const res = await request.get('/system/configs')
    const list = res.data || []
    for (const item of list) {
      const key = item.config_key
      const val = item.config_value
      if (key in params) params[key] = isNaN(val) ? val : Number(val)
      if (key in flowConfigs) flowConfigs[key] = val
    }
  } finally { loading.value = false }
}

// ========== 保存参数 ==========
async function handleSaveParams() {
  saving.value = true
  try {
    await request.put('/system/configs', { ...params })
    ElMessage.success('业务参数保存成功')
  } finally { saving.value = false }
}

// ========== 保存流程 ==========
async function handleSaveFlow() {
  saving.value = true
  try {
    await request.put('/system/configs', { ...flowConfigs })
    ElMessage.success('流程配置保存成功')
  } finally { saving.value = false }
}

// ========== 字典管理 ==========
async function loadDictItems() {
  try {
    const res = await request.get(`/system/dict-items?type=${currentDict.value}`)
    dictItems.value = res.data || []
  } catch (e) { /* handled */ }
}

function showDictDialog(row) {
  if (row) {
    dictEditing.value = true
    Object.assign(dictForm, { id: row.id, name: row.name, code: row.code, sort: row.sort, status: row.status })
  } else {
    dictEditing.value = false
    Object.assign(dictForm, { id: null, name: '', code: '', sort: 0, status: 1 })
  }
  dictDialogVisible.value = true
}

async function handleSaveDictItem() {
  if (!dictForm.name) { ElMessage.warning('请输入名称'); return }
  saving.value = true
  try {
    if (dictForm.id) {
      await request.put(`/system/dict-items/${dictForm.id}`, { ...dictForm, dict_type: currentDict.value })
    } else {
      await request.post('/system/dict-items', { ...dictForm, dict_type: currentDict.value })
    }
    ElMessage.success('保存成功')
    dictDialogVisible.value = false
    loadDictItems()
  } finally { saving.value = false }
}

async function handleDeleteDictItem(row) {
  await ElMessageBox.confirm(`确定删除"${row.name}"？`, '提示', { type: 'warning' })
  try {
    await request.delete(`/system/dict-items/${row.id}`)
    ElMessage.success('删除成功')
    loadDictItems()
  } catch (e) { /* handled */ }
}

onMounted(() => {
  loadConfigs()
  loadDictItems()
})
</script>

<style scoped>
:deep(.el-form) {
  max-width: 700px;
}
</style>
