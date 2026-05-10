<template>
  <el-container style="height: 100vh">
    <!-- 侧边栏 -->
    <el-aside :width="'220px'" class="sidebar">
      <div class="logo">
        <el-icon class="logo-icon"><Van /></el-icon>
        <span>嘉之星企业管理</span>
      </div>
      <el-menu :default-active="activeMenu" router
               background-color="transparent"
               text-color="#ffffff"
               active-text-color="#5cf0e0">
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>首页概览</span>
        </el-menu-item>

        <el-sub-menu v-if="perm('customer:read')" index="customer">
          <template #title>
            <el-icon><User /></el-icon>
            <span>客户管理</span>
          </template>
          <el-menu-item index="/customers">客户列表</el-menu-item>
          <el-menu-item index="/vehicles">车辆管理</el-menu-item>
          <el-menu-item index="/appointments">预约管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="perm('work_order:read')" index="workorder">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>维修管理</span>
          </template>
          <el-menu-item index="/work-orders?status=0">在修</el-menu-item>
          <el-menu-item index="/work-orders?status=1">结算</el-menu-item>
          <el-menu-item index="/work-orders">全部工单</el-menu-item>
          <el-menu-item index="/repair-items">维修项目管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="perm('parts:read')" index="parts">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>配件管理</span>
          </template>
          <el-menu-item index="/work-orders/parts-outbound">配件出库</el-menu-item>
          <el-menu-item index="/parts">配件库存</el-menu-item>
          <el-menu-item index="/parts/archive">配件档案</el-menu-item>
          <el-menu-item index="/parts/inbound">入库管理</el-menu-item>
          <el-menu-item index="/parts/suppliers">供应商管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="perm('finance:read')" index="finance">
          <template #title>
            <el-icon><Money /></el-icon>
            <span>财务管理</span>
          </template>
          <el-menu-item index="/finance/payments">收款管理</el-menu-item>
          <el-menu-item index="/finance/invoices">发票管理</el-menu-item>
          <el-menu-item index="/finance/manufacturers">索赔厂家管理</el-menu-item>
          <el-menu-item index="/finance/insurances">保险公司管理</el-menu-item>
        </el-sub-menu>

        <el-menu-item v-if="perm('report:read')" index="/reports">
          <el-icon><TrendCharts /></el-icon>
          <span>报表中心</span>
        </el-menu-item>

        <el-sub-menu v-if="perm('system:user') || perm('system:role') || perm('system:config') || perm('system:log')" index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item v-if="perm('system:user')" index="/system/users">用户管理</el-menu-item>
          <el-menu-item v-if="perm('system:role')" index="/system/roles">角色管理</el-menu-item>
          <el-menu-item v-if="perm('system:log')" index="/system/logs">操作日志</el-menu-item>
          <el-menu-item v-if="perm('system:config')" index="/system/config">系统配置</el-menu-item>
          <el-menu-item v-if="perm('system:config')" index="/system/business">业务设置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-header class="app-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
        </el-breadcrumb>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-trigger">
              <el-icon><UserFilled /></el-icon>
              {{ userStore.userInfo?.real_name || '用户' }}
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <!-- 修改密码对话框 -->
  <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
    <el-form :model="passwordForm" label-width="80px">
      <el-form-item label="原密码">
        <el-input v-model="passwordForm.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="passwordForm.new_password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showPasswordDialog = false">取消</el-button>
      <el-button type="primary" @click="handleChangePassword">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { changePassword } from '@/utils/auth'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const perm = (p) => userStore.hasPermission(p)

const activeMenu = computed(() => route.path)
const showPasswordDialog = ref(false)
const passwordForm = reactive({ old_password: '', new_password: '' })

onMounted(() => {
  if (!userStore.isLoggedIn) {
    userStore.fetchUserInfo()
  }
})

function handleCommand(cmd) {
  if (cmd === 'logout') {
    userStore.logout()
  } else if (cmd === 'password') {
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    showPasswordDialog.value = true
  }
}

async function handleChangePassword() {
  try {
    await changePassword(passwordForm)
    ElMessage.success('密码修改成功')
    showPasswordDialog.value = false
  } catch (e) {
    // handled by interceptor
  }
}
</script>

<style scoped>
/* === Sidebar === */
.sidebar {
  width: 220px;
  height: 100vh;
  background: #2d72d4;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar::-webkit-scrollbar {
  width: 0;
}

/* Logo */
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.logo-icon {
  font-size: 24px;
  color: #5cf0e0;
}

/* Menu */
.sidebar :deep(.el-menu) {
  background: transparent !important;
  border-right: none !important;
  padding: 6px;
  flex: 1;
}

.sidebar :deep(.el-menu-item),
.sidebar :deep(.el-sub-menu__title) {
  color: #ffffff !important;
  border-radius: 4px !important;
  margin-bottom: 2px;
  height: 42px !important;
  line-height: 42px !important;
  font-size: 15px;
  font-weight: 600;
}

.sidebar :deep(.el-menu-item:hover),
.sidebar :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
}

.sidebar :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #5cf0e0 !important;
  font-weight: 700;
  border-left: 3px solid #5cf0e0;
}

.sidebar :deep(.el-menu-item .el-icon),
.sidebar :deep(.el-sub-menu__title .el-icon) {
  font-size: 18px;
  margin-right: 10px;
}

/* Sub-menu */
.sidebar :deep(.el-sub-menu .el-menu) {
  padding-left: 12px;
}

.sidebar :deep(.el-sub-menu .el-menu .el-menu-item) {
  font-size: 14px;
  font-weight: 500;
  height: 38px !important;
  line-height: 38px !important;
}

.sidebar :deep(.el-sub-menu__icon-arrow) {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

/* === Header === */
.app-header {
  height: 56px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid rgba(53, 128, 232, 0.08);
  position: sticky;
  top: 0;
  z-index: 10;
}

/* Breadcrumb */
.app-header :deep(.el-breadcrumb) {
  font-size: 13px;
}

.app-header :deep(.el-breadcrumb__inner) {
  color: #718096 !important;
  font-weight: 400 !important;
}

.app-header :deep(.el-breadcrumb__inner.is-link) {
  color: #4a5568 !important;
  font-weight: 400 !important;
}

.app-header :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #3580e8 !important;
  font-weight: 500 !important;
}

.app-header :deep(.el-breadcrumb__separator) {
  color: #718096 !important;
}

/* User dropdown */
.header-right {
  display: flex;
  align-items: center;
}

.user-trigger {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 400;
  color: #4a5568;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.25s ease;
}

.user-trigger:hover {
  color: #3580e8;
  background: rgba(53, 128, 232, 0.06);
}

.arrow-icon {
  font-size: 12px;
}

/* === Main Content === */
.main-content {
  padding: 24px;
  background: #f0f4ff;
  min-height: calc(100vh - 56px);
}
</style>
