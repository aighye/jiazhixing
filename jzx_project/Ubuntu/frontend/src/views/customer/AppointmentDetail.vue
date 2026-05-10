<template>
  <div v-loading="loading">
    <div class="page-header">
      <h2>预约详情</h2>
      <el-button @click="goBack">返回</el-button>
    </div>

    <el-card shadow="hover">
      <template #header>基本信息</template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="预约编号">{{ apt.appointment_no }}</el-descriptions-item>
        <el-descriptions-item label="客户姓名">{{ apt.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="车牌号">{{ apt.plate_number }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ apt.phone }}</el-descriptions-item>
        <el-descriptions-item label="预约日期">{{ apt.appointment_date }}</el-descriptions-item>
        <el-descriptions-item label="预约时间">{{ apt.appointment_time }}</el-descriptions-item>
        <el-descriptions-item label="服务类型">{{ apt.service_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="['info', '', 'success', 'danger'][apt.status]">
            {{ ['待确认', '已确认', '已完成', '已取消'][apt.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(apt.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ apt.creator_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="问题描述" :span="3">{{ apt.description || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="3">{{ apt.remark || '暂无' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <div class="action-buttons">
      <el-button v-if="apt.status === 0" type="success" @click="handleConfirm">确认预约</el-button>
      <el-button v-if="apt.status === 0" type="warning" @click="handleCancel">取消预约</el-button>
      <el-button v-if="apt.status === 1" type="primary" @click="handleToWorkOrder">转为工单</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

function goBack() {
  router.back()
}
const loading = ref(false)
const apt = ref({})

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

async function loadData() {
  loading.value = true
  try {
    const res = await request.get(`/customers/appointments/${route.params.id}`)
    apt.value = res.data
  } finally { loading.value = false }
}

async function handleConfirm() {
  await request.put(`/customers/appointments/${apt.value.id}/confirm`)
  ElMessage.success('已确认')
  loadData()
}

async function handleCancel() {
  const { value } = await ElMessageBox.prompt('请输入取消原因', '取消预约', {
    confirmButtonText: '确定取消',
    cancelButtonText: '返回',
    inputType: 'textarea',
    inputPlaceholder: '请输入取消预约说明',
    inputValidator: (v) => v && v.trim() ? true : '请填写取消原因'
  })
  await request.put(`/customers/appointments/${apt.value.id}/cancel`, { remark: value })
  ElMessage.success('已取消')
  loadData()
}

async function handleToWorkOrder() {
  await ElMessageBox.confirm('确定将此预约转为工单？', '转工单', { type: 'info' })
  const res = await request.post(`/customers/appointments/${apt.value.id}/to-work-order`)
  ElMessage.success('已转为工单')
  router.push(`/work-orders/${res.data.id}`)
}

onMounted(loadData)
</script>

<style scoped>
/* Apple Design - Appointment Detail Page Styles */

/* Card spacing */
:deep(.el-card) {
  margin-bottom: var(--space-lg);
}

/* Action buttons */
.action-buttons {
  display: flex;
  gap: var(--space-sm);
}
</style>
