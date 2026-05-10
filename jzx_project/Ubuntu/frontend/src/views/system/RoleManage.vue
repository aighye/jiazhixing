<template>
  <div>
    <div class="page-header">
      <h2>角色管理</h2>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增角色
      </el-button>
    </div>

    <el-table :data="list" stripe v-loading="loading">
      <el-table-column prop="name" label="角色名称" width="150" />
      <el-table-column prop="code" label="角色编码" width="150" />
      <el-table-column prop="description" label="描述" min-width="200" />
      <el-table-column label="权限概览" min-width="250">
        <template #default="{ row }">
          <template v-if="row.permissions && row.permissions.length > 0">
            <el-tag v-if="row.permissions.includes('*')" type="danger" size="small">全部权限</el-tag>
            <template v-else>
              <el-tag v-for="p in getModuleSummary(row.permissions)" :key="p" size="small" style="margin: 2px;">{{ p }}</el-tag>
            </template>
          </template>
          <span v-else style="color: #999;">未配置</span>
        </template>
      </el-table-column>
      <el-table-column prop="user_count" label="用户数" width="80" align="center" />
      <el-table-column label="操作" fixed="right" width="260">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="showDialog(row)">编辑</el-button>
          <el-button type="warning" link size="small" @click="showPermDialog(row)">权限</el-button>
          <el-button type="success" link size="small" @click="showUserDialog(row)">分配用户</el-button>
          <el-button type="danger" link size="small" :disabled="row.user_count > 0" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑角色对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingRole ? '编辑角色' : '新增角色'" width="500px" @close="resetForm">
      <el-form :model="form" label-width="90px">
        <el-form-item label="角色名称" required>
          <el-input v-model="form.name" placeholder="如：维修技师" />
        </el-form-item>
        <el-form-item label="角色编码" required>
          <el-input v-model="form.code" placeholder="如：technician（英文）" :disabled="!!editingRole" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 权限配置对话框 -->
    <el-dialog v-model="permDialogVisible" title="权限配置" width="680px">
      <div style="margin-bottom: 12px;">
        <span style="font-weight: bold;">角色：{{ currentRole?.name }}</span>
      </div>
      <div style="margin-bottom: 12px;">
        <el-checkbox v-model="permAll" @change="onPermAllChange">全部权限</el-checkbox>
      </div>
      <el-table :data="permissionModules" border size="small" v-if="!permAll">
        <el-table-column prop="label" label="模块" width="120" />
        <el-table-column label="权限">
          <template #default="{ row }">
            <el-checkbox-group v-model="selectedPerms">
              <el-checkbox v-for="act in row.actions" :key="act.value" :label="act.value" style="margin-right: 16px;">
                {{ act.label }}
              </el-checkbox>
            </el-checkbox-group>
          </template>
        </el-table-column>
        <el-table-column label="快捷操作" width="100" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="checkModuleAll(row)">全选</el-button>
            <el-button link size="small" @click="uncheckModuleAll(row)">清空</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="permSaving" @click="handleSavePerms">保存</el-button>
      </template>
    </el-dialog>

    <!-- 分配用户对话框 -->
    <el-dialog v-model="userDialogVisible" title="分配用户" width="700px">
      <div style="margin-bottom: 12px;">
        <span style="font-weight: bold;">角色：{{ currentRole?.name }}</span>
        <span style="color: #909399; margin-left: 12px;">已分配 {{ selectedUserIds.length }} 个用户</span>
      </div>
      <div style="display: flex; gap: 16px;">
        <div style="flex: 1;">
          <el-input v-model="userSearch" placeholder="搜索用户" clearable style="margin-bottom: 8px;" />
          <div style="max-height: 350px; overflow-y: auto; border: 1px solid #dcdfe6; border-radius: 4px;">
            <div v-for="u in filteredAvailableUsers" :key="u.id"
              style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f0f0f0;"
              @click="selectedUserIds.push(u.id)"
              :style="{ background: selectedUserIds.includes(u.id) ? '#f0f9eb' : '' }">
              {{ u.real_name }}（{{ u.username }}）
            </div>
            <div v-if="filteredAvailableUsers.length === 0" style="padding: 20px; text-align: center; color: #999;">暂无可选用户</div>
          </div>
        </div>
        <div style="flex: 1;">
          <div style="margin-bottom: 8px; font-weight: bold; color: #409eff;">已分配用户</div>
          <div style="max-height: 350px; overflow-y: auto; border: 1px solid #dcdfe6; border-radius: 4px;">
            <div v-for="uid in selectedUserIds" :key="uid"
              style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center;"
              @click="selectedUserIds = selectedUserIds.filter(id => id !== uid)">
              {{ getUserName(uid) }}
              <el-icon style="color: #f56c6c;"><Close /></el-icon>
            </div>
            <div v-if="selectedUserIds.length === 0" style="padding: 20px; text-align: center; color: #999;">暂未分配用户</div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="assigning" @click="handleAssignUsers">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

// 权限模块定义
const permissionModules = [
  { module: 'customer', label: '客户管理', actions: [
    { value: 'customer:read', label: '查看' },
    { value: 'customer:create', label: '新增' },
    { value: 'customer:update', label: '编辑' },
    { value: 'customer:delete', label: '删除' },
  ]},
  { module: 'work_order', label: '工单管理', actions: [
    { value: 'work_order:read', label: '查看工单' },
    { value: 'work_order:create', label: '创建工单' },
    { value: 'work_order:update', label: '编辑信息' },
    { value: 'work_order:status', label: '状态变更' },
    { value: 'work_order:repair', label: '维修项目' },
    { value: 'work_order:parts', label: '配件操作' },
    { value: 'work_order:settle', label: '费用结算' },
  ]},
  { module: 'parts', label: '配件管理', actions: [
    { value: 'parts:read', label: '查看' },
    { value: 'parts:create', label: '新增' },
    { value: 'parts:update', label: '编辑' },
    { value: 'parts:delete', label: '删除' },
    { value: 'parts:stock', label: '出入库' },
  ]},
  { module: 'finance', label: '财务管理', actions: [
    { value: 'finance:read', label: '查看' },
    { value: 'finance:create', label: '新增' },
    { value: 'finance:update', label: '编辑' },
    { value: 'finance:delete', label: '删除' },
  ]},
  { module: 'report', label: '报表中心', actions: [
    { value: 'report:read', label: '查看报表' },
    { value: 'report:finance', label: '财务报表' },
    { value: 'report:export', label: '导出' },
  ]},
  { module: 'system', label: '系统管理', actions: [
    { value: 'system:user', label: '用户管理' },
    { value: 'system:role', label: '角色管理' },
    { value: 'system:config', label: '系统配置' },
    { value: 'system:log', label: '操作日志' },
  ]},
]

const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingRole = ref(null)
const submitting = ref(false)
const form = ref({ name: '', code: '', description: '' })

// 权限配置相关
const permDialogVisible = ref(false)
const permAll = ref(false)
const selectedPerms = ref([])
const permSaving = ref(false)

// 分配用户相关
const userDialogVisible = ref(false)
const currentRole = ref(null)
const allUsers = ref([])
const selectedUserIds = ref([])
const assigning = ref(false)
const userSearch = ref('')

const filteredAvailableUsers = computed(() => {
  const q = userSearch.value.toLowerCase()
  return allUsers.value.filter(u => {
    if (q && !u.real_name.toLowerCase().includes(q) && !u.username.toLowerCase().includes(q)) return false
    return true
  })
})

function getUserName(uid) {
  const u = allUsers.value.find(u => u.id === uid)
  return u ? `${u.real_name}（${u.username}）` : uid
}

function formatTime(t) { return t ? t.replace('T', ' ').substring(0, 16) : '' }

// 提取模块概览（用于列表展示）
function getModuleSummary(perms) {
  if (!perms) return []
  const moduleMap = {}
  permissionModules.forEach(m => { moduleMap[m.module] = m.label })
  const modules = new Set()
  perms.forEach(p => {
    const mod = p.split(':')[0]
    if (moduleMap[mod]) modules.add(moduleMap[mod])
  })
  return [...modules]
}

// 检查模块下是否全部选中
function isModuleAll(mod) {
  return mod.actions.every(a => selectedPerms.value.includes(a.value))
}

function checkModuleAll(mod) {
  mod.actions.forEach(a => {
    if (!selectedPerms.value.includes(a.value)) selectedPerms.value.push(a.value)
  })
}

function uncheckModuleAll(mod) {
  const vals = mod.actions.map(a => a.value)
  selectedPerms.value = selectedPerms.value.filter(p => !vals.includes(p))
}

function onPermAllChange(val) {
  if (val) {
    selectedPerms.value = []
  }
}

async function loadData() {
  loading.value = true
  try {
    const res = await request.get('/system/roles')
    list.value = res.data || []
  } catch (e) { /* handled */ }
  loading.value = false
}

function showDialog(role = null) {
  editingRole.value = role
  if (role) {
    form.value = { name: role.name, code: role.code, description: role.description || '' }
  } else {
    form.value = { name: '', code: '', description: '' }
  }
  dialogVisible.value = true
}

function resetForm() {
  form.value = { name: '', code: '', description: '' }
  editingRole.value = null
}

async function handleSubmit() {
  if (!form.value.name.trim()) return ElMessage.warning('请输入角色名称')
  if (!form.value.code.trim()) return ElMessage.warning('请输入角色编码')
  submitting.value = true
  try {
    if (editingRole.value) {
      await request.put(`/system/roles/${editingRole.value.id}`, form.value)
      ElMessage.success('角色更新成功')
    } else {
      await request.post('/system/roles', form.value)
      ElMessage.success('角色创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) { /* handled */ }
  submitting.value = false
}

async function handleDelete(row) {
  try {
    await request.delete(`/system/roles/${row.id}`)
    ElMessage.success('角色删除成功')
    loadData()
  } catch (e) { /* handled */ }
}

function showPermDialog(role) {
  currentRole.value = role
  const perms = role.permissions || []
  if (perms.includes('*')) {
    permAll.value = true
    selectedPerms.value = []
  } else {
    permAll.value = false
    selectedPerms.value = [...perms]
  }
  permDialogVisible.value = true
}

async function handleSavePerms() {
  permSaving.value = true
  try {
    const perms = permAll.value ? ['*'] : selectedPerms.value
    await request.put(`/system/roles/${currentRole.value.id}`, { permissions: perms })
    ElMessage.success('权限配置保存成功')
    permDialogVisible.value = false
    loadData()
  } catch (e) { /* handled */ }
  permSaving.value = false
}

async function showUserDialog(role) {
  currentRole.value = role
  userDialogVisible.value = true
  try {
    const usersRes = await request.get('/system/users', { params: { per_page: 999 } })
    allUsers.value = (usersRes.data?.items || []).map(u => ({
      id: u.id,
      real_name: u.real_name,
      username: u.username,
      role_id: u.role_id
    }))
    const roleUsersRes = await request.get(`/system/roles/${role.id}/users`)
    selectedUserIds.value = (roleUsersRes.data || []).map(u => u.id)
  } catch (e) { /* handled */ }
}

async function handleAssignUsers() {
  assigning.value = true
  try {
    await request.post(`/system/roles/${currentRole.value.id}/users`, {
      user_ids: selectedUserIds.value
    })
    ElMessage.success('用户分配成功')
    userDialogVisible.value = false
    loadData()
  } catch (e) { /* handled */ }
  assigning.value = false
}

onMounted(() => loadData())
</script>
