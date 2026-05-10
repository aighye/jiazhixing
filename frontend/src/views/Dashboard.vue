<template>
  <div class="dashboard">
    <!-- Stat Cards -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon stat-icon--blue">
          <el-icon :size="22"><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">今日工单</div>
          <div class="stat-value">{{ stats.today_orders }}</div>
          <div class="stat-sub">本月累计 {{ stats.month_orders }} 单</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon--cyan">
          <el-icon :size="22"><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">今日营收</div>
          <div class="stat-value">¥{{ formatMoney(stats.today_revenue) }}</div>
          <div class="stat-sub">本月累计 ¥{{ formatMoney(stats.month_revenue) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon--green">
          <el-icon :size="22"><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">客户总数</div>
          <div class="stat-value">{{ stats.total_customers }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon--purple">
          <el-icon :size="22"><Avatar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">员工总数</div>
          <div class="stat-value">{{ stats.total_employees }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon--red">
          <el-icon :size="22"><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">库存预警</div>
          <div class="stat-value" :class="{ 'text-danger': stats.low_stock_count > 0 }">{{ stats.low_stock_count }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon--orange">
          <el-icon :size="22"><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">今日预约</div>
          <div class="stat-value">{{ stats.today_appointments }}</div>
          <div class="stat-sub">待确认 {{ stats.pending_appointments }}</div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card chart-card--main">
        <div class="chart-card__header">近7天营收趋势</div>
        <div ref="chartRef" class="chart-card__body"></div>
      </div>
      <div class="chart-card chart-card--aside">
        <div class="chart-card__header">工单状态分布</div>
        <div ref="pieChartRef" class="chart-card__body"></div>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="recent-orders">
      <div class="recent-orders__header">最近工单</div>
      <el-table :data="stats.recent_orders" stripe>
        <el-table-column prop="order_no" label="工单号" width="180" />
        <el-table-column prop="plate_number" label="车牌号" width="120" />
        <el-table-column prop="customer_name" label="客户" width="100" />
        <el-table-column prop="status_name" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">¥{{ row.total_amount }}</template>
        </el-table-column>
        <el-table-column prop="creator_name" label="操作人" width="100" align="center">
          <template #default="{ row }">{{ row.creator_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import request from '@/utils/request'
import * as echarts from 'echarts'

const stats = ref({
  today_orders: 0, today_revenue: 0, month_orders: 0, month_revenue: 0,
  total_customers: 0, total_employees: 0, low_stock_count: 0,
  daily_revenue: [], recent_orders: [], status_distribution: {}
})

const chartRef = ref(null)
const pieChartRef = ref(null)

function formatMoney(v) {
  return Number(v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatTime(t) {
  return t ? t.replace('T', ' ').substring(0, 16) : ''
}

function getStatusType(status) {
  const map = { 0: 'warning', 1: '', 2: 'success' }
  return map[status] || ''
}

onMounted(async () => {
  const res = await request.get('/dashboard/stats')
  stats.value = res.data

  await nextTick()

  // 营收趋势图
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.9)', borderColor: '#e2e8f0', textStyle: { color: '#0a1628' } },
      xAxis: {
        type: 'category', data: stats.value.daily_revenue.map(d => d.date),
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#718096', fontSize: 12 }
      },
      yAxis: {
        type: 'value',
        axisLabel: { formatter: '¥{value}', color: '#718096', fontSize: 12 },
        splitLine: { lineStyle: { color: 'rgba(53, 128, 232, 0.06)' } }
      },
      series: [{
        type: 'line', data: stats.value.daily_revenue.map(d => d.revenue),
        smooth: true,
        areaStyle: { color: 'rgba(53, 128, 232, 0.1)' },
        itemStyle: { color: '#3580e8', borderWidth: 2, borderColor: '#fff' },
        lineStyle: { color: '#3580e8', width: 3 },
        symbolSize: 8
      }],
      grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true }
    })
  }

  // 工单状态饼图
  if (pieChartRef.value) {
    const pieChart = echarts.init(pieChartRef.value)
    const statusNames = { 0: '在修', 1: '结算' }
    const dist = stats.value.status_distribution || {}
    const pieData = Object.entries(dist).map(([k, v]) => ({ name: statusNames[k] || k, value: v }))

    pieChart.setOption({
      tooltip: { trigger: 'item', backgroundColor: 'rgba(255,255,255,0.9)', borderColor: '#e2e8f0', textStyle: { color: '#0a1628' } },
      color: ['#5cf0e0', '#3580e8', '#16a34a', '#dc2626', '#d97706', '#6b7280'],
      series: [{
        type: 'pie', radius: ['45%', '72%'],
        data: pieData,
        label: { formatter: '{b}\n{c}', fontSize: 12, color: '#4a5568', lineHeight: 18 },
        emphasis: {
          itemStyle: { shadowBlur: 20, shadowOffsetX: 0, shadowColor: 'rgba(53, 128, 232, 0.3)' }
        },
        itemStyle: { borderColor: '#fff', borderWidth: 2, borderRadius: 4 }
      }]
    })
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

/* ---- Stat Cards ---- */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(53, 128, 232, 0.12);
  display: flex;
  align-items: flex-start;
  gap: 14px;
  transition: box-shadow 0.25s ease;
}

.stat-card:hover {
  box-shadow: 0 16px 48px rgba(53, 128, 232, 0.16);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon--blue { background: rgba(53, 128, 232, 0.1); color: #3580e8; }
.stat-icon--cyan { background: rgba(15, 252, 238, 0.1); color: #0ad4c4; }
.stat-icon--green { background: rgba(22, 163, 74, 0.1); color: #16a34a; }
.stat-icon--purple { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
.stat-icon--red { background: rgba(220, 38, 38, 0.1); color: #dc2626; }
.stat-icon--orange { background: rgba(217, 119, 6, 0.1); color: #d97706; }

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: #718096;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #0a1628;
  line-height: 1.2;
}

.text-danger {
  color: #dc2626 !important;
}

.stat-sub {
  font-size: 12px;
  color: #718096;
  margin-top: 4px;
}

/* ---- Charts Row ---- */
.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.chart-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(53, 128, 232, 0.12);
  overflow: hidden;
}

.chart-card__header {
  font-weight: 600;
  font-size: 15px;
  color: #0a1628;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.chart-card__body {
  height: 320px;
  padding: 16px;
}

/* ---- Recent Orders ---- */
.recent-orders {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(53, 128, 232, 0.12);
  overflow: hidden;
}

.recent-orders__header {
  font-weight: 600;
  font-size: 15px;
  color: #0a1628;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.recent-orders :deep(.el-table th.el-table__cell) {
  font-weight: 600 !important;
  font-size: 13px;
  color: #3580e8 !important;
  background: rgba(53, 128, 232, 0.04) !important;
}

/* ---- Responsive ---- */
@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
