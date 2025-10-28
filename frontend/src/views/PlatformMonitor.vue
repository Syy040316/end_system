<template>
  <div>
    <h1>模拟平台数据监控</h1>
    <p class="subtitle">实时查看模拟招聘平台的数据变化情况</p>

    <!-- 平台统计 -->
    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="招聘总数"
            :value="platformStats.total"
            suffix="条"
          />
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card>
          <a-statistic
            title="活跃招聘"
            :value="platformStats.active"
            :value-style="{ color: '#3f8600' }"
            suffix="条"
          />
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card>
          <a-statistic
            title="已下架"
            :value="platformStats.deleted"
            :value-style="{ color: '#cf1322' }"
            suffix="条"
          />
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card>
          <a-statistic
            title="平均薪资"
            :value="platformStats.avg_salary"
            suffix="K"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- 刷新按钮 -->
    <a-space style="margin-bottom: 16px">
      <a-button type="primary" @click="fetchPlatformData" :loading="loading">
        <template #icon>
          <ReloadOutlined />
        </template>
        刷新数据
      </a-button>
      
      <a-button @click="fetchUpdates">
        <template #icon>
          <ClockCircleOutlined />
        </template>
        获取最近更新
      </a-button>
    </a-space>

    <!-- 城市和公司分布 -->
    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="12">
        <a-card title="城市分布">
          <a-tag
            v-for="city in platformStats.cities"
            :key="city"
            color="blue"
            style="margin: 4px"
          >
            {{ city }}
          </a-tag>
        </a-card>
      </a-col>

      <a-col :span="12">
        <a-card title="公司列表（前10）">
          <a-tag
            v-for="company in platformStats.companies?.slice(0, 10)"
            :key="company"
            color="purple"
            style="margin: 4px"
          >
            {{ company }}
          </a-tag>
        </a-card>
      </a-col>
    </a-row>

    <!-- 最近更新的招聘信息 -->
    <a-card title="最近更新的招聘" v-if="recentUpdates.length > 0">
      <a-list
        :data-source="recentUpdates"
        :pagination="{ pageSize: 10 }"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #title>
                <a-space>
                  <a-tag color="green" v-if="isNew(item)">NEW</a-tag>
                  <a-tag color="orange" v-else>UPDATE</a-tag>
                  {{ item.company }} | {{ item.position }}
                </a-space>
              </template>
              <template #description>
                <p>💰 薪资: {{ item.salary_min }}K - {{ item.salary_max }}K</p>
                <p>📍 地点: {{ item.location }} | 🕐 更新: {{ formatTime(item.update_date) }}</p>
                <p>🛠 技能: {{ item.skills.join(', ') }}</p>
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import {
  ReloadOutlined,
  ClockCircleOutlined
} from '@ant-design/icons-vue'

const MOCK_PLATFORM_URL = 'http://localhost:5001'

const loading = ref(false)
const platformStats = ref({
  total: 0,
  active: 0,
  inactive: 0,
  deleted: 0,
  cities: [],
  companies: [],
  avg_salary: 0
})

const recentUpdates = ref<any[]>([])
const lastUpdateTime = ref<Date>(new Date(Date.now() - 3600000)) // 1小时前

onMounted(() => {
  fetchPlatformData()
})

async function fetchPlatformData() {
  loading.value = true
  try {
    const response = await axios.get(`${MOCK_PLATFORM_URL}/api/v1/stats`)
    if (response.data.code === 0) {
      platformStats.value = response.data.data
    }
  } catch (error) {
    message.error('获取平台统计数据失败')
  } finally {
    loading.value = false
  }
}

async function fetchUpdates() {
  try {
    const sinceTime = lastUpdateTime.value.toISOString()
    const response = await axios.get(`${MOCK_PLATFORM_URL}/api/v1/jobs/updates`, {
      params: { since: sinceTime }
    })
    
    if (response.data.code === 0) {
      const updates = response.data.data
      recentUpdates.value = [...updates.updated, ...updates.deleted]
      message.success(`找到 ${recentUpdates.value.length} 条更新`)
      lastUpdateTime.value = new Date()
    }
  } catch (error) {
    message.error('获取更新数据失败')
  }
}

function isNew(job: any) {
  const updateTime = new Date(job.update_date)
  const publishTime = new Date(job.publish_date)
  // 如果更新时间和发布时间相同，说明是新增
  return Math.abs(updateTime.getTime() - publishTime.getTime()) < 1000
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN')
}
</script>

<style scoped>
.subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
}
</style>

