# 招聘信息监控系统

基于爬虫的招聘信息监控系统 - 完整实现（第一、二阶段）

## 系统架构

```
├── backend/                 # 主后端服务
│   ├── app/                # 应用核心
│   ├── migrations/         # 数据库迁移
│   ├── tests/              # 测试
│   └── requirements.txt    # Python依赖
├── mock_platform/          # 模拟招聘平台
│   ├── app/
│   └── requirements.txt
├── frontend/               # Vue前端
│   ├── src/
│   └── package.json
└── docker-compose.yml      # Docker编排

```

## 技术栈

### 后端
- **框架**: Flask + Flask-RESTful
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **任务队列**: Celery + Redis
- **认证**: JWT (Flask-JWT-Extended)
- **ORM**: SQLAlchemy
- **数据库迁移**: Alembic

### 前端
- **框架**: Vue 3 + TypeScript
- **UI库**: Ant Design Vue 4
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 模拟招聘平台
- **框架**: Flask
- **数据生成**: Faker

## 快速开始

### 使用Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务地址：
- 前端: http://localhost:5173
- 主后端API: http://localhost:5000
- 模拟招聘平台: http://localhost:5001
- API文档: http://localhost:5000/api/docs

### 本地开发

#### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 数据库迁移
flask db upgrade

# 启动后端
flask run --port=5000

# 启动Celery Worker（新终端）
celery -A app.celery worker -l info

# 启动Celery Beat（新终端）
celery -A app.celery beat -l info
```

#### 模拟招聘平台

```bash
cd mock_platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run --port=5001
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 核心功能

### 第一阶段（MVP）
- ✅ 用户注册/登录（JWT认证）
- ✅ 监控规则管理（创建、查询、更新、删除）
- ✅ 模拟招聘平台（500+数据、定时更新）
- ✅ 定时监控任务（Celery Beat）
- ✅ 邮件通知系统
- ✅ 基础前端界面

### 第二阶段
- ✅ 高级搜索和过滤
- ✅ 变化详情展示（新增、更新、下架）
- ✅ API文档（Swagger UI）
- ✅ 缓存优化（Redis）
- ✅ 数据库索引优化

## API文档

启动后端后访问: http://localhost:5000/api/docs

主要API端点：

### 用户认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新Token

### 监控规则
- `GET /api/v1/monitoring-rules` - 获取所有规则
- `POST /api/v1/monitoring-rules` - 创建规则
- `GET /api/v1/monitoring-rules/{id}` - 获取规则详情
- `PATCH /api/v1/monitoring-rules/{id}` - 更新规则
- `DELETE /api/v1/monitoring-rules/{id}` - 删除规则
- `POST /api/v1/monitoring-rules/{id}/test` - 测试规则

### 扫描结果
- `GET /api/v1/scan-results` - 获取扫描结果
- `GET /api/v1/scan-results/{id}` - 获取结果详情

### 招聘信息
- `GET /api/v1/jobs` - 获取招聘列表
- `GET /api/v1/jobs/{id}` - 获取招聘详情
- `GET /api/v1/jobs/search` - 搜索招聘

## 数据库设计

主要表结构：
- `users` - 用户表
- `monitoring_rules` - 监控规则表
- `scan_results` - 扫描结果表
- `jobs` - 招聘信息表
- `job_versions` - 招聘变化历史表
- `user_preferences` - 用户邮件偏好表

## 监控任务流程

1. Celery Beat 定时触发监控任务
2. 对每个用户的监控规则：
   - 调用模拟平台API获取最新招聘
   - 与上次结果对比，检测变化
   - 记录新增、更新、下架的招聘
3. 根据用户邮件偏好触发邮件通知
4. 保存扫描结果到数据库

## 环境变量配置

### 后端 (.env)
```
DATABASE_URL=postgresql://admin:password@localhost:5432/job_monitor
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
