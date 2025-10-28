# 系统架构图 (Mermaid 格式)

> 在支持Mermaid的环境中（GitHub、Typora、VS Code等）可以看到图形化显示

## 1️⃣ 整体架构图

```mermaid
graph TB
    subgraph "用户端"
        User[👤 用户/第三方平台]
        Browser[🌐 浏览器]
    end

    subgraph "前端层 :8080"
        Frontend[🎨 Vue 3 Frontend<br/>- 仪表板<br/>- 监控规则<br/>- 扫描结果<br/>- 平台监控<br/>- API文档]
    end

    subgraph "后端层 :5000"
        Backend[⚙️ Flask Backend<br/>- 用户认证 JWT<br/>- 监控规则管理<br/>- 任务调度<br/>- 推送API<br/>- 邮件通知]
    end

    subgraph "任务队列层"
        Beat[⏰ Celery Beat<br/>定时调度器<br/>每小时触发]
        Worker[🔄 Celery Worker<br/>异步任务执行器<br/>- 监控任务<br/>- 邮件任务]
    end

    subgraph "数据层"
        Redis[(🔴 Redis :6379<br/>消息队列 + 缓存)]
        Postgres[(🐘 PostgreSQL :5432<br/>主数据库<br/>- users<br/>- rules<br/>- jobs<br/>- results)]
    end

    subgraph "外部服务"
        Mock[🏢 Mock Platform :5001<br/>模拟招聘平台<br/>动态数据生成]
        Mail[📧 邮件服务<br/>SMTP]
    end

    User --> Browser
    Browser -->|HTTP :8080| Frontend
    User -->|API :5000| Backend
    
    Frontend -->|REST API| Backend
    Backend --> Redis
    Backend --> Postgres
    Backend --> Mail
    
    Beat --> Redis
    Worker --> Redis
    Worker --> Postgres
    Worker --> Mock
    Worker --> Mail
    
    Backend -.触发任务.-> Worker

    style Frontend fill:#42b983
    style Backend fill:#409eff
    style Beat fill:#f56c6c
    style Worker fill:#e6a23c
    style Redis fill:#ff6b6b
    style Postgres fill:#4dabf7
    style Mock fill:#69db7c
    style Mail fill:#ffd93d
```

## 2️⃣ 数据流向图

```mermaid
sequenceDiagram
    participant U as 👤 用户
    participant F as 🎨 Frontend
    participant B as ⚙️ Backend
    participant DB as 🐘 Database
    participant Q as 🔴 Redis Queue
    participant W as 🔄 Worker
    participant M as 🏢 Mock Platform
    participant E as 📧 邮件服务

    Note over U,E: 用户创建监控规则
    U->>F: 填写监控条件
    F->>B: POST /api/v1/monitoring-rules
    B->>DB: 保存规则
    DB-->>B: 成功
    B-->>F: 规则已创建
    F-->>U: 显示成功

    Note over U,E: 自动监控执行
    activate W
    Note right of W: Celery Beat 定时触发
    W->>DB: 获取活跃规则
    DB-->>W: 返回规则列表
    W->>M: 爬取招聘数据
    M-->>W: 返回职位数据
    W->>DB: 获取上次结果
    DB-->>W: 上次数据
    W->>W: 比对数据变化
    
    alt 发现变化
        W->>DB: 保存扫描结果
        W->>E: 发送邮件通知
        E-->>U: 📧 邮件通知
    else 无变化
        W->>DB: 记录无变化
    end
    deactivate W
```

## 3️⃣ 第三方推送流程

```mermaid
sequenceDiagram
    participant T as 🏢 第三方平台
    participant B as ⚙️ Backend
    participant DB as 🐘 Database
    participant W as 🔄 Worker
    participant U as 👤 用户

    Note over T,U: 认证流程
    T->>B: POST /api/v1/auth/login
    B->>DB: 验证用户
    DB-->>B: 用户信息
    B-->>T: 返回 JWT Token

    Note over T,U: 推送职位数据
    T->>B: POST /api/v1/jobs/push<br/>(携带Token)
    B->>B: 验证Token
    B->>DB: 检查job_id是否存在
    
    alt 职位已存在
        DB-->>B: 已存在
        B->>DB: 更新职位
    else 新职位
        DB-->>B: 不存在
        B->>DB: 创建职位
    end
    
    DB-->>B: 保存成功
    B->>W: 触发监控检查
    
    W->>DB: 查询匹配的规则
    alt 有匹配规则
        W->>U: 📧 发送邮件通知
    end
    
    B-->>T: 推送成功
```

## 4️⃣ 技术栈架构

```mermaid
graph LR
    subgraph "前端技术栈"
        A1[Vue 3]
        A2[TypeScript]
        A3[Ant Design Vue]
        A4[Pinia]
        A5[Vue Router]
        A6[Axios]
    end

    subgraph "后端技术栈"
        B1[Flask]
        B2[SQLAlchemy]
        B3[Alembic]
        B4[Flask-JWT]
        B5[Flask-Mail]
        B6[Celery]
        B7[Flasgger]
    end

    subgraph "数据存储"
        C1[PostgreSQL 15]
        C2[Redis]
    end

    subgraph "部署运维"
        D1[Docker]
        D2[Docker Compose]
        D3[Nginx]
    end

    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> A5
    A5 --> A6

    B1 --> B2
    B2 --> B3
    B3 --> B4
    B4 --> B5
    B5 --> B6
    B6 --> B7

    style A1 fill:#42b983
    style B1 fill:#409eff
    style C1 fill:#4dabf7
    style D1 fill:#2496ed
```

## 5️⃣ Docker容器架构

```mermaid
graph TB
    subgraph "Docker Network: default"
        subgraph "Web服务"
            F[🎨 frontend<br/>nginx:alpine<br/>:8080]
            B[⚙️ backend<br/>python:3.9<br/>:5000]
            M[🏢 mock_platform<br/>python:3.9<br/>:5001]
        end

        subgraph "任务服务"
            W[🔄 celery_worker<br/>python:3.9]
            CB[⏰ celery_beat<br/>python:3.9]
        end

        subgraph "数据服务"
            P[(🐘 postgres<br/>postgres:15<br/>:5432)]
            R[(🔴 redis<br/>redis:alpine<br/>:6379)]
        end

        subgraph "持久化存储"
            PV[📦 postgres_data<br/>Volume]
        end
    end

    F -.-> B
    B --> P
    B --> R
    W --> R
    W --> P
    CB --> R
    P --> PV

    style F fill:#42b983
    style B fill:#409eff
    style M fill:#69db7c
    style W fill:#e6a23c
    style CB fill:#f56c6c
    style P fill:#4dabf7
    style R fill:#ff6b6b
    style PV fill:#95a5a6
```

## 6️⃣ 监控任务执行流程

```mermaid
flowchart TD
    Start([⏰ Celery Beat 定时触发<br/>每小时一次]) --> GetRules[📋 获取所有活跃监控规则]
    GetRules --> CheckRules{有活跃规则?}
    
    CheckRules -->|否| End([结束])
    CheckRules -->|是| LoopRules[🔄 遍历每个规则]
    
    LoopRules --> BuildQuery[🔧 构建搜索条件<br/>关键词/城市/薪资]
    BuildQuery --> FetchData[🌐 调用模拟平台API<br/>获取招聘数据]
    FetchData --> GetLastResult[📂 从数据库获取<br/>上次扫描结果]
    GetLastResult --> CompareData[⚖️ 比对数据变化<br/>新增/更新/下架]
    
    CompareData --> HasChange{发现变化?}
    
    HasChange -->|否| LogNoChange[📝 记录无变化]
    LogNoChange --> NextRule{还有规则?}
    
    HasChange -->|是| SaveResult[💾 保存扫描结果]
    SaveResult --> CheckNotify{满足通知条件?}
    
    CheckNotify -->|否| JustSave[只保存结果]
    JustSave --> NextRule
    
    CheckNotify -->|是| SendEmail[📧 发送异步邮件任务]
    SendEmail --> MarkSent[✅ 标记已发送邮件]
    MarkSent --> NextRule
    
    NextRule -->|是| LoopRules
    NextRule -->|否| End

    style Start fill:#f56c6c
    style GetRules fill:#409eff
    style FetchData fill:#69db7c
    style CompareData fill:#e6a23c
    style SendEmail fill:#ffd93d
    style End fill:#95a5a6
```

## 7️⃣ 数据库ER图

```mermaid
erDiagram
    users ||--o{ monitoring_rules : "创建"
    users ||--o{ scan_results : "拥有"
    monitoring_rules ||--o{ scan_results : "产生"

    users {
        int user_id PK
        string username UK
        string email UK
        string password_hash
        datetime created_at
        datetime updated_at
    }

    monitoring_rules {
        int rule_id PK
        int user_id FK
        string rule_name
        json keywords
        json exclude_keywords
        json city_filter
        int salary_min
        int salary_max
        string notification_trigger
        int notification_count
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    jobs {
        string job_id PK
        string company
        string position
        text description
        text requirements
        json skills
        string location
        int salary_min
        int salary_max
        string status
        datetime publish_date
        datetime update_date
    }

    scan_results {
        int result_id PK
        int rule_id FK
        json jobs_new
        json jobs_updated
        json jobs_deleted
        boolean email_sent
        datetime scan_time
    }
```

## 8️⃣ API路由架构

```mermaid
graph LR
    API[/api/v1/] --> Auth[/auth]
    API --> Rules[/monitoring-rules]
    API --> Results[/scan-results]
    API --> Jobs[/jobs]
    API --> Push[/jobs/push]

    Auth --> Login[POST /login<br/>用户登录]
    Auth --> Register[POST /register<br/>用户注册]
    Auth --> Refresh[POST /refresh<br/>刷新Token]
    Auth --> Current[GET /current<br/>当前用户]

    Rules --> GetRules[GET /<br/>获取规则列表]
    Rules --> CreateRule[POST /<br/>创建规则]
    Rules --> GetRule[GET /:id<br/>获取单个规则]
    Rules --> UpdateRule[PUT /:id<br/>更新规则]
    Rules --> DeleteRule[DELETE /:id<br/>删除规则]
    Rules --> TestRule[POST /:id/test<br/>测试规则]

    Results --> GetResults[GET /<br/>获取结果列表]
    Results --> GetResult[GET /:id<br/>获取单个结果]
    Results --> Stats[GET /stats<br/>统计信息]

    Jobs --> SearchJobs[GET /search<br/>搜索职位]
    Jobs --> GetJobs[GET /<br/>获取职位列表]
    Jobs --> GetJob[GET /:id<br/>获取职位详情]

    Push --> PushOne[POST /<br/>推送单个职位]
    Push --> PushBatch[POST /batch<br/>批量推送]
    Push --> UpdateJob[PUT /:id<br/>更新职位]
    Push --> DeleteJob[DELETE /:id<br/>下架职位]

    style API fill:#409eff
    style Auth fill:#67c23a
    style Rules fill:#e6a23c
    style Results fill:#f56c6c
    style Jobs fill:#909399
    style Push fill:#42b983
```

## 📊 查看建议

### GitHub / GitLab
- 直接在仓库中查看此Markdown文件，Mermaid图表会自动渲染

### VS Code
- 安装插件：`Markdown Preview Mermaid Support`
- 使用快捷键 `Ctrl+Shift+V` 预览

### Typora / Obsidian
- 原生支持Mermaid语法

### 在线工具
- https://mermaid.live/ - 在线Mermaid编辑器
- 复制代码块到在线编辑器查看

---

**提示：** 如果图表未显示，请使用支持Mermaid的Markdown查看器

