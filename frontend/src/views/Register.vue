<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h1>招聘信息监控系统</h1>
        <p>创建新账户</p>
      </div>

      <a-form
        :model="formState"
        :rules="rules"
        @finish="handleRegister"
        layout="vertical"
      >
        <a-form-item label="用户名" name="username">
          <a-input
            v-model:value="formState.username"
            size="large"
            placeholder="请输入用户名"
          />
        </a-form-item>

        <a-form-item label="邮箱" name="email">
          <a-input
            v-model:value="formState.email"
            size="large"
            type="email"
            placeholder="请输入邮箱"
          />
        </a-form-item>

        <a-form-item label="密码" name="password">
          <a-input-password
            v-model:value="formState.password"
            size="large"
            placeholder="请输入密码"
          />
        </a-form-item>

        <a-form-item label="确认密码" name="confirmPassword">
          <a-input-password
            v-model:value="formState.confirmPassword"
            size="large"
            placeholder="请再次输入密码"
          />
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            block
          >
            注册
          </a-button>
        </a-form-item>

        <div class="login-link">
          已有账号？
          <router-link to="/login">立即登录</router-link>
        </div>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formState = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePass2 = async (_rule: any, value: string) => {
  if (value === '') {
    return Promise.reject('请再次输入密码')
  } else if (value !== formState.password) {
    return Promise.reject('两次输入的密码不一致')
  } else {
    return Promise.resolve()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符' }
  ],
  email: [
    { required: true, message: '请输入邮箱' },
    { type: 'email', message: '请输入有效的邮箱地址' }
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码长度至少6个字符' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码' },
    { validator: validatePass2, trigger: 'change' }
  ]
}

const loading = ref(false)

async function handleRegister() {
  loading.value = true
  try {
    const success = await authStore.register(
      formState.username,
      formState.email,
      formState.password
    )
    
    if (success) {
      message.success('注册成功，请登录')
      router.push({ name: 'Login' })
    } else {
      message.error('注册失败')
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h1 {
  font-size: 24px;
  margin: 0 0 10px 0;
  color: #333;
}

.register-header p {
  color: #999;
  margin: 0;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #999;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
