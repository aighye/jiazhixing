import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      if (res.code === 401) {
        router.push('/login')
      }
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  error => {
    if (error.response && error.response.status === 401) {
      router.push('/login')
    }
    // 优先从响应体中提取错误消息
    let msg = '网络错误'
    if (error.response) {
      const data = error.response.data
      if (data && typeof data === 'object') {
        msg = data.message || data.error || data.msg || `服务器错误 (${error.response.status})`
      } else {
        msg = `服务器错误 (${error.response.status})`
      }
    } else if (error.code === 'ECONNABORTED') {
      msg = '请求超时，请稍后重试'
    } else if (error.message) {
      msg = error.message
    }
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default request
