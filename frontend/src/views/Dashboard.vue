<template>
  <div class="dashboard">
    <h1>仪表盘</h1>
    <p>欢迎使用实验室设备管理系统！</p>

    <!-- 添加用户信息卡片 -->
    <div class="user-card" v-if="user">
      <h3>用户信息</h3>
      <div class="user-details">
        <div class="detail-item">
          <span class="label">用户名：</span>
          <span class="value">{{ user.username }}</span>
        </div>
        <div class="detail-item">
          <span class="label">邮箱：</span>
          <span class="value">{{ user.email || '未设置' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">角色：</span>
          <span class="role-tag">{{ userRoleText }}</span>
        </div>
        <div class="detail-item">
          <span class="label">用户ID：</span>
          <span class="value">{{ user.id || 'N/A' }}</span>
        </div>
      </div>
    </div>

    <!-- 系统状态 -->
    <div class="system-info">
      <h3>系统状态</h3>
      <div class="status-item">
        <span class="status-label">当前时间：</span>
        <span class="status-value">{{ currentTime }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">登录状态：</span>
        <span class="status-success">{{ authStatus }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">Token状态：</span>
        <span class="status-success">{{ tokenStatus }}</span>
      </div>
    </div>

    <!-- 统计数据 -->
    <div class="stats">
      <div class="stat-card" @click="goToDevices">
        <h3>设备总数</h3>
        <p class="stat-number">{{ stats.devicesCount }}</p>
        <p class="stat-desc">台设备</p>
      </div>

      <div class="stat-card" @click="goToReservations">
        <h3>今日预约</h3>
        <p class="stat-number">{{ stats.todayReservations }}</p>
        <p class="stat-desc">个预约</p>
      </div>

      <div class="stat-card" @click="goToReservations">
        <h3>待审批</h3>
        <p class="stat-number">{{ stats.pendingApprovals }}</p>
        <p class="stat-desc">个申请</p>
      </div>

      <div class="stat-card">
        <h3>系统运行</h3>
        <p class="stat-number">{{ uptime }}</p>
        <p class="stat-desc">天</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <button class="btn btn-primary" @click="goToDevices">设备管理</button>
      <button class="btn btn-success" @click="goToReservations">预约管理</button>
      <button class="btn btn-info" @click="refreshData">刷新数据</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

export default {
  name: 'Dashboard',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    // 响应式数据
    const currentTime = ref(new Date().toLocaleString())
    const startTime = ref(new Date())
    const uptime = ref('0.00')
    const stats = ref({
      devicesCount: 15,
      todayReservations: 8,
      pendingApprovals: 3
    })

    // 计算属性
    const user = computed(() => authStore.user)
    const authStatus = computed(() => authStore.isAuthenticated() ? '已认证' : '未认证')
    const tokenStatus = computed(() => authStore.token ? '有效' : '无效')

    // 用户角色文本
    const userRoleText = computed(() => {
      if (!user.value) return '未知'
      switch (user.value.role) {
        case 'admin': return '管理员'
        case 'teacher': return '教师'
        case 'student': return '学生'
        default: return '用户'
      }
    })

    // 定时器
    let timer

    onMounted(() => {
      console.log('Dashboard组件加载完成')
      console.log('当前用户:', user.value)
      console.log('认证状态:', authStore.isAuthenticated())
      console.log('localStorage用户:', localStorage.getItem('user'))

      // 调试：检查用户数据结构
      if (user.value) {
        console.log('用户数据结构:', JSON.stringify(user.value, null, 2))
      }

      timer = setInterval(() => {
        currentTime.value = new Date().toLocaleString()

        const now = new Date()
        const diff = now - startTime.value
        uptime.value = (diff / (1000 * 60 * 60 * 24)).toFixed(2)
      }, 1000)
    })

    onUnmounted(() => {
      if (timer) clearInterval(timer)
    })

    // 方法
    const goToDevices = () => {
      router.push('/devices')
    }

    const goToReservations = () => {
      router.push('/reservations')
    }

    const refreshData = () => {
      ElMessage.success('数据已刷新！')
      console.log('刷新数据，用户:', user.value)
    }

    return {
      currentTime,
      uptime,
      stats,
      user,
      authStatus,
      tokenStatus,
      userRoleText,
      goToDevices,
      goToReservations,
      refreshData
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

p {
  color: #666;
  margin-bottom: 20px;
}

/* 用户卡片 */
.user-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-left: 4px solid #409eff;
}

.user-card h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-item:last-child {
  border-bottom: none;
}

.label {
  width: 100px;
  color: #666;
  font-weight: 500;
}

.value {
  color: #333;
  font-weight: 500;
  flex: 1;
}

.role-tag {
  background: #409eff;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

/* 系统状态 */
.system-info {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.system-info h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.status-item {
  display: flex;
  margin: 10px 0;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  width: 100px;
  color: #666;
}

.status-value {
  color: #333;
  font-weight: bold;
}

.status-success {
  color: #52c41a;
  font-weight: bold;
}

/* 统计数据 */
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stat-card:nth-child(1) {
  border-top: 4px solid #1890ff;
}

.stat-card:nth-child(2) {
  border-top: 4px solid #52c41a;
}

.stat-card:nth-child(3) {
  border-top: 4px solid #faad14;
}

.stat-card:nth-child(4) {
  border-top: 4px solid #d9d9d9;
}

.stat-card h3 {
  margin-top: 0;
  color: #666;
  font-size: 16px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  margin: 10px 0;
  color: #333;
}

.stat-desc {
  color: #999;
  font-size: 14px;
  margin: 0;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-success {
  background: #52c41a;
  color: white;
}

.btn-success:hover {
  background: #73d13d;
}

.btn-info {
  background: #13c2c2;
  color: white;
}

.btn-info:hover {
  background: #36cfc9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .stats {
    grid-template-columns: 1fr;
  }
}
</style>