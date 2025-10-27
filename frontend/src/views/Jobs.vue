<template>
  <div>
    <h1>招聘搜索</h1>

    <a-card style="margin-bottom: 16px">
      <a-form layout="inline" :model="searchForm" @finish="handleSearch">
        <a-form-item label="关键词">
          <a-input
            v-model:value="searchForm.keyword"
            placeholder="岗位名称或技能"
            style="width: 200px"
          />
        </a-form-item>

        <a-form-item label="城市">
          <a-select
            v-model:value="searchForm.city"
            placeholder="选择城市"
            style="width: 120px"
            allow-clear
          >
            <a-select-option value="北京">北京</a-select-option>
            <a-select-option value="上海">上海</a-select-option>
            <a-select-option value="深圳">深圳</a-select-option>
            <a-select-option value="杭州">杭州</a-select-option>
            <a-select-option value="广州">广州</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="薪资范围（K）">
          <a-input-number
            v-model:value="searchForm.salary_min"
            placeholder="最低"
            :min="0"
            style="width: 100px"
          />
          <span style="margin: 0 8px">-</span>
          <a-input-number
            v-model:value="searchForm.salary_max"
            placeholder="最高"
            :min="0"
            style="width: 100px"
          />
        </a-form-item>

        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading">
            <template #icon>
              <SearchOutlined />
            </template>
            搜索
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-list
      :grid="{ gutter: 16, xs: 1, sm: 2, md: 2, lg: 3, xl: 3 }"
      :data-source="jobs"
      :loading="loading"
    >
      <template #renderItem="{ item }">
        <a-list-item>
          <a-card :title="item.position" hoverable>
            <template #extra>
              <a-tag color="blue">{{ item.status }}</a-tag>
            </template>

            <p><strong>🏢 {{ item.company }}</strong></p>
            <p>💰 {{ item.salary_min }}K - {{ item.salary_max }}K</p>
            <p>📍 {{ item.location }}</p>
            <p>📅 {{ item.experience_required }}年经验 | {{ item.education_required }}</p>
            
            <div style="margin-top: 8px">
              <a-tag
                v-for="skill in item.skills.slice(0, 3)"
                :key="skill"
                color="purple"
                style="margin-bottom: 4px"
              >
                {{ skill }}
              </a-tag>
              <a-tag v-if="item.skills.length > 3" color="default">
                +{{ item.skills.length - 3 }}
              </a-tag>
            </div>

            <template #actions>
              <a-button type="link" @click="viewJobDetail(item)">查看详情</a-button>
            </template>
          </a-card>
        </a-list-item>
      </template>
    </a-list>

    <a-pagination
      v-if="pagination.total > 0"
      v-model:current="pagination.current"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      show-size-changer
      :show-total="total => `共 ${total} 条`"
      style="margin-top: 16px; text-align: center"
      @change="handlePageChange"
    />

    <!-- 详情弹窗 -->
    <a-modal
      v-model:open="detailVisible"
      :title="currentJob?.position"
      :footer="null"
      width="700px"
    >
      <div v-if="currentJob">
        <a-descriptions bordered :column="2">
          <a-descriptions-item label="公司">
            {{ currentJob.company }}
          </a-descriptions-item>
          <a-descriptions-item label="岗位">
            {{ currentJob.position }}
          </a-descriptions-item>
          <a-descriptions-item label="薪资">
            {{ currentJob.salary_min }}K - {{ currentJob.salary_max }}K
          </a-descriptions-item>
          <a-descriptions-item label="地点">
            {{ currentJob.location }}
          </a-descriptions-item>
          <a-descriptions-item label="经验要求">
            {{ currentJob.experience_required }}年
          </a-descriptions-item>
          <a-descriptions-item label="学历要求">
            {{ currentJob.education_required }}
          </a-descriptions-item>
          <a-descriptions-item label="发布时间" :span="2">
            {{ formatTime(currentJob.publish_date) }}
          </a-descriptions-item>
          <a-descriptions-item label="技能要求" :span="2">
            <a-tag v-for="skill in currentJob.skills" :key="skill" color="blue">
              {{ skill }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="岗位描述" :span="2">
            <pre style="white-space: pre-wrap; font-family: inherit">{{ currentJob.job_description }}</pre>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { message } from 'ant-design-vue'
import api from '@/api'
import { SearchOutlined } from '@ant-design/icons-vue'

const searchForm = reactive({
  keyword: '',
  city: undefined,
  salary_min: undefined,
  salary_max: undefined
})

const jobs = ref<any[]>([])
const loading = ref(false)
const pagination = ref({
  current: 1,
  pageSize: 12,
  total: 0
})

const detailVisible = ref(false)
const currentJob = ref<any>(null)

onMounted(() => {
  fetchJobs()
})

async function fetchJobs() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/jobs', {
      params: {
        page: pagination.value.current,
        per_page: pagination.value.pageSize,
        status: 'active'
      }
    })
    
    if (response.data.code === 0) {
      jobs.value = response.data.data.jobs
      pagination.value.total = response.data.data.pagination.total
    }
  } catch (error) {
    message.error('加载招聘信息失败')
  } finally {
    loading.value = false
  }
}

async function handleSearch() {
  pagination.value.current = 1
  loading.value = true
  
  try {
    const response = await api.get('/api/v1/jobs/search', {
      params: {
        keyword: searchForm.keyword,
        city: searchForm.city,
        salary_min: searchForm.salary_min || 0,
        salary_max: searchForm.salary_max || 999999
      }
    })
    
    if (response.data.code === 0) {
      jobs.value = response.data.data.jobs
      pagination.value.total = response.data.data.count
    }
  } catch (error) {
    message.error('搜索失败')
  } finally {
    loading.value = false
  }
}

function handlePageChange() {
  if (searchForm.keyword || searchForm.city || searchForm.salary_min || searchForm.salary_max) {
    handleSearch()
  } else {
    fetchJobs()
  }
}

function viewJobDetail(job: any) {
  currentJob.value = job
  detailVisible.value = true
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN')
}
</script>
