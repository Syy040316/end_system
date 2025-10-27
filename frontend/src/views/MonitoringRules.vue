<template>
  <div>
    <div style="margin-bottom: 16px; display: flex; justify-content: space-between">
      <h1>监控规则管理</h1>
      <a-button type="primary" @click="showCreateModal">
        <template #icon>
          <PlusOutlined />
        </template>
        创建规则
      </a-button>
    </div>

    <a-table
      :columns="columns"
      :data-source="rules"
      :loading="loading"
      row-key="rule_id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'keywords'">
          <a-tag v-for="keyword in record.keywords" :key="keyword" color="blue">
            {{ keyword }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'is_active'">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="testRule(record)">测试</a-button>
            <a-button size="small" @click="editRule(record)">编辑</a-button>
            <a-popconfirm
              title="确定删除这条规则吗？"
              @confirm="deleteRule(record.rule_id)"
            >
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 创建/编辑规则弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑规则' : '创建规则'"
      @ok="handleSubmit"
      @cancel="handleCancel"
      width="600px"
    >
      <a-form :model="formState" layout="vertical">
        <a-form-item label="规则名称" required>
          <a-input v-model:value="formState.rule_name" placeholder="请输入规则名称" />
        </a-form-item>

        <a-form-item label="监控关键词" required>
          <a-select
            v-model:value="formState.keywords"
            mode="tags"
            placeholder="输入关键词后按回车"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="排除关键词">
          <a-select
            v-model:value="formState.exclude_keywords"
            mode="tags"
            placeholder="输入排除关键词后按回车"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="城市过滤">
          <a-select
            v-model:value="formState.city_filter"
            mode="multiple"
            placeholder="选择城市"
            style="width: 100%"
          >
            <a-select-option value="北京">北京</a-select-option>
            <a-select-option value="上海">上海</a-select-option>
            <a-select-option value="深圳">深圳</a-select-option>
            <a-select-option value="杭州">杭州</a-select-option>
            <a-select-option value="广州">广州</a-select-option>
            <a-select-option value="成都">成都</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="薪资范围（K）">
          <a-row :gutter="8">
            <a-col :span="12">
              <a-input-number
                v-model:value="formState.salary_min"
                placeholder="最低"
                :min="0"
                style="width: 100%"
              />
            </a-col>
            <a-col :span="12">
              <a-input-number
                v-model:value="formState.salary_max"
                placeholder="最高"
                :min="0"
                style="width: 100%"
              />
            </a-col>
          </a-row>
        </a-form-item>

        <a-form-item label="通知触发方式">
          <a-select v-model:value="formState.notification_trigger">
            <a-select-option value="immediately">立即通知</a-select-option>
            <a-select-option value="hourly">每小时汇总</a-select-option>
            <a-select-option value="daily">每天汇总</a-select-option>
            <a-select-option value="when_count">达到数量时</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          v-if="formState.notification_trigger === 'when_count'"
          label="触发数量"
        >
          <a-input-number
            v-model:value="formState.notification_count"
            :min="1"
            placeholder="变化数量"
          />
        </a-form-item>

        <a-form-item label="状态">
          <a-switch v-model:checked="formState.is_active" />
          <span style="margin-left: 8px">
            {{ formState.is_active ? '启用' : '禁用' }}
          </span>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { message } from 'ant-design-vue'
import api from '@/api'
import { PlusOutlined } from '@ant-design/icons-vue'

const columns = [
  { title: '规则名称', dataIndex: 'rule_name', key: 'rule_name' },
  { title: '关键词', dataIndex: 'keywords', key: 'keywords' },
  { title: '薪资范围', key: 'salary', customRender: ({ record }: any) => {
    return `${record.salary_min || 0}K - ${record.salary_max || '不限'}K`
  }},
  { title: '状态', dataIndex: 'is_active', key: 'is_active' },
  { title: '操作', key: 'action', width: 200 }
]

const rules = ref<any[]>([])
const loading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const currentRuleId = ref<number | null>(null)

const formState = reactive({
  rule_name: '',
  keywords: [],
  exclude_keywords: [],
  city_filter: [],
  salary_min: undefined,
  salary_max: undefined,
  notification_trigger: 'immediately',
  notification_count: undefined,
  is_active: true
})

onMounted(() => {
  fetchRules()
})

async function fetchRules() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/monitoring-rules')
    if (response.data.code === 0) {
      rules.value = response.data.data.rules
    }
  } catch (error) {
    message.error('加载规则失败')
  } finally {
    loading.value = false
  }
}

function showCreateModal() {
  isEdit.value = false
  currentRuleId.value = null
  resetForm()
  modalVisible.value = true
}

function editRule(record: any) {
  isEdit.value = true
  currentRuleId.value = record.rule_id
  Object.assign(formState, {
    rule_name: record.rule_name,
    keywords: record.keywords || [],
    exclude_keywords: record.exclude_keywords || [],
    city_filter: record.city_filter || [],
    salary_min: record.salary_min,
    salary_max: record.salary_max,
    notification_trigger: record.notification_trigger,
    notification_count: record.notification_count,
    is_active: record.is_active
  })
  modalVisible.value = true
}

async function handleSubmit() {
  try {
    if (isEdit.value && currentRuleId.value) {
      await api.patch(`/api/v1/monitoring-rules/${currentRuleId.value}`, formState)
      message.success('更新成功')
    } else {
      await api.post('/api/v1/monitoring-rules', formState)
      message.success('创建成功')
    }
    
    modalVisible.value = false
    fetchRules()
  } catch (error) {
    message.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

function handleCancel() {
  modalVisible.value = false
  resetForm()
}

function resetForm() {
  Object.assign(formState, {
    rule_name: '',
    keywords: [],
    exclude_keywords: [],
    city_filter: [],
    salary_min: undefined,
    salary_max: undefined,
    notification_trigger: 'immediately',
    notification_count: undefined,
    is_active: true
  })
}

async function testRule(record: any) {
  try {
    await api.post(`/api/v1/monitoring-rules/${record.rule_id}/test`)
    message.success('测试任务已提交，请稍后查看扫描结果')
  } catch (error) {
    message.error('提交测试任务失败')
  }
}

async function deleteRule(ruleId: number) {
  try {
    await api.delete(`/api/v1/monitoring-rules/${ruleId}`)
    message.success('删除成功')
    fetchRules()
  } catch (error) {
    message.error('删除失败')
  }
}
</script>

