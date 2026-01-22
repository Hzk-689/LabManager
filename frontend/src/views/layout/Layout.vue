<template>
  <div class="layout">
    <header class="header">
      <div class="header-left">
        <h1>实验室设备管理系统</h1>
        <nav class="nav-menu">
          <router-link to="/dashboard" class="nav-item">仪表盘</router-link>
          <router-link to="/devices" class="nav-item">设备管理</router-link>
          <router-link to="/reservations" class="nav-item">预约管理</router-link>
        </nav>
      </div>

      <div class="header-right" v-if="authStore.user">
        <span class="user-info">
          <span class="user-name">{{ authStore.user.username }}</span>
          <button class="logout-btn" @click="handleLogout">退出</button>
        </span>
      </div>
      <div class="header-right" v-else>
        <router-link to="/login" class="login-btn">登录</router-link>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox, ElMessage } from 'element-plus'

export default {
  name: 'Layout',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const handleLogout = async () => {
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        authStore.logoutUser()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // 用户取消
      }
    }

    return {
      authStore,
      handleLogout
    }
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #304156;
  color: white;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.header-left h1 {
  font-size: 1.3rem;
  font-weight: bold;
  margin: 0;
}

.nav-menu {
  display: flex;
  gap: 20px;
}

.nav-item {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
}

.nav-item:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.router-link-active {
  color: #ffd04b;
  background: rgba(255, 255, 255, 0.1);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  color: white;
  font-weight: 500;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 0.9rem;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.login-btn {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: white;
}

.main-content {
  flex: 1;
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>