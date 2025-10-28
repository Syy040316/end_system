<template>
  <div class="api-docs">
    <h1>第三方数据接入 API 文档</h1>
    <p class="intro">本系统提供标准的RESTful API接口，供第三方招聘平台推送职位数据到本系统。</p>

    <a-alert
      message="认证说明"
      description="所有API请求需要在请求头中携带JWT Token进行认证。请先联系系统管理员获取API账号。"
      type="info"
      show-icon
      style="margin-bottom: 24px"
    />

    <a-tabs v-model:activeKey="activeTab">
      <!-- 认证接口 -->
      <a-tab-pane key="auth" tab="1. 获取访问令牌">
        <a-card title="获取访问令牌 (Access Token)">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="blue">POST</a-tag>
              <code>/api/v1/auth/login</code>
            </a-descriptions-item>
            <a-descriptions-item label="说明">
              使用系统分配的API账号获取访问令牌，令牌有效期为24小时
            </a-descriptions-item>
            <a-descriptions-item label="请求参数">
              <pre>{{ JSON.stringify({
  username: "api_partner_name",
  password: "your_api_password"
}, null, 2) }}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="响应示例">
              <pre>{{ JSON.stringify({
  code: 0,
  message: "登录成功",
  data: {
    access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    refresh_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    expires_in: 86400
  }
}, null, 2) }}</pre>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>

      <!-- 推送招聘数据 -->
      <a-tab-pane key="push-job" tab="2. 推送职位数据">
        <a-card title="推送单个职位" style="margin-bottom: 16px">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="blue">POST</a-tag>
              <code>/api/v1/jobs/push</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}
Content-Type: application/json</pre>
            </a-descriptions-item>
            <a-descriptions-item label="请求参数">
              <pre>{{ JSON.stringify({
  job_id: "unique_job_id_from_your_platform",
  company: "公司名称",
  position: "职位名称",
  description: "职位描述",
  requirements: "任职要求",
  skills: ["Python", "Django", "Redis"],
  location: "北京",
  salary_min: 25,
  salary_max: 35,
  status: "active",
  publish_date: "2024-01-01T00:00:00Z",
  update_date: "2024-01-01T00:00:00Z"
}, null, 2) }}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="参数说明">
              <a-table
                :columns="pushJobParamsColumns"
                :data-source="pushJobParams"
                :pagination="false"
                size="small"
              />
            </a-descriptions-item>
            <a-descriptions-item label="响应示例">
              <pre>{{ JSON.stringify({
  code: 0,
  message: "职位推送成功",
  data: {
    job_id: "unique_job_id_from_your_platform",
    created: true
  }
}, null, 2) }}</pre>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="批量推送职位">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="blue">POST</a-tag>
              <code>/api/v1/jobs/push/batch</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}
Content-Type: application/json</pre>
            </a-descriptions-item>
            <a-descriptions-item label="请求参数">
              <pre>{{ JSON.stringify({
  jobs: [
    {
      job_id: "job_001",
      company: "字节跳动",
      position: "Python开发工程师",
      skills: ["Python", "Django"],
      location: "北京",
      salary_min: 25,
      salary_max: 35,
      status: "active"
    },
    {
      job_id: "job_002",
      company: "阿里巴巴",
      position: "Java开发工程师",
      skills: ["Java", "Spring"],
      location: "杭州",
      salary_min: 30,
      salary_max: 40,
      status: "active"
    }
  ]
}, null, 2) }}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="说明">
              单次批量推送最多支持100个职位
            </a-descriptions-item>
            <a-descriptions-item label="响应示例">
              <pre>{{ JSON.stringify({
  code: 0,
  message: "批量推送完成",
  data: {
    success_count: 2,
    failed_count: 0,
    total: 2
  }
}, null, 2) }}</pre>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>

      <!-- 更新和下架 -->
      <a-tab-pane key="update-job" tab="3. 更新/下架职位">
        <a-card title="更新职位信息" style="margin-bottom: 16px">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="orange">PUT</a-tag>
              <code>/api/v1/jobs/push/{'{job_id}'}</code>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}
Content-Type: application/json</pre>
            </a-descriptions-item>
            <a-descriptions-item label="路径参数">
              <code>job_id</code>: 职位的唯一标识符（来自您平台的ID）
            </a-descriptions-item>
            <a-descriptions-item label="请求参数">
              <pre>{{ JSON.stringify({
  salary_min: 30,
  salary_max: 40,
  update_date: "2024-01-02T00:00:00Z"
}, null, 2) }}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="说明">
              只需要提供需要更新的字段，系统会自动触发监控并通知相关用户
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="下架职位">
          <a-descriptions bordered :column="1">
            <a-descriptions-item label="接口地址">
              <a-tag color="red">DELETE</a-tag>
              <code>/api/v1/jobs/push/{'{job_id}'}</code>
            </a-descriptions-item>
            <a-descriptions-item label="或使用">
              <a-tag color="orange">PUT</a-tag>
              <code>/api/v1/jobs/push/{'{job_id}'}</code>
              <pre>{{ JSON.stringify({ status: "inactive" }, null, 2) }}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="请求头">
              <pre>Authorization: Bearer {access_token}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="说明">
              下架后的职位会被标记为inactive状态，系统会通知相关监控用户
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-tab-pane>

      <!-- 代码示例 -->
      <a-tab-pane key="examples" tab="4. 调用示例">
        <a-card title="Python 调用示例" style="margin-bottom: 16px">
          <pre><code>import requests
from datetime import datetime

# 基础配置
BASE_URL = "http://your-domain.com"
API_USERNAME = "api_partner_name"
API_PASSWORD = "your_api_password"

# 1. 获取访问令牌
def get_access_token():
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": API_USERNAME, "password": API_PASSWORD}
    )
    data = response.json()
    if data['code'] == 0:
        return data['data']['access_token']
    raise Exception(f"登录失败: {data['message']}")

# 2. 推送单个职位
def push_job(token, job_data):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/jobs/push",
        headers=headers,
        json=job_data
    )
    return response.json()

# 3. 批量推送职位
def batch_push_jobs(token, jobs_list):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/jobs/push/batch",
        headers=headers,
        json={"jobs": jobs_list}
    )
    return response.json()

# 4. 更新职位
def update_job(token, job_id, updates):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/jobs/push/{job_id}",
        headers=headers,
        json=updates
    )
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 获取令牌
    token = get_access_token()
    print("✓ 令牌获取成功")
    
    # 推送单个职位
    job = {
        "job_id": "job_12345",
        "company": "示例科技有限公司",
        "position": "Python开发工程师",
        "description": "负责后端开发",
        "skills": ["Python", "Django", "PostgreSQL"],
        "location": "北京",
        "salary_min": 25,
        "salary_max": 35,
        "status": "active",
        "publish_date": datetime.now().isoformat(),
        "update_date": datetime.now().isoformat()
    }
    
    result = push_job(token, job)
    print(f"✓ 职位推送结果: {result['message']}")
    
    # 批量推送
    jobs = [job, {...}]  # 多个职位
    batch_result = batch_push_jobs(token, jobs)
    print(f"✓ 批量推送: {batch_result['data']}")
    
    # 更新职位
    update_result = update_job(token, "job_12345", {
        "salary_min": 30,
        "salary_max": 40
    })
    print(f"✓ 更新结果: {update_result['message']}")</code></pre>
        </a-card>

        <a-card title="JavaScript/Node.js 调用示例">
          <pre><code>const axios = require('axios');

// 基础配置
const BASE_URL = 'http://your-domain.com';
const API_USERNAME = 'api_partner_name';
const API_PASSWORD = 'your_api_password';

// 1. 获取访问令牌
async function getAccessToken() {
  const response = await axios.post(`${BASE_URL}/api/v1/auth/login`, {
    username: API_USERNAME,
    password: API_PASSWORD
  });
  
  if (response.data.code === 0) {
    return response.data.data.access_token;
  }
  throw new Error(`登录失败: ${response.data.message}`);
}

// 2. 推送单个职位
async function pushJob(token, jobData) {
  const response = await axios.post(
    `${BASE_URL}/api/v1/jobs/push`,
    jobData,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}

// 3. 批量推送职位
async function batchPushJobs(token, jobsList) {
  const response = await axios.post(
    `${BASE_URL}/api/v1/jobs/push/batch`,
    { jobs: jobsList },
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}

// 4. 更新职位
async function updateJob(token, jobId, updates) {
  const response = await axios.put(
    `${BASE_URL}/api/v1/jobs/push/${jobId}`,
    updates,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}

// 使用示例
(async () => {
  try {
    // 获取令牌
    const token = await getAccessToken();
    console.log('✓ 令牌获取成功');
    
    // 推送职位
    const job = {
      job_id: 'job_12345',
      company: '示例科技有限公司',
      position: 'Python开发工程师',
      description: '负责后端开发',
      skills: ['Python', 'Django', 'PostgreSQL'],
      location: '北京',
      salary_min: 25,
      salary_max: 35,
      status: 'active',
      publish_date: new Date().toISOString(),
      update_date: new Date().toISOString()
    };
    
    const result = await pushJob(token, job);
    console.log('✓ 职位推送成功:', result.message);
    
    // 批量推送
    const jobs = [job, {...}];  // 多个职位
    const batchResult = await batchPushJobs(token, jobs);
    console.log('✓ 批量推送完成:', batchResult.data);
    
    // 更新职位
    const updateResult = await updateJob(token, 'job_12345', {
      salary_min: 30,
      salary_max: 40
    });
    console.log('✓ 更新成功:', updateResult.message);
    
  } catch (error) {
    console.error('错误:', error.message);
  }
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

    <a-card title="注意事项" style="margin-top: 16px">
      <ul>
        <li>访问令牌(Access Token)有效期为24小时，过期后需要重新获取</li>
        <li>job_id必须是您平台的唯一标识符，用于去重和更新</li>
        <li>薪资单位为K（千元/月），如25表示25000元/月</li>
        <li>批量推送单次最多100条，建议每次50条以内</li>
        <li>推送成功后，系统会自动触发相关监控规则并通知用户</li>
        <li>建议使用增量推送，只推送新增或更新的职位</li>
        <li>如有问题请联系系统管理员</li>
      </ul>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('auth')

// 推送职位参数
const pushJobParamsColumns = [
  { title: '参数名', dataIndex: 'name', key: 'name' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '必填', dataIndex: 'required', key: 'required' },
  { title: '说明', dataIndex: 'desc', key: 'desc' }
]

const pushJobParams = [
  { name: 'job_id', type: 'string', required: '是', desc: '职位唯一标识（来自您的平台）' },
  { name: 'company', type: 'string', required: '是', desc: '公司名称' },
  { name: 'position', type: 'string', required: '是', desc: '职位名称' },
  { name: 'description', type: 'string', required: '否', desc: '职位描述' },
  { name: 'requirements', type: 'string', required: '否', desc: '任职要求' },
  { name: 'skills', type: 'array', required: '是', desc: '技能列表，如["Python", "Django"]' },
  { name: 'location', type: 'string', required: '是', desc: '工作地点城市' },
  { name: 'salary_min', type: 'integer', required: '是', desc: '最低薪资（K，千元/月）' },
  { name: 'salary_max', type: 'integer', required: '是', desc: '最高薪资（K，千元/月）' },
  { name: 'status', type: 'string', required: '否', desc: 'active或inactive，默认active' },
  { name: 'publish_date', type: 'string', required: '否', desc: '发布时间，ISO 8601格式' },
  { name: 'update_date', type: 'string', required: '否', desc: '更新时间，ISO 8601格式' }
]

// 错误码
const errorCodeColumns = [
  { title: '错误码', dataIndex: 'code', key: 'code' },
  { title: '说明', dataIndex: 'desc', key: 'desc' }
]

const errorCodes = [
  { code: 0, desc: '成功' },
  { code: 400, desc: '参数错误（缺少必填字段或格式不正确）' },
  { code: 401, desc: '未认证或Token过期' },
  { code: 403, desc: '无权限访问（Token无效）' },
  { code: 409, desc: '资源冲突（job_id已存在且不可覆盖）' },
  { code: 429, desc: '请求过于频繁，请稍后重试' },
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

ul {
  padding-left: 20px;
}

ul li {
  margin: 8px 0;
  color: #666;
}
</style>
