<template>
  <div>
    <div class="page-header">
      <h2>配件库存</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增配件
      </el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索配件名/编号/品牌" clearable style="width: 250px" @clear="loadData" @keyup.enter="loadData" />
      <el-button type="primary" @click="loadData">搜索</el-button>
      <el-button :type="showLowStock ? 'danger' : ''" @click="showLowStock = !showLowStock; loadData()">
        {{ showLowStock ? '显示全部' : '库存预警' }}
      </el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="part_no" label="配件编号" width="140" />
      <el-table-column prop="name" label="配件名称" width="150" />
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="brand" label="品牌" width="80" />
      <el-table-column prop="model" label="规格型号" width="120" />
      <el-table-column prop="unit" label="单位" width="60" />
      <el-table-column prop="purchase_price" label="采购价" width="90">
        <template #default="{ row }">¥{{ Number(row.purchase_price).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="selling_price" label="销售价" width="90">
        <template #default="{ row }">¥{{ Number(row.selling_price).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="stock_quantity" label="库存" width="80">
        <template #default="{ row }">
          <span :style="{ color: row.is_low_stock ? '#f56c6c' : '', fontWeight: row.is_low_stock ? 'bold' : '' }">
            {{ row.stock_quantity }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="min_stock" label="最低库存" width="80" />
      <el-table-column label="操作" fixed="right" width="140">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="showDialog(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" :page-sizes="[10, 20, 50]"
                   layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑配件' : '新增配件'" width="600px">
      <el-form :model="form" label-width="80px" class="dialog-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="配件编号" required>
              <el-input v-model="form.part_no" :disabled="!!editingId" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="配件名称" required>
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="品牌">
              <el-input v-model="form.brand" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="规格型号">
              <el-input v-model="form.model" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单位">
              <el-input v-model="form.unit" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="采购价">
              <el-input v-model="form.purchase_price" type="number" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="销售价">
              <el-input v-model="form.selling_price" type="number" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="初始库存">
              <el-input v-model="form.stock_quantity" type="number" :disabled="!!editingId" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最低库存">
              <el-input v-model="form.min_stock" type="number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高库存">
              <el-input v-model="form.max_stock" type="number" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const keyword = ref('')
const showLowStock = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)

const form = reactive({
  part_no: '', name: '', brand: '', model: '', unit: '个',
  purchase_price: 0, selling_price: 0, stock_quantity: 0, min_stock: 0, max_stock: 0
})

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: pageSize.value, keyword: keyword.value }
    if (showLowStock.value) params.low_stock = 1
    const res = await request.get('/parts/list', { params })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

function showDialog(row) {
  editingId.value = row ? row.id : null
  Object.assign(form, { part_no: '', name: '', brand: '', model: '', unit: '个', purchase_price: 0, selling_price: 0, stock_quantity: 0, min_stock: 0, max_stock: 0 })
  if (row) Object.assign(form, row)
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.part_no || !form.name) return ElMessage.warning('请填写必填项')
  submitting.value = true
  try {
    if (editingId.value) {
      await request.put(`/parts/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await request.post('/parts', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally { submitting.value = false }
}

onMounted(loadData)
</script>
