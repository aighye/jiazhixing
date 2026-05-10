<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="login-bg">
      <div class="bg-orb bg-orb--1"></div>
      <div class="bg-orb bg-orb--2"></div>
      <div class="bg-orb bg-orb--3"></div>
    </div>

    <!-- 毛玻璃登录卡片 -->
    <div class="login-card">
      <div class="login-logo">
        <el-icon :size="42" class="logo-icon"><Van /></el-icon>
        <h1>嘉之星企业管理系统</h1>
        <p class="login-subtitle">专业 · 责任 · 创新</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" prefix-icon="User" placeholder="请输入用户名" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" prefix-icon="Lock" placeholder="请输入密码"
                    type="password" show-password size="large" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(form)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0d47a1;
  position: relative;
  overflow: hidden;
}

/* 动态背景光球 */
.login-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.bg-orb--1 {
  width: 400px;
  height: 400px;
  background: #5cf0e0;
  top: -100px;
  right: -50px;
}

.bg-orb--2 {
  width: 300px;
  height: 300px;
  background: #3580e8;
  bottom: -80px;
  left: -60px;
}

.bg-orb--3 {
  width: 200px;
  height: 200px;
  background: #5cf0e0;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.2;
}

/* 毛玻璃卡片 */
.login-card {
  width: 420px;
  padding: 48px 40px 36px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(53, 128, 232, 0.25);
  position: relative;
  z-index: 1;
}

/* Logo */
.login-logo {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  color: #3580e8;
  margin-bottom: 16px;
}

.login-logo h1 {
  font-size: 22px;
  font-weight: 600;
  color: #0a1628;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 13px;
  color: #718096;
  letter-spacing: 4px;
}

/* Form */
.login-form :deep(.el-input__wrapper) {
  border-radius: 10px !important;
  background: #f0f4ff !important;
  box-shadow: none !important;
  border: 1px solid transparent !important;
  height: 44px;
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(53, 128, 232, 0.3) !important;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #3580e8 !important;
  box-shadow: 0 0 0 3px rgba(53, 128, 232, 0.1) !important;
}

.login-form :deep(.el-input__inner) {
  font-size: 14px;
  height: 44px;
}

.login-form :deep(.el-input__prefix .el-icon) {
  color: #3580e8;
  font-size: 18px;
}

.login-btn {
  width: 100%;
  height: 46px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px !important;
  background: #3580e8 !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(53, 128, 232, 0.4) !important;
  letter-spacing: 4px;
}

.login-btn:hover {
  box-shadow: 0 6px 20px rgba(53, 128, 232, 0.5) !important;
}

.login-tip {
  text-align: center;
  color: #718096;
  font-size: 12px;
  margin-top: 24px;
}

/* Responsive */
@media (max-width: 480px) {
  .login-card {
    width: 90%;
    padding: 32px 24px 28px;
  }
}
</style>
