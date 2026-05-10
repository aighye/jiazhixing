import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, logout as logoutApi, getUserInfo } from '@/utils/auth'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const isLoggedIn = ref(false)

  async function login(credentials) {
    const res = await loginApi(credentials)
    userInfo.value = res.data.user
    isLoggedIn.value = true
    return res
  }

  async function fetchUserInfo() {
    try {
      const res = await getUserInfo()
      userInfo.value = res.data
      isLoggedIn.value = true
    } catch {
      isLoggedIn.value = false
      router.push('/login')
    }
  }

  async function logout() {
    try {
      await logoutApi()
    } finally {
      userInfo.value = null
      isLoggedIn.value = false
      router.push('/login')
    }
  }

  function hasPermission(perm) {
    if (!userInfo.value || !userInfo.value.permissions) return false
    const perms = userInfo.value.permissions
    if (perms.includes('*')) return true
    const module = perm.split(':')[0]
    if (perms.includes(`${module}:*`)) return true
    return perms.includes(perm)
  }

  return { userInfo, isLoggedIn, login, fetchUserInfo, logout, hasPermission }
})
