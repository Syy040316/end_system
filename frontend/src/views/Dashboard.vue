<template>
  <div>
    <h1>仪表板</h1>
    
    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6">
        <a-card hoverable @click="goToRules" style="cursor: pointer">
          <a-statistic
            title="监控规则总数"
            :value="stats.totalRules"
            :prefix="h(UnorderedListOutlined)"
          />
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card hoverable @click="goToResults" style="cursor: pointer">
          <a-statistic
            title="新增招聘"
            :value="stats.totalNewJobs"
            :value-style="{ color: '#3f8600' }"
            :prefix="h(ArrowUpOutlined)"
          />
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card hoverable @click="goToResults" style="cursor: pointer">
          <a-statistic
            title="更新招聘"
            :value="stats.totalUpdatedJobs"
            :value-style="{ color: '#cf1322' }"
            :prefix="h(SyncOutlined)"
          />
        </a-card>
      </a-col>

      <a-col :span="6">
        <a-card hoverable @click="goToResults" style="cursor: pointer">
          <a-statistic
            title="下架招聘"
            :value="stats.totalDeletedJobs"
            :prefix="h(MinusCircleOutlined)"
          />
        </a-card>
      </a-col>
    </a-row>

    <a-card title="最近扫描结果" style="margin-bottom: 24px">
      <a-timeline v-if="recentResults.length > 0">
        <a-timeline-item
          v-for="result in recentResults"
          :key="result.result_id"
          :color="result.total_changes > 0 ? 'green' : 'gray'"
        >
          <p>
            <strong>{{ formatTime(result.scan_time) }}</strong>
            - 规则 #{{ result.rule_id }}
          </p>
          <p>
            新增: {{ result.jobs_new.length }} |
            更新: {{ result.jobs_updated.length }} |
            下架: {{ result.jobs_deleted.length }}
          </p>
        </a-timeline-item>
      </a-timeline>
      <a-empty v-else description="暂无扫描结果" />
    </a-card>

    <a-button type="primary" size="large" @click="goToCreateRule">
      <template #icon>
        <PlusOutlined />
      </template>
      创建新监控规则
    </a-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import api from '@/api'
import {
  UnorderedListOutlined,
  ArrowUpOutlined,
  SyncOutlined,
  MinusCircleOutlined,
  PlusOutlined
} from '@ant-design/icons-vue'

const router = useRouter()

const stats = ref({
  totalRules: 0,
  totalNewJobs: 0,
  totalUpdatedJobs: 0,
  totalDeletedJobs: 0
})

const recentResults = ref<any[]>([])

onMounted(() => {
  fetchDashboardData()
})

async function fetchDashboardData() {
  try {
    // 获取监控规则统计
    const rulesRes = await api.get('/api/v1/monitoring-rules')
    if (rulesRes.data.code === 0) {
      stats.value.totalRules = rulesRes.data.data.count
    }

    // 获取扫描结果统计
    const scanRes = await api.get('/api/v1/scan-results/stats')
    if (scanRes.data.code === 0) {
      stats.value.totalNewJobs = scanRes.data.data.total_new_jobs
      stats.value.totalUpdatedJobs = scanRes.data.data.total_updated_jobs
      stats.value.totalDeletedJobs = scanRes.data.data.total_deleted_jobs
    }

    // 获取最近扫描结果
    const resultsRes = await api.get('/api/v1/scan-results', {
      params: { per_page: 10 }
    })
    if (resultsRes.data.code === 0) {
      recentResults.value = resultsRes.data.data.results
    }
  } catch (error) {
    message.error('加载数据失败')
  }
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN')
}

function goToCreateRule() {
  router.push({ name: 'MonitoringRules' })
}

function goToRules() {
  router.push({ name: 'MonitoringRules' })
}

function goToResults() {
  router.push({ name: 'ScanResults' })
}
</script>
