<template>
  <a-layout class="main-layout">
    <a-layout-sider v-model:collapsed="collapsed" :trigger="null" collapsible>
      <div class="logo">
        <h2 v-if="!collapsed">招聘监控</h2>
        <h2 v-else>JM</h2>
      </div>

      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="handleMenuClick"
      >
        <a-menu-item key="dashboard">
          <template #icon>
            <DashboardOutlined />
          </template>
          <span>仪表板</span>
        </a-menu-item>

        <a-menu-item key="monitoring-rules">
          <template #icon>
            <UnorderedListOutlined />
          </template>
          <span>监控规则</span>
        </a-menu-item>

        <a-menu-item key="scan-results">
          <template #icon>
            <FileTextOutlined />
          </template>
          <span>扫描结果</span>
        </a-menu-item>

        <a-menu-item key="jobs">
          <template #icon>
            <SearchOutlined />
          </template>
          <span>招聘搜索</span>
        </a-menu-item>

        <a-menu-item key="api-docs">
          <template #icon>
            <ApiOutlined />
          </template>
          <span>第三方数据接入</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <a-layout>
      <a-layout-header style="background: #fff; padding: 0">
        <div class="header-content">
          <menu-unfold-outlined
            v-if="collapsed"
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
          <menu-fold-outlined
            v-else
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />

          <div class="header-right">
            <a-dropdown>
              <a class="user-dropdown" @click.prevent>
                <UserOutlined />
                <span style="margin-left: 8px">{{ user?.username }}</span>
                <DownOutlined style="margin-left: 8px" />
              </a>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="logout" @click="handleLogout">
                    <LogoutOutlined />
                    退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </div>
      </a-layout-header>

      <a-layout-content class="content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  DashboardOutlined,
  UnorderedListOutlined,
  FileTextOutlined,
  SearchOutlined,
  ApiOutlined,
  UserOutlined,
  DownOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const collapsed = ref(false)
const selectedKeys = ref<string[]>(['dashboard'])

const user = computed(() => authStore.user)

watch(() => route.name, (newName) => {
  if (newName) {
    selectedKeys.value = [newName.toString().toLowerCase().replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase()]
  }
})

function handleMenuClick({ key }: { key: string }) {
  const routeMap: Record<string, string> = {
    'dashboard': 'Dashboard',
    'monitoring-rules': 'MonitoringRules',
    'scan-results': 'ScanResults',
    'jobs': 'Jobs',
    'api-docs': 'ApiDocs'
  }
  
  if (routeMap[key]) {
    router.push({ name: routeMap[key] })
  }
}

function handleLogout() {
  authStore.logout()
  message.success('已退出登录')
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.logo h2 {
  margin: 0;
  color: white;
}

.trigger {
  font-size: 18px;
  padding: 0 24px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-right: 24px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  padding: 0 12px;
  cursor: pointer;
}

.content {
  margin: 24px;
  padding: 24px;
  background: white;
  border-radius: 8px;
  min-height: 280px;
}
</style>
