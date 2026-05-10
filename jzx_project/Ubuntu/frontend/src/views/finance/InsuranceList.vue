<template>
  <div class="page-container">
    <el-card shadow="hover">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>保险公司管理</span>
          <el-button type="primary" @click="handleAdd">新增公司</el-button>
        </div>
      </template>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="code" label="公司编码" width="120">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/finance/insurances/${row.id}`)">{{ row.code || '-' }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="公司名称" min-width="150" />
        <el-table-column prop="contact_person" label="联系人" width="120" />
        <el-table-column prop="contact_phone" label="联系电话" width="130" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除此公司？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" size="small" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑公司' : '新增公司'" width="500px" @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="公司编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入公司编码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="公司名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入公司名称" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact_person" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const API = '/dict/insurances'
const list = ref([])
const loading = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref(null)
const editId = ref(null)

const form = ref({ code: '', name: '', contact_person: '', contact_phone: '', remark: '', status: 1 })
const rules = { code: [{ required: true, message: '请输入公司编码', trigger: 'blur' }], name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }] }

async function loadList() {
  loading.value = true
  try {
    const res = await request.get(API)
    list.value = res.data || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function handleAdd() {
  isEdit.value = false
  editId.value = null
  form.value = { code: '', name: '', contact_person: '', contact_phone: '', remark: '', status: 1 }
  showDialog.value = true
}

function handleEdit(row) {
  isEdit.value = true
  editId.value = row.id
  form.value = { code: row.code, name: row.name, contact_person: row.contact_person, contact_phone: row.contact_phone, remark: row.remark, status: row.status }
  showDialog.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await request.put(`${API}/${editId.value}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await request.post(API, form.value)
      ElMessage.success('添加成功')
    }
    showDialog.value = false
    loadList()
  } catch (e) { console.error(e) }
  finally { saving.value = false }
}

async function handleDelete(id) {
  try {
    await request.delete(`${API}/${id}`)
    ElMessage.success('删除成功')
    loadList()
  } catch (e) { console.error(e) }
}

function resetForm() {
  formRef.value?.resetFields()
}

onMounted(loadList)
</script>

<style scoped>
/* Apple Design - Insurance List Page Styles */

.page-container {
  padding: 0;
}

/* Card header action */
:deep(.el-card__header) {
  .card-header-action {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
