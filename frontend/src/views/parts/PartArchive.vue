<template>
  <div>
    <div class="page-header">
      <h2>配件档案</h2>
      <el-button type="primary" @click="openAdd">
        <el-icon><Plus /></el-icon> 新增配件档案
      </el-button>
    </div>

    <div class="search-bar">
      <el-input v-model="keyword" placeholder="搜索配件编码/名称" clearable style="width: 250px" @clear="loadData" @keyup.enter="loadData" />
      <el-button type="primary" @click="loadData">搜索</el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="part_no" label="配件编码" width="130">
        <template #default="{ row }">
          <el-link type="primary" @click="$open(`/parts/archive/${row.id}?from=archive-list`)">{{ row.part_no }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="配件名称" min-width="140" />
      <el-table-column prop="unit" label="单位" width="60" align="center" />
      <el-table-column prop="brand" label="品牌" width="90" />
      <el-table-column prop="specification" label="规格型号" width="120" />
      <el-table-column prop="applicable_vehicle" label="适用车系" width="100" />
      <el-table-column prop="purchase_price" label="采购价" width="90" align="right">
        <template #default="{ row }">¥{{ Number(row.purchase_price || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="selling_price" label="销售价" width="90" align="right">
        <template #default="{ row }">¥{{ Number(row.selling_price || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="stock_quantity" label="库存" width="70" align="center" />
      <el-table-column prop="stock_age" label="库龄(天)" width="90" align="center" />
      <el-table-column prop="safety_stock" label="安全库存" width="90" align="center" />
      <el-table-column prop="warehouse_location" label="库位编码" width="100" />
      <el-table-column label="操作" fixed="right" width="100">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
                   :total="total" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: flex-end;"
                   @size-change="loadData" @current-change="loadData" />

    <!-- 编辑配件档案对话框 -->
    <el-dialog v-model="editVisible" title="编辑配件档案" width="900px" top="3vh">
      <el-form :model="form" label-width="90px" size="default">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="配件编码"><el-input v-model="form.part_no" disabled /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="配件名称"><el-input v-model="form.name" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="拼音简码"><el-input v-model="form.pinyin_code" disabled /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="单位">
              <el-select v-model="form.unit" filterable allow-create placeholder="请选择" style="width: 100%;">
                <el-option v-for="u in unitOptions" :key="u" :label="u" :value="u" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="原厂编码"><el-input v-model="form.factory_code" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="位置码"><el-input v-model="form.location_code" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="库位编码"><el-input v-model="form.warehouse_location" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="品牌">
              <el-select v-model="form.brand" filterable allow-create clearable placeholder="请选择" style="width: 100%;">
                <el-option v-for="b in brandOptions" :key="b" :label="b" :value="b" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="规格型号"><el-input v-model="form.specification" placeholder="如: 5W-30 4L" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="适用车系">
              <el-select v-model="form.applicable_vehicle" filterable allow-create clearable placeholder="请选择" style="width: 100%;">
                <el-option v-for="v in vehicleOptions" :key="v" :label="v" :value="v" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">价格</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="销售价"><el-input v-model="form.selling_price" type="number" :step="0.01" /></el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">库存控制</el-divider>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="库存上限"><el-input-number v-model="form.max_stock" :min="0" style="width: 100%;" /></el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="库存下限"><el-input-number v-model="form.min_stock" :min="0" style="width: 100%;" /></el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="安全库存"><el-input-number v-model="form.safety_stock" :min="0" style="width: 100%;" /></el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="最小包装量"><el-input-number v-model="form.min_package_qty" :min="0" style="width: 100%;" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="停用标记">
              <el-switch v-model="form.discontinued" active-text="停用" inactive-text="启用" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="form.archive_remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增配件档案对话框 -->
    <el-dialog v-model="addVisible" title="新增配件档案" width="900px" top="3vh">
      <el-form :model="addForm" label-width="90px" size="default">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="配件编码" required><el-input v-model="addForm.part_no" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="配件名称" required><el-input v-model="addForm.name" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="拼音简码"><el-input v-model="addForm.pinyin_code" disabled /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="单位">
              <el-select v-model="addForm.unit" filterable allow-create placeholder="请选择" style="width: 100%;">
                <el-option v-for="u in unitOptions" :key="u" :label="u" :value="u" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="原厂编码"><el-input v-model="addForm.factory_code" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="位置码"><el-input v-model="addForm.location_code" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="库位编码"><el-input v-model="addForm.warehouse_location" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="品牌">
              <el-select v-model="addForm.brand" filterable allow-create clearable placeholder="请选择" style="width: 100%;">
                <el-option v-for="b in brandOptions" :key="b" :label="b" :value="b" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="规格型号"><el-input v-model="addForm.specification" placeholder="如: 5W-30 4L" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="适用车系">
              <el-select v-model="addForm.applicable_vehicle" filterable allow-create clearable placeholder="请选择" style="width: 100%;">
                <el-option v-for="v in vehicleOptions" :key="v" :label="v" :value="v" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">价格</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="销售价"><el-input v-model="addForm.selling_price" type="number" :step="0.01" /></el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">库存控制</el-divider>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="库存上限"><el-input-number v-model="addForm.max_stock" :min="0" style="width: 100%;" /></el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="库存下限"><el-input-number v-model="addForm.min_stock" :min="0" style="width: 100%;" /></el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="安全库存"><el-input-number v-model="addForm.safety_stock" :min="0" style="width: 100%;" /></el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="最小包装量"><el-input-number v-model="addForm.min_package_qty" :min="0" style="width: 100%;" /></el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="addForm.archive_remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="addSaving" @click="handleAdd">确认新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const keyword = ref('')
const editVisible = ref(false)
const saving = ref(false)
const addVisible = ref(false)
const addSaving = ref(false)

const vehicleOptions = [
  '海狮', '阁瑞斯', '金杯后市场', 'H2', 'SUV', 'H2S', 'F30', '金杯新快运', 'F70', 'T20',
  'X30', 'T50', 'H230', 'H330', 'H530', 'V3', 'V5', 'V6', 'V7', 'FRV',
  'FSV', 'H320', '骏捷', '尊驰', '中华', '华颂',
  '上汽大众', '一汽大众', '一汽丰田', '广汽丰田',
  '东风本田', '广汽本田', '雪佛兰', '起亚', '现代',
  '奔驰', '宝马', '奥迪', '长城', '吉利',
  '比亚迪', '长安', '奇瑞', '江淮', '东风',
  '林肯', '凯迪拉克', '沃尔沃', '马自达', '日产',
  '标致', '雪铁龙', '荣威', '福特', '新快运',
  '广汽传祺', '依维柯', '金杯油品', '三菱', 'H3',
  '福特锐界', '奔驰C200', 'BYD-V3', '别克', 'T20S',
  '金龙', '凯马', '福田', '小卡', '皮卡',
  'MPV', '凌宝', '电动屋', '新特', 'BYD-T5'
]

const unitOptions = ['个', '只', '对', '条', '套', '台', '桶', '瓶', '盒', '包', '片', '根', '支', '米', '卷', '块', '组']

const brandOptions = [
  '华晨', '金杯', '中华', '丰田', '本田', '大众', '日产', '奔驰', '宝马', '奥迪',
  '福特', '别克', '雪佛兰', '现代', '起亚', '马自达', '标致', '雪铁龙', '比亚迪',
  '长城', '吉利', '长安', '奇瑞', '江淮', '东风', '传祺', '荣威', '沃尔沃', '林肯',
  '凯迪拉克', '三菱', '依维柯', '金龙', '凯马', '福田', '通用', '博世', '电装',
  '大陆', '采埃孚', '米其林', '马牌', '普利司通', '固特异', '邓禄普', '其他'
]

const form = reactive({
  id: null, part_no: '', name: '', pinyin_code: '', unit: '', factory_code: '',
  brand: '', specification: '', location_code: '', warehouse_location: '', applicable_vehicle: '',
  network_price: 0, selling_price: 0, max_stock: 0, min_stock: 0,
  safety_stock: 0, min_package_qty: 0, discontinued: false,
  archive_remark: ''
})

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/parts/list', { params: { page: page.value, per_page: pageSize.value, keyword: keyword.value } })
    list.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

function handleEdit(row) {
  Object.assign(form, {
    id: row.id, part_no: row.part_no, name: row.name, pinyin_code: row.pinyin_code || '',
    unit: row.unit || '', factory_code: row.factory_code || '',
    brand: row.brand || '', specification: row.specification || '',
    location_code: row.location_code || '',
    warehouse_location: row.warehouse_location || '', applicable_vehicle: row.applicable_vehicle || '',
    network_price: row.network_price || 0, selling_price: row.selling_price || 0, max_stock: row.max_stock || 0,
    min_stock: row.min_stock || 0, safety_stock: row.safety_stock || 0,
    min_package_qty: row.min_package_qty || 0, discontinued: row.discontinued || false,
    archive_remark: row.archive_remark || ''
  })
  editVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await request.put(`/parts/${form.id}`, form)
    ElMessage.success('保存成功')
    editVisible.value = false
    loadData()
  } finally { saving.value = false }
}

onMounted(loadData)

const addForm = reactive({
  part_no: '', name: '', pinyin_code: '', unit: '个', factory_code: '',
  brand: '', specification: '', location_code: '', warehouse_location: '', applicable_vehicle: '',
  network_price: 0, selling_price: 0, max_stock: 0, min_stock: 0,
  safety_stock: 0, min_package_qty: 0, archive_remark: ''
})

function openAdd() {
  Object.assign(addForm, {
    part_no: '', name: '', pinyin_code: '', unit: '个', factory_code: '',
    brand: '', specification: '', location_code: '', warehouse_location: '', applicable_vehicle: '',
    network_price: 0, selling_price: 0, max_stock: 0, min_stock: 0,
    safety_stock: 0, min_package_qty: 0, archive_remark: ''
  })
  addVisible.value = true
}

async function handleAdd() {
  if (!addForm.part_no) return ElMessage.warning('请输入配件编码')
  if (!addForm.name) return ElMessage.warning('请输入配件名称')
  addSaving.value = true
  try {
    await request.post('/parts', addForm)
    ElMessage.success('配件档案创建成功')
    addVisible.value = false
    loadData()
  } finally { addSaving.value = false }
}
</script>
