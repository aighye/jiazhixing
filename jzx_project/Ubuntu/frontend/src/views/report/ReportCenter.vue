<template>
  <div>
    <div class="page-header">
      <h2>报表中心</h2>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="日报" name="daily">
        <div class="search-bar">
          <el-date-picker v-model="dailyDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" @change="loadDaily" />
          <el-button type="primary" @click="loadDaily">查询</el-button>
        </div>
        <el-row :gutter="16" v-if="dailyData">
          <el-col :span="6">
            <el-statistic title="工单总数" :value="dailyData.total_orders" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="总金额" :value="dailyData.total_amount" prefix="¥" :precision="2" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="已收金额" :value="dailyData.total_received" prefix="¥" :precision="2" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="未收金额" :value="dailyData.total_amount - dailyData.total_received" prefix="¥" :precision="2" />
          </el-col>
        </el-row>
        <el-table :data="dailyData?.items || []" stripe style="margin-top: 16px;" v-if="dailyData">
          <el-table-column prop="order_no" label="工单号" width="180" />
          <el-table-column prop="customer_name" label="客户" width="120" />
          <el-table-column prop="plate_number" label="车牌号" width="110" />
          <el-table-column prop="vehicle_model" label="品牌车型" width="130" />
          <el-table-column prop="service_type" label="维修类别" width="90" />
          <el-table-column prop="status_name" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="总金额" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.total_amount).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="received_amount" label="已收金额" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.received_amount).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="is_paid" label="付款" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_paid ? 'success' : 'danger'" size="small">{{ row.is_paid ? '已付' : '未付' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="creator_name" label="操作人" width="80" />
          <el-table-column prop="created_at" label="创建时间" width="140">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="营收报表" name="revenue">
        <div class="search-bar">
          <el-date-picker v-model="revenueRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" />
          <el-button type="primary" @click="loadRevenue">查询</el-button>
        </div>
        <el-row :gutter="16" v-if="revenueData">
          <el-col :span="8">
            <el-statistic title="总营收" :value="revenueData.total" prefix="¥" :precision="2" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="收款笔数" :value="revenueData.count" />
          </el-col>
        </el-row>
        <el-table :data="Object.entries(revenueData?.by_method || {})" stripe style="margin-top: 16px;">
          <el-table-column prop="0" label="支付方式" />
          <el-table-column prop="1" label="金额">
            <template #default="{ row }">¥{{ Number(row[1]).toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="工单报表" name="workorders">
        <div class="search-bar">
          <el-date-picker v-model="woRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" />
          <el-button type="primary" @click="loadWorkOrders">查询</el-button>
        </div>
        <el-row :gutter="16" v-if="woData">
          <el-col :span="8">
            <el-statistic title="工单总数" :value="woData.total" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="总营收" :value="woData.total_revenue" prefix="¥" :precision="2" />
          </el-col>
        </el-row>
        <el-table :data="Object.entries(woData?.by_status || {})" stripe style="margin-top: 16px;">
          <el-table-column prop="0" label="状态" />
          <el-table-column prop="1" label="数量" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="库存报表" name="inventory">
        <el-row :gutter="16" v-if="invData">
          <el-col :span="8">
            <el-statistic title="配件总数" :value="invData.total_parts" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="库存总值" :value="invData.total_value" prefix="¥" :precision="2" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="预警数量" :value="invData.low_stock_count" />
          </el-col>
        </el-row>
        <el-table :data="invData?.low_stock_parts || []" stripe style="margin-top: 16px;" v-if="invData">
          <el-table-column prop="part_no" label="编号" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="stock_quantity" label="库存" />
          <el-table-column prop="min_stock" label="最低库存" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="客户报表" name="customer">
        <el-row :gutter="16" v-if="custData">
          <el-col :span="8">
            <el-statistic title="客户总数" :value="custData.total" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="本月新增" :value="custData.new_this_month" />
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const activeTab = ref('daily')
const dailyDate = ref(null)
const dailyData = ref(null)
const revenueRange = ref(null)
const woRange = ref(null)
const revenueData = ref(null)
const woData = ref(null)
const invData = ref(null)
const custData = ref(null)

async function loadDaily() {
  const params = {}
  if (dailyDate.value) params.date = dailyDate.value
  const res = await request.get('/reports/daily', { params })
  dailyData.value = res.data
}

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }
function getStatusType(s) {
  const map = { 0: 'info', 1: 'primary', 2: 'warning', 3: 'success', 4: 'success' }
  return map[s] || 'info'
}

async function loadRevenue() {
  const params = {}
  if (revenueRange.value) { params.start_date = revenueRange.value[0]; params.end_date = revenueRange.value[1] }
  const res = await request.get('/reports/revenue', { params })
  revenueData.value = res.data
}

async function loadWorkOrders() {
  const params = {}
  if (woRange.value) { params.start_date = woRange.value[0]; params.end_date = woRange.value[1] }
  const res = await request.get('/reports/work-orders', { params })
  woData.value = res.data
}

async function loadInventory() {
  const res = await request.get('/reports/inventory')
  invData.value = res.data
}

async function loadCustomer() {
  const res = await request.get('/reports/customer')
  custData.value = res.data
}

onMounted(() => { loadDaily(); loadRevenue(); loadWorkOrders(); loadInventory(); loadCustomer() })
</script>

<style scoped>
/* Apple Design - Report Center Page Styles */

/* Table spacing */
:deep(.el-table) {
  margin-top: var(--space-lg);
}

/* Statistic row spacing */
:deep(.el-row) {
  margin-bottom: var(--space-lg);
}

/* Search bar spacing */
:deep(.search-bar) {
  margin-bottom: var(--space-lg);
}
</style>
