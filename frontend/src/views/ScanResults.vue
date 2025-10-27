<template>
  <div>
    <h1>扫描结果</h1>

    <a-table
      :columns="columns"
      :data-source="results"
      :loading="loading"
      :pagination="pagination"
      row-key="result_id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'scan_time'">
          {{ formatTime(record.scan_time) }}
        </template>

        <template v-else-if="column.key === 'changes'">
          <a-space>
            <a-tag color="green" v-if="record.jobs_new.length > 0">
              新增: {{ record.jobs_new.length }}
            </a-tag>
            <a-tag color="orange" v-if="record.jobs_updated.length > 0">
              更新: {{ record.jobs_updated.length }}
            </a-tag>
            <a-tag color="red" v-if="record.jobs_deleted.length > 0">
              下架: {{ record.jobs_deleted.length }}
            </a-tag>
          </a-space>
        </template>

        <template v-else-if="column.key === 'email_sent'">
          <a-tag :color="record.email_sent ? 'green' : 'gray'">
            {{ record.email_sent ? '已发送' : '未发送' }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'action'">
          <a-button size="small" @click="viewDetail(record)">查看详情</a-button>
        </template>
      </template>
    </a-table>

    <!-- 详情弹窗 -->
    <a-modal
      v-model:open="detailVisible"
      title="扫描结果详情"
      :footer="null"
      width="900px"
    >
      <div v-if="currentResult">
        <a-tabs>
          <a-tab-pane key="new" :tab="`新增 (${currentResult.jobs_new.length})`">
            <a-list
              :data-source="currentResult.jobs_new"
              :locale="{ emptyText: '暂无新增' }"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      <a-tag color="green">NEW</a-tag>
                      {{ item.company }} | {{ item.position }}
                    </template>
                    <template #description>
                      <p>💰 薪资: {{ item.salary_min }}K - {{ item.salary_max }}K</p>
                      <p>📍 地点: {{ item.location }}</p>
                      <p>🛠 技能: {{ item.skills.join(', ') }}</p>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-tab-pane>

          <a-tab-pane key="updated" :tab="`更新 (${currentResult.jobs_updated.length})`">
            <a-list
              :data-source="currentResult.jobs_updated"
              :locale="{ emptyText: '暂无更新' }"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      <a-tag color="orange">UPDATED</a-tag>
                      {{ item.company }} | {{ item.position }}
                    </template>
                    <template #description>
                      <p>💰 薪资: {{ item.salary_min }}K - {{ item.salary_max }}K</p>
                      <p>📍 地点: {{ item.location }}</p>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-tab-pane>

          <a-tab-pane key="deleted" :tab="`下架 (${currentResult.jobs_deleted.length})`">
            <a-list
              :data-source="currentResult.jobs_deleted"
              :locale="{ emptyText: '暂无下架' }"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      <a-tag color="red">DELETED</a-tag>
                      {{ item.company }} | {{ item.position }}
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-tab-pane>
        </a-tabs>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import api from '@/api'

const columns = [
  { title: '扫描时间', dataIndex: 'scan_time', key: 'scan_time' },
  { title: '规则ID', dataIndex: 'rule_id', key: 'rule_id' },
  { title: '变化统计', key: 'changes' },
  { title: '邮件状态', dataIndex: 'email_sent', key: 'email_sent' },
  { title: '操作', key: 'action', width: 120 }
]

const results = ref<any[]>([])
const loading = ref(false)
const pagination = ref({
  current: 1,
  pageSize: 20,
  total: 0
})

const detailVisible = ref(false)
const currentResult = ref<any>(null)

onMounted(() => {
  fetchResults()
})

async function fetchResults() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/scan-results', {
      params: {
        page: pagination.value.current,
        per_page: pagination.value.pageSize
      }
    })
    
    if (response.data.code === 0) {
      results.value = response.data.data.results
      pagination.value.total = response.data.data.pagination.total
    }
  } catch (error) {
    message.error('加载扫描结果失败')
  } finally {
    loading.value = false
  }
}

function handleTableChange(pag: any) {
  pagination.value.current = pag.current
  pagination.value.pageSize = pag.pageSize
  fetchResults()
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN')
}

function viewDetail(record: any) {
  currentResult.value = record
  detailVisible.value = true
}
</script>

