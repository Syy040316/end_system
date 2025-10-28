<template>
  <div class="api-docs">
    <h1>第三方数据接入 API 文档</h1>
    <p class="intro">本系统提供标准的RESTful API接口，支持第三方系统获取招聘数据和管理监控规则。</p>

    <a-alert
      message="认证说明"
      description="所有API请求需要在请求头中携带JWT Token进行认证。"
      type="info"
      show-icon
      style="margin-bottom: 24px"
    />

    <a-tabs v-model:activeKey="activeTab">
      <!-- 认证接口 -->
      <a-tab-pane key="auth" tab="认证接口">
        <a-card title="用户登录" style="margin-bottom: 16px">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="blue">POST</a-tag>
              <code>/api/v1/auth/login</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求参数">
              <pre>{{ JSON.stringify({
  username: "your_username",
  password: "your_password"
}, null, 2) }}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="响应示例">
              <pre>{{ JSON.stringify({
  code: 0,
  message: "登录成功",
  data: {
    user: {
      user_id: 1,
      username: "john_doe",
      email: "john@example.com"
    },
    access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    refresh_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}, null, 2) }}</pre>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="用户注册">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="blue">POST</a-tag>
              <code>/api/v1/auth/register</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求参数">
              <pre>{{ JSON.stringify({
  username: "new_user",
  email: "user@example.com",
  password: "secure_password"
}, null, 2) }}</pre>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>

      <!-- 招聘数据接口 -->
      <a-tab-pane key="jobs" tab="招聘数据">
        <a-card title="搜索招聘信息" style="margin-bottom: 16px">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="green">GET</a-tag>
              <code>/api/v1/jobs/search</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="查询参数">
              <a-table
                :columns="searchParamsColumns"
                :data-source="searchParams"
                :pagination="false"
                size="small"
              />
            </a-descriptions-item>
            <a-descriptions-item label="请求示例">
              <pre>GET /api/v1/jobs/search?keyword=Python&city=北京&salary_min=20&salary_max=40</pre>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="获取职位详情">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="green">GET</a-tag>
              <code>/api/v1/jobs/{job_id}</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="路径参数">
              <code>job_id</code>: 招聘信息的唯一标识符
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>

      <!-- 监控规则接口 -->
      <a-tab-pane key="monitoring" tab="监控规则">
        <a-card title="获取监控规则列表" style="margin-bottom: 16px">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="green">GET</a-tag>
              <code>/api/v1/monitoring-rules</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}</pre>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="创建监控规则" style="margin-bottom: 16px">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="blue">POST</a-tag>
              <code>/api/v1/monitoring-rules</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}
Content-Type: application/json</pre>
            </a-descriptions-item>
            <a-descriptions-item label="请求参数">
              <pre>{{ JSON.stringify({
  rule_name: "Python后端岗位监控",
  keywords: ["Python", "后端", "Django"],
  exclude_keywords: ["实习"],
  city_filter: ["北京", "上海"],
  salary_min: 15,
  salary_max: 30,
  notification_trigger: "immediately",
  is_active: true
}, null, 2) }}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="参数说明">
              <a-table
                :columns="ruleParamsColumns"
                :data-source="ruleParams"
                :pagination="false"
                size="small"
              />
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="测试监控规则">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="blue">POST</a-tag>
              <code>/api/v1/monitoring-rules/{rule_id}/test</code>
            </a-descriptions-item>
            <a-descriptions-item label="说明">
              手动触发一次监控规则执行，立即返回任务ID
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>

      <!-- 扫描结果接口 -->
      <a-tab-pane key="results" tab="扫描结果">
        <a-card title="获取扫描结果列表" style="margin-bottom: 16px">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="green">GET</a-tag>
              <code>/api/v1/scan-results</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="查询参数">
              <a-table
                :columns="resultParamsColumns"
                :data-source="resultParams"
                :pagination="false"
                size="small"
              />
            </a-descriptions-item>
            <a-descriptions-item label="响应示例">
              <pre>{{ JSON.stringify({
  code: 0,
  message: "success",
  data: {
    results: [
      {
        result_id: 1,
        rule_id: 1,
        scan_time: "2024-01-01T12:00:00",
        jobs_new: [/* 新增招聘列表 */],
        jobs_updated: [/* 更新招聘列表 */],
        jobs_deleted: [/* 下架招聘列表 */],
        email_sent: true,
        total_changes: 10
      }
    ],
    pagination: {
      page: 1,
      per_page: 20,
      total: 50
    }
  }
}, null, 2) }}</pre>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="获取统计信息">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="green">GET</a-tag>
              <code>/api/v1/scan-results/stats</code>
            </a-descriptions-item>
            <a-descriptions-item label="说明">
              获取最近扫描的统计数据（新增、更新、下架数量）
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>

      <!-- 代码示例 -->
      <a-tab-pane key="examples" tab="调用示例">
        <a-card title="Python 调用示例" style="margin-bottom: 16px">
          <pre><code>import requests

# 基础配置
BASE_URL = "http://localhost:5000"
username = "your_username"
password = "your_password"

# 1. 登录获取Token
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={"username": username, "password": password}
)
access_token = login_response.json()["data"]["access_token"]

# 2. 设置认证头
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# 3. 搜索招聘信息
search_response = requests.get(
    f"{BASE_URL}/api/v1/jobs/search",
    headers=headers,
    params={
        "keyword": "Python",
        "city": "北京",
        "salary_min": 20,
        "salary_max": 40
    }
)
jobs = search_response.json()["data"]["jobs"]
print(f"找到 {len(jobs)} 个职位")

# 4. 创建监控规则
rule_response = requests.post(
    f"{BASE_URL}/api/v1/monitoring-rules",
    headers=headers,
    json={
        "rule_name": "Python岗位监控",
        "keywords": ["Python", "Django"],
        "city_filter": ["北京"],
        "salary_min": 20,
        "salary_max": 40,
        "notification_trigger": "immediately",
        "is_active": True
    }
)
rule_id = rule_response.json()["data"]["rule_id"]
print(f"创建规则成功，ID: {rule_id}")

# 5. 获取扫描结果
results_response = requests.get(
    f"{BASE_URL}/api/v1/scan-results",
    headers=headers,
    params={"rule_id": rule_id, "page": 1, "per_page": 10}
)
results = results_response.json()["data"]["results"]
print(f"找到 {len(results)} 条扫描结果")</code></pre>
        </a-card>

        <a-card title="JavaScript 调用示例">
          <pre><code>// 基础配置
const BASE_URL = 'http://localhost:5000';

// 1. 登录获取Token
const login = async (username, password) => {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  return data.data.access_token;
};

// 2. 搜索招聘信息
const searchJobs = async (token, keyword, city) => {
  const params = new URLSearchParams({ keyword, city });
  const response = await fetch(
    `${BASE_URL}/api/v1/jobs/search?${params}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  const data = await response.json();
  return data.data.jobs;
};

// 3. 创建监控规则
const createRule = async (token, ruleData) => {
  const response = await fetch(`${BASE_URL}/api/v1/monitoring-rules`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(ruleData)
  });
  return await response.json();
};

// 使用示例
(async () => {
  const token = await login('your_username', 'your_password');
  const jobs = await searchJobs(token, 'Python', '北京');
  console.log(`找到 ${jobs.length} 个职位`);
  
  const rule = await createRule(token, {
    rule_name: 'Python岗位监控',
    keywords: ['Python', 'Django'],
    city_filter: ['北京'],
    salary_min: 20,
    salary_max: 40,
    notification_trigger: 'immediately',
    is_active: true
  });
  console.log('创建规则成功:', rule);
})();</code></pre>
        </a-card>
      </a-tab-pane>
    </a-tabs>

    <a-card title="错误码说明" style="margin-top: 24px">
      <a-table
        :columns="errorCodeColumns"
        :data-source="errorCodes"
        :pagination="false"
      />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('auth')

// 搜索参数
const searchParamsColumns = [
  { title: '参数名', dataIndex: 'name', key: 'name' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '必填', dataIndex: 'required', key: 'required' },
  { title: '说明', dataIndex: 'desc', key: 'desc' }
]

const searchParams = [
  { name: 'keyword', type: 'string', required: '否', desc: '岗位名称或技能关键词' },
  { name: 'skills', type: 'string', required: '否', desc: '技能列表，逗号分隔' },
  { name: 'city', type: 'string', required: '否', desc: '城市' },
  { name: 'salary_min', type: 'integer', required: '否', desc: '最低薪资（K）' },
  { name: 'salary_max', type: 'integer', required: '否', desc: '最高薪资（K）' }
]

// 监控规则参数
const ruleParamsColumns = searchParamsColumns
const ruleParams = [
  { name: 'rule_name', type: 'string', required: '是', desc: '规则名称' },
  { name: 'keywords', type: 'array', required: '是', desc: '监控关键词列表' },
  { name: 'exclude_keywords', type: 'array', required: '否', desc: '排除关键词列表' },
  { name: 'city_filter', type: 'array', required: '否', desc: '城市过滤列表' },
  { name: 'salary_min', type: 'integer', required: '否', desc: '最低薪资（K）' },
  { name: 'salary_max', type: 'integer', required: '否', desc: '最高薪资（K）' },
  { name: 'notification_trigger', type: 'string', required: '否', desc: '通知触发方式：immediately/hourly/daily/when_count' },
  { name: 'notification_count', type: 'integer', required: '否', desc: '触发数量（when_count时必填）' },
  { name: 'is_active', type: 'boolean', required: '否', desc: '是否启用，默认true' }
]

// 扫描结果参数
const resultParamsColumns = searchParamsColumns
const resultParams = [
  { name: 'page', type: 'integer', required: '否', desc: '页码，默认1' },
  { name: 'per_page', type: 'integer', required: '否', desc: '每页数量，默认20' },
  { name: 'rule_id', type: 'integer', required: '否', desc: '按规则ID过滤' }
]

// 错误码
const errorCodeColumns = [
  { title: '错误码', dataIndex: 'code', key: 'code' },
  { title: '说明', dataIndex: 'desc', key: 'desc' }
]

const errorCodes = [
  { code: 0, desc: '成功' },
  { code: 400, desc: '参数错误' },
  { code: 401, desc: '未认证或Token过期' },
  { code: 403, desc: '无权限访问' },
  { code: 404, desc: '资源不存在' },
  { code: 409, desc: '资源冲突（如用户名已存在）' },
  { code: 500, desc: '服务器内部错误' }
]
</script>

<style scoped>
.api-docs {
  max-width: 1200px;
  margin: 0 auto;
}

.intro {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 13px;
}

code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

pre code {
  background: none;
  padding: 0;
}
</style>
