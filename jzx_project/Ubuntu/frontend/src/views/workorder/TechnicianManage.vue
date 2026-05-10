<template>
  <div>
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>技师管理</h2>
      <div style="display: flex; gap: 8px;">
        <el-button type="success" @click="showLaborSummary = true; loadLaborSummary()">
          <el-icon><DataAnalysis /></el-icon> 工时工资汇总
        </el-button>
        <el-button type="primary" @click="openDialog(null)">新增技师</el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <el-card shadow="never" style="margin-bottom: 16px;">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="姓名/工号/电话" clearable style="width: 180px;" @clear="loadList" @keyup.enter="loadList" />
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="searchForm.level" placeholder="全部" clearable style="width: 120px;" @change="loadList">
            <el-option v-for="lv in levelOptions" :key="lv" :label="lv" :value="lv" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100px;" @change="loadList">
            <el-option label="在岗" :value="1" />
            <el-option label="离职" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 技师列表 -->
    <el-card shadow="never">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%;">
        <el-table-column prop="employee_no" label="工号" width="100" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="level" label="等级" width="80">
          <template #default="{ row }">
            <el-tag :type="levelTagType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="department" label="部门" width="100" />
        <el-table-column prop="hourly_rate" label="时薪(元/h)" width="110" align="right">
          <template #default="{ row }">
            <span style="font-weight: 500;">¥{{ Number(row.hourly_rate).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="base_salary" label="底薪(元)" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.base_salary).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="entry_date" label="入职日期" width="110" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '在岗' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="showLaborDetail(row)">工时统计</el-button>
            <el-button type="primary" size="small" link @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该技师？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" size="small" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadList"
          @current-change="loadList"
        />
      </div>
    </el-card>

    <!-- ==================== 新增/编辑技师对话框 ==================== -->
    <el-dialog v-model="showDialog" :title="form.id ? '编辑技师' : '新增技师'" width="600px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_no">
              <el-input v-model="form.employee_no" placeholder="如 TEC001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender" style="width: 100%;">
                <el-option label="男" :value="1" />
                <el-option label="女" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话">
              <el-input v-model="form.phone" placeholder="手机号码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="等级" prop="level">
              <el-select v-model="form.level" placeholder="选择等级" style="width: 100%;" allow-create filterable>
                <el-option label="高级" value="高级" />
                <el-option label="中级" value="中级" />
                <el-option label="初级" value="初级" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期">
              <el-date-picker v-model="form.entry_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="底薪(元)">
              <el-input-number v-model="form.base_salary" :min="0" :precision="2" :step="500" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时薪(元/h)">
              <el-input-number v-model="form.hourly_rate" :min="0" :precision="2" :step="10" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="部门">
              <el-input v-model="form.department" placeholder="默认：维修部" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%;">
                <el-option label="在岗" :value="1" />
                <el-option label="离职" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="身份证号">
          <el-input v-model="form.id_card" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- ==================== 个人工时统计对话框 ==================== -->
    <el-dialog v-model="showLaborDetailDialog" :title="`${laborDetailTech?.name || ''} - 工时统计`" width="900px" @open="loadPersonalStats">
      <div style="margin-bottom: 16px; display: flex; gap: 12px; align-items: center;">
        <span>统计月份：</span>
        <el-date-picker v-model="laborMonth" type="month" value-format="YYYY-MM" placeholder="选择月份" @change="loadPersonalStats" />
      </div>

      <template v-if="personalStats">
        <!-- 汇总卡片 -->
        <el-row :gutter="16" style="margin-bottom: 16px;">
          <el-col :span="4">
            <el-statistic title="总工时(h)" :value="personalStats.summary.total_hours" :precision="1" />
          </el-col>
          <el-col :span="4">
            <el-statistic title="工单数" :value="personalStats.summary.order_count" />
          </el-col>
          <el-col :span="5">
            <el-statistic title="工时产值(元)" :value="personalStats.summary.total_labor_amount" :precision="2" />
          </el-col>
          <el-col :span="5">
            <el-statistic title="底薪(元)" :value="personalStats.summary.base_salary" :precision="2" />
          </el-col>
          <el-col :span="5">
            <el-statistic title="工时工资(元)" :value="personalStats.summary.labor_wage" :precision="2" />
          </el-col>
          <el-col :span="5">
            <el-statistic title="应发工资(元)" :value="personalStats.summary.total_wage" :precision="2" value-style="color: #f56c6c; font-weight: bold;" />
          </el-col>
        </el-row>

        <!-- 工时明细 -->
        <el-table :data="personalStats.details" stripe max-height="350" size="small">
          <el-table-column prop="order_no" label="工单号" width="160" />
          <el-table-column prop="plate_number" label="车牌号" width="100" />
          <el-table-column prop="assign_type" label="角色" width="80">
            <template #default="{ row }">
              <el-tag :type="row.assign_type === 'primary' ? '' : 'info'" size="small">
                {{ row.assign_type === 'primary' ? '主修' : '副修' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="labor_hours" label="工时(h)" width="80" align="right" />
          <el-table-column prop="labor_amount" label="工时费(元)" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.labor_amount).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="status_name" label="工单状态" width="80">
            <template #default="{ row }">
              <el-tag size="small">{{ row.status_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="assigned_at" label="分配时间" min-width="140">
            <template #default="{ row }">{{ formatTime(row.assigned_at) }}</template>
          </el-table-column>
        </el-table>
      </template>

      <template #footer>
        <el-button @click="showLaborDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- ==================== 工时工资汇总对话框 ==================== -->
    <el-dialog v-model="showLaborSummary" title="技师工时工资汇总" width="1000px" @open="loadLaborSummary">
      <div style="margin-bottom: 16px; display: flex; gap: 12px; align-items: center;">
        <span>统计月份：</span>
        <el-date-picker v-model="summaryMonth" type="month" value-format="YYYY-MM" placeholder="选择月份" @change="loadLaborSummary" />
      </div>

      <template v-if="summaryData">
        <!-- 合计 -->
        <el-alert
          :title="`合计：总工时 ${summaryData.total.total_hours}h | 总工单 ${summaryData.total.total_order_count} 单 | 总工资 ¥${summaryData.total.total_wage.toFixed(2)}`"
          type="info"
          show-icon
          :closable="false"
          style="margin-bottom: 16px;"
        />

        <el-table :data="summaryData.items" stripe show-summary :summary-method="getSummaryRow">
          <el-table-column prop="name" label="技师" width="100" />
          <el-table-column prop="employee_no" label="工号" width="100" />
          <el-table-column prop="level" label="等级" width="80">
            <template #default="{ row }">
              <el-tag :type="levelTagType(row.level)" size="small">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_hours" label="总工时(h)" width="100" align="right" />
          <el-table-column prop="order_count" label="工单数" width="80" align="center" />
          <el-table-column prop="total_labor_amount" label="工时产值(元)" width="120" align="right">
            <template #default="{ row }">¥{{ Number(row.total_labor_amount).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="hourly_rate" label="时薪(元)" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.hourly_rate).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="base_salary" label="底薪(元)" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.base_salary).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="labor_wage" label="工时工资(元)" width="110" align="right">
            <template #default="{ row }">¥{{ Number(row.labor_wage).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="total_wage" label="应发工资(元)" min-width="120" align="right">
            <template #default="{ row }">
              <span style="font-weight: bold; color: #f56c6c;">¥{{ Number(row.total_wage).toFixed(2) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </template>

      <template #footer>
        <el-button @click="showLaborSummary = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

// ==================== 列表 ====================
const list = ref([])
const loading = ref(false)
const levelOptions = ref([])

const searchForm = reactive({ keyword: '', level: '', status: null })
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

async function loadList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: searchForm.keyword,
      level: searchForm.level
    }
    if (searchForm.status !== null && searchForm.status !== '') {
      params.status = searchForm.status
    }
    const res = await request.get('/technicians/list', { params })
    list.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    // handled by interceptor
  } finally { loading.value = false }
}

async function loadLevels() {
  try {
    const res = await request.get('/technicians/levels')
    levelOptions.value = res.data || []
  } catch (e) { /* ignore */ }
}

function resetSearch() {
  searchForm.keyword = ''
  searchForm.level = ''
  searchForm.status = null
  pagination.page = 1
  loadList()
}

function levelTagType(level) {
  const map = { '高级': 'danger', '中级': 'warning', '初级': 'info' }
  return map[level] || ''
}

// ==================== 新增/编辑 ====================
const showDialog = ref(false)
const saving = ref(false)
const formRef = ref(null)
const form = reactive({
  id: null,
  employee_no: '',
  name: '',
  gender: 1,
  phone: '',
  id_card: '',
  department: '维修部',
  position: '技师',
  level: '初级',
  entry_date: '',
  base_salary: 0,
  hourly_rate: 0,
  status: 1
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  level: [{ required: true, message: '请选择等级', trigger: 'change' }]
}

function openDialog(row) {
  if (row) {
    Object.assign(form, {
      id: row.id,
      employee_no: row.employee_no || '',
      name: row.name,
      gender: row.gender || 1,
      phone: row.phone || '',
      id_card: row.id_card || '',
      department: row.department || '维修部',
      position: row.position || '技师',
      level: row.level || '初级',
      entry_date: row.entry_date || '',
      base_salary: Number(row.base_salary || 0),
      hourly_rate: Number(row.hourly_rate || 0),
      status: row.status ?? 1
    })
  } else {
    resetForm()
  }
  showDialog.value = true
}

function resetForm() {
  Object.assign(form, {
    id: null,
    employee_no: '',
    name: '',
    gender: 1,
    phone: '',
    id_card: '',
    department: '维修部',
    position: '技师',
    level: '初级',
    entry_date: '',
    base_salary: 0,
    hourly_rate: 0,
    status: 1
  })
}

async function handleSave() {
  if (!form.name?.trim()) return ElMessage.warning('请输入技师姓名')

  saving.value = true
  try {
    if (form.id) {
      await request.put(`/technicians/${form.id}`, form)
      ElMessage.success('技师信息已更新')
    } else {
      await request.post('/technicians', form)
      ElMessage.success('技师创建成功')
    }
    showDialog.value = false
    loadList()
  } catch (e) {
    // handled by interceptor
  } finally { saving.value = false }
}

async function handleDelete(row) {
  try {
    await request.delete(`/technicians/${row.id}`)
    ElMessage.success('技师已删除')
    loadList()
  } catch (e) { /* handled */ }
}

// ==================== 个人工时统计 ====================
const showLaborDetailDialog = ref(false)
const laborDetailTech = ref(null)
const laborMonth = ref('')
const personalStats = ref(null)

function showLaborDetail(row) {
  laborDetailTech.value = row
  const now = new Date()
  laborMonth.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  showLaborDetailDialog.value = true
}

async function loadPersonalStats() {
  if (!laborDetailTech.value) return
  const [year, month] = (laborMonth.value || '').split('-')
  try {
    const res = await request.get(`/technicians/${laborDetailTech.value.id}/labor-stats`, {
      params: { year: Number(year), month: Number(month) }
    })
    personalStats.value = res.data
  } catch (e) { /* handled */ }
}

// ==================== 工时工资汇总 ====================
const showLaborSummary = ref(false)
const summaryMonth = ref('')
const summaryData = ref(null)

async function loadLaborSummary() {
  const [year, month] = (summaryMonth.value || '').split('-')
  if (!year || !month) {
    const now = new Date()
    summaryMonth.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  }
  const [y, m] = (summaryMonth.value || '').split('-')
  try {
    const res = await request.get('/technicians/labor-summary', {
      params: { year: Number(y), month: Number(m) }
    })
    summaryData.value = res.data
  } catch (e) { /* handled */ }
}

function getSummaryRow({ columns, data }) {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (idx === 1) { sums[idx] = ''; return }
    if (idx === 2) { sums[idx] = ''; return }
    const prop = col.property
    if (['total_hours', 'order_count', 'total_labor_amount', 'labor_wage', 'total_wage'].includes(prop)) {
      const val = data.reduce((sum, row) => sum + Number(row[prop] || 0), 0)
      sums[idx] = prop === 'order_count' ? val : val.toFixed(2)
    } else {
      sums[idx] = ''
    }
  })
  return sums
}

// ==================== 工具方法 ====================
function formatTime(t) {
  if (!t) return ''
  return t.replace('T', ' ').substring(0, 16)
}

onMounted(() => {
  loadList()
  loadLevels()
})
</script>
