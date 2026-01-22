<template>
  <div class="login-container">
    <div class="login-form">
      <div class="login-header">
        <h1>实验室设备管理系统</h1>
        <p>请登录您的账户</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form-content">
        <div class="form-group">
          <input
            v-model="form.username"
            placeholder="用户名"
            class="form-input"
            required
          />
        </div>

        <div class="form-group">
          <input
            v-model="form.password"
            type="password"
            placeholder="密码"
            class="form-input"
            required
            @keyup.enter="handleLogin"
          />
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="login-tips">
        <p>测试账户：admin / admin123</p>
        <p v-if="debugInfo" class="debug-info">{{ debugInfo }}</p>
      </div>

      <!-- 调试工具 -->
      <div class="debug-tools">
        <h4>调试工具</h4>
        <div class="debug-buttons">
          <button class="debug-btn" @click="testDirectJump">测试直接跳转</button>
          <button class="debug-btn" @click="checkAuthState">检查认证状态</button>
          <button class="debug-btn" @click="clearStorage">清除存储</button>
          <button class="debug-btn" @click="testLoginAPI">测试登录API</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/services/auth'
import { ElMessage } from 'element-plus'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const loading = ref(false)
    const debugInfo = ref('等待操作...')

    const form = reactive({
      username: 'admin',
      password: 'admin123'
    })

    const handleLogin = async () => {
      console.log('=== 开始登录 ===')
      loading.value = true
      debugInfo.value = '表单验证通过，开始调用API...'

      try {
        const response = await login(form)
        console.log('登录API响应:', response)

        if (response && response.token) {
          debugInfo.value = '登录成功，存储token和用户信息...'

          authStore.setToken(response.token)

          if (response.user) {
            authStore.setUser(response.user)
            console.log('用户信息已保存:', response.user)
          } else {
            console.warn('响应中没有用户信息')
            const defaultUser = {
              username: form.username,
              email: form.username + '@example.com',
              role: 'admin'
            }
            authStore.setUser(defaultUser)
          }

          console.log('Token已存储')
          debugInfo.value = '登录成功，准备跳转...'

          ElMessage.success('登录成功！')

          setTimeout(() => {
            router.push('/dashboard')
          }, 500)

        } else {
          throw new Error('登录响应缺少token')
        }
      } catch (error) {
        console.error('登录失败:', error)

        let errorMessage = '登录失败，请检查用户名和密码'

        if (error.response) {
          const errorData = error.response.data || {}
          errorMessage = errorData.error || errorData.message || errorMessage
        } else if (error.request) {
          errorMessage = '网络错误，请检查后端服务是否运行'
        } else {
          errorMessage = error.message || errorMessage
        }

        debugInfo.value = `错误: ${errorMessage}`
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }

    const testDirectJump = () => {
      console.log('测试直接跳转到仪表盘')
      router.push('/dashboard')
    }

    const checkAuthState = () => {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')
      debugInfo.value = `Token: ${token ? '存在' : '不存在'}, User: ${user ? '存在' : '不存在'}`
      console.log('认证状态检查:', { token, user })
      ElMessage.info('请查看控制台和调试信息')
    }

    const clearStorage = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      authStore.logoutUser()
      debugInfo.value = '本地存储已清除，认证状态已重置'
      ElMessage.success('存储已清除，请重新登录')
    }

    const testLoginAPI = async () => {
      debugInfo.value = '测试登录API...'
      loading.value = true

      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: 'admin', password: 'admin123' })
        })

        console.log('API测试响应状态:', response.status)
        const data = await response.json()
        console.log('API测试响应数据:', data)

        if (response.status === 200) {
          debugInfo.value = `API测试成功: ${JSON.stringify(data)}`
          ElMessage.success('API测试成功！')
        } else {
          debugInfo.value = `API测试失败: ${response.status} - ${JSON.stringify(data)}`
          ElMessage.error(`API测试失败: ${data.error || '未知错误'}`)
        }
      } catch (error) {
        console.error('API测试失败:', error)
        debugInfo.value = `API测试失败: ${error.message}`
        ElMessage.error('API测试失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      debugInfo,
      handleLogin,
      testDirectJump,
      checkAuthState,
      clearStorage,
      testLoginAPI
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-form {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-header {
  padding: 30px 30px 20px;
  text-align: center;
  background: linear-gradient(135deg, #304156 0%, #1f2d3d 100%);
  color: white;
}

.login-header h1 {
  margin: 0 0 10px 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.login-form-content {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #409eff;
}

.login-button {
  width: 100%;
  padding: 12px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.login-button:hover:not(:disabled) {
  background: #66b1ff;
}

.login-button:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.login-tips {
  padding: 0 30px 20px;
  text-align: center;
  border-top: 1px solid #f0f0f0;
}

.login-tips p {
  margin: 10px 0;
  color: #909399;
  font-size: 0.85rem;
}

.debug-info {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #606266;
  word-break: break-all;
  white-space: pre-wrap;
  margin-top: 10px;
}

.debug-tools {
  padding: 20px 30px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.debug-tools h4 {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 0.9rem;
  text-align: center;
}

.debug-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.debug-btn {
  padding: 8px 12px;
  background: #909399;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.3s;
}

.debug-btn:hover {
  background: #a6a9ad;
}

@media (max-width: 480px) {
  .login-container {
    padding: 10px;
  }

  .login-form {
    max-width: 100%;
  }

  .login-header {
    padding: 20px 20px 15px;
  }

  .login-form-content {
    padding: 20px;
  }

  .debug-tools {
    padding: 15px 20px;
  }

  .debug-buttons {
    flex-direction: column;
  }

  .debug-btn {
    width: 100%;
  }
}
</style>