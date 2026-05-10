<template>
  <div>
    <div class="page-header">
      <h2>维修项目管理</h2>
      <el-button type="primary" @click="openDialog()">新增维修项目</el-button>
    </div>

    <!-- 搜索栏 -->
    <el-card shadow="never" style="margin-bottom: 16px;">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="项目名称/编码" clearable style="width: 200px;" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="全部分类" clearable style="width: 140px;">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100px;">
            <el-option label="启用" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table :data="tableData" stripe v-loading="loading" border>
        <el-table-column prop="item_code" label="项目编码" width="120" />
        <el-table-column prop="item_name" label="项目名称" min-width="160" />
        <el-table-column prop="labor_hours" label="标准工时" width="100" align="center">
          <template #default="{ row }">{{ row.labor_hours }} h</template>
        </el-table-column>
        <el-table-column prop="labor_price" label="工时单价" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.labor_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="labor_amount" label="工时费" width="110" align="right">
          <template #default="{ row }">
            <span style="font-weight: 500;">¥{{ Number(row.labor_amount).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="关联配件" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ (row.parts || []).length }} 个</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="openDialog(row)">编辑</el-button>
            <el-button type="warning" size="small" link @click="openPartsDialog(row)">配件</el-button>
            <el-popconfirm title="确定删除此维修项目？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" size="small" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑维修项目' : '新增维修项目'" width="550px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="项目编码">
          <el-input :model-value="isEdit ? form.item_code : '系统自动生成'" disabled />
        </el-form-item>
        <el-form-item label="项目名称" prop="item_name">
          <el-input v-model="form.item_name" placeholder="如：更换机油机滤" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="标准工时" prop="labor_hours">
              <el-input-number v-model="form.labor_hours" :min="0" :precision="1" :step="0.5" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工时单价" prop="labor_price">
              <el-input-number v-model="form.labor_price" :min="0" :precision="2" :step="10" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="工时费">
          <el-input :model-value="'¥' + (Number(form.labor_hours || 0) * Number(form.labor_price || 0)).toFixed(2)" disabled />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="项目说明" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" :max="999" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 配件关联对话框 -->
    <el-dialog v-model="partsDialogVisible" title="关联配件" width="700px" @open="loadTemplateParts">
      <div style="margin-bottom: 12px;">
        <el-input v-model="partKeyword" placeholder="搜索配件名称/编号" clearable style="width: 250px;" />
      </div>
      <el-table :data="filteredPartOptions" stripe border size="small" max-height="250" @row-click="onPartSelect">
        <el-table-column prop="part_no" label="配件编号" width="120" />
        <el-table-column prop="name" label="配件名称" min-width="140" />
        <el-table-column prop="unit" label="单位" width="60" align="center" />
        <el-table-column prop="brand" label="品牌" width="80" />
        <el-table-column label="销售单价" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.selling_price || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存" width="70" align="center" />
      </el-table>
      <div style="margin-top: 12px;">
        <h4 style="margin: 0 0 8px;">已关联配件</h4>
        <el-table :data="templateParts" stripe border size="small" v-loading="partsLoading">
          <el-table-column prop="part_no" label="配件编号" width="120" />
          <el-table-column prop="part_name" label="配件名称" min-width="140" />
          <el-table-column prop="unit" label="单位" width="60" align="center" />
          <el-table-column label="销售单价" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.selling_price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="数量" width="100">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" size="small" style="width: 80px;" @change="updatePartQty(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="70" align="center">
            <template #default="{ row }">
              <el-button type="danger" size="small" link @click="removePart(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="partsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])
const categories = ref([])

const searchForm = reactive({ keyword: '', category: '', status: null })
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

const form = reactive({
  id: null,
  item_name: '', item_code: '', category: '', labor_hours: 1, labor_price: 100,
  description: '', status: 1, sort_order: 0, remark: ''
})

const rules = {
  item_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

// ========== 配件关联 ==========
const partsDialogVisible = ref(false)
const partsLoading = ref(false)
const partKeyword = ref('')
const partOptions = ref([])
const currentTemplateId = ref(null)
const templateParts = ref([])

const filteredPartOptions = computed(() => {
  if (!partKeyword.value) return partOptions.value
  const kw = partKeyword.value.toLowerCase()
  return partOptions.value.filter(p =>
    (p.part_no || '').toLowerCase().includes(kw) ||
    (p.name || '').toLowerCase().includes(kw)
  )
})

async function openPartsDialog(row) {
  currentTemplateId.value = row.id
  partKeyword.value = ''
  partsDialogVisible.value = true
  // 加载配件列表
  try {
    const res = await request.get('/parts/list', { params: { per_page: 999, status: 1 } })
    partOptions.value = res.data.items || []
  } catch (e) { /* ignore */ }
}

async function loadTemplateParts() {
  if (!currentTemplateId.value) return
  partsLoading.value = true
  try {
    const res = await request.get(`/repair-items/${currentTemplateId.value}`)
    templateParts.value = res.data.parts || []
  } finally { partsLoading.value = false }
}

async function onPartSelect(row) {
  if (!currentTemplateId.value) return
  try {
    await request.post(`/repair-items/${currentTemplateId.value}/parts`, {
      part_id: row.id,
      quantity: 1
    })
    ElMessage.success('配件关联成功')
    loadTemplateParts()
    loadData()
  } catch (e) { /* handled */ }
}

async function updatePartQty(row) {
  try {
    await request.post(`/repair-items/${currentTemplateId.value}/parts`, {
      part_id: row.part_id,
      quantity: row.quantity
    })
  } catch (e) { /* handled */ }
}

async function removePart(row) {
  try {
    await request.delete(`/repair-items/${currentTemplateId.value}/parts/${row.id}`)
    ElMessage.success('配件关联已删除')
    loadTemplateParts()
    loadData()
  } catch (e) { /* handled */ }
}

// ========== 基础 CRUD ==========
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: searchForm.keyword,
      category: searchForm.category,
      status: searchForm.status
    }
    const res = await request.get('/repair-items/list', { params })
    tableData.value = res.data.items
    pagination.total = res.data.total
  } finally { loading.value = false }
}

async function loadCategories() {
  try {
    const res = await request.get('/repair-items/categories')
    categories.value = res.data || []
  } catch (e) { /* ignore */ }
}

function resetSearch() {
  searchForm.keyword = ''
  searchForm.category = ''
  searchForm.status = null
  pagination.page = 1
  loadData()
}

function openDialog(row) {
  isEdit.value = !!row
  if (row) {
    Object.assign(form, {
      id: row.id,
      item_name: row.item_name,
      item_code: row.item_code || '',
      category: row.category || '',
      labor_hours: row.labor_hours,
      labor_price: row.labor_price,
      description: row.description || '',
      status: row.status,
      sort_order: row.sort_order || 0,
      remark: row.remark || ''
    })
  } else {
    resetForm()
  }
  dialogVisible.value = true
}

function resetForm() {
  Object.assign(form, {
    id: null,
    item_name: '', item_code: '', category: '', labor_hours: 1, labor_price: 100,
    description: '', status: 1, sort_order: 0, remark: ''
  })
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await request.put(`/repair-items/${form.id}`, form)
      ElMessage.success('维修项目更新成功')
    } else {
      await request.post('/repair-items', form)
      ElMessage.success('维修项目创建成功')
    }
    dialogVisible.value = false
    loadData()
    loadCategories()
  } catch (e) {
    // handled by interceptor
  } finally { submitting.value = false }
}

async function handleDelete(row) {
  try {
    await request.delete(`/repair-items/${row.id}`)
    ElMessage.success('维修项目已删除')
    loadData()
    loadCategories()
  } catch (e) { /* handled */ }
}

onMounted(() => {
  loadData()
  loadCategories()
})
</script>
