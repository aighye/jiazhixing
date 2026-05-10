<template>
  <div>
    <div class="page-header"><h2>系统配置</h2></div>

    <el-card v-loading="loading">
      <el-form :model="configs" label-width="120px" style="max-width: 600px;">
        <el-form-item label="店铺名称">
          <el-input v-model="configs.shop_name" />
        </el-form-item>
        <el-form-item label="店铺地址">
          <el-input v-model="configs.shop_address" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="configs.shop_phone" />
        </el-form-item>
        <el-form-item label="默认工时单价">
          <el-input v-model="configs.default_labor_rate" type="number" />
        </el-form-item>
        <el-form-item label="税率">
          <el-input v-model="configs.tax_rate" type="number" step="0.01" />
        </el-form-item>
        <el-form-item label="库存预警">
          <el-switch v-model="configs.stock_warning_enabled" active-value="true" inactive-value="false" />
        </el-form-item>
        <el-form-item label="备份保留天数">
          <el-input v-model="configs.backup_retention_days" type="number" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
          <el-button type="warning" @click="handleBackup">立即备份</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const configs = reactive({
  shop_name: '', shop_address: '', shop_phone: '',
  default_labor_rate: '200', tax_rate: '0.13',
  stock_warning_enabled: 'true', backup_retention_days: '30'
})

async function loadConfigs() {
  loading.value = true
  try {
    const res = await request.get('/system/configs')
    const list = res.data
    for (const item of list) {
      if (item.config_key in configs) {
        configs[item.config_key] = item.config_value
      }
    }
  } finally { loading.value = false }
}

async function handleSave() {
  saving.value = true
  try {
    await request.put('/system/configs', { ...configs })
    ElMessage.success('配置保存成功')
  } finally { saving.value = false }
}

async function handleBackup() {
  try {
    await request.post('/system/backup')
    ElMessage.success('备份任务已启动')
  } catch (e) {
    // handled by interceptor
  }
}

onMounted(loadConfigs)
</script>

<style scoped>
/* Apple Design - System Config Page Styles */

/* Config form max width */
:deep(.el-form) {
  max-width: 600px;
}
</style>
