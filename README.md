# 招聘信息监控系统

基于爬虫技术的智能招聘信息监控平台，支持自定义规则监控、邮件通知和第三方数据接入。

## ✨ 主要功能

- 🔍 **智能监控** - 自定义关键词、城市、薪资范围等筛选条件
- 📧 **邮件通知** - 新增/更新/下架招聘信息实时通知
- 📊 **数据可视化** - 直观的仪表板展示监控统计
- 🔌 **API接入** - 第三方招聘平台可推送数据到系统
- 📡 **平台监控** - 实时查看模拟招聘平台数据变化
- 🔄 **自动化任务** - 基于Celery的定时监控和异步处理

## 🏗️ 技术栈

### 后端
- **Flask** - Python Web框架
- **PostgreSQL** - 关系型数据库
- **Redis** - 缓存和消息队列
- **Celery** - 分布式任务队列
- **SQLAlchemy** - ORM
- **JWT** - 身份认证

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全
- **Ant Design Vue** - UI组件库
- **Axios** - HTTP客户端

### 部署
- **Docker** - 容器化
- **Docker Compose** - 服务编排

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Python 3.9+ (用于测试脚本，可选)

### Ubuntu环境部署

#### 1. 克隆项目

```bash
git clone https://github.com/Syy040316/end_system.git
cd end_system
```

#### 2. 赋予脚本执行权限

```bash
chmod +x *.sh
```

#### 3. 启动系统

**方法A：使用交互式菜单（推荐新手）**

```bash
./快速启动.sh
```

选择选项 1 进行首次安装。

**方法B：直接启动（熟悉命令行）**

```bash
./rebuild_all.sh
```

#### 4. 等待服务启动

大约需要30秒。你可以查看日志：

```bash
docker-compose logs -f
```

#### 5. 访问系统

- **前端界面**: http://localhost:8080 或 http://your-server-ip:8080
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/apidocs
- **模拟平台**: http://localhost:5001

#### 6. 创建账号

访问前端界面，点击"注册"创建账号，或使用快速启动脚本：

```bash
./快速启动.sh
# 选择选项 9 创建管理员账号
```

## 📚 文档

- **[Ubuntu使用指南.md](Ubuntu使用指南.md)** - 所有可用脚本和命令
- **[Ubuntu部署完整指南.md](Ubuntu部署完整指南.md)** - 从零开始的详细部署教程
- **[更新说明.md](更新说明.md)** - 新功能说明和使用指南

## 🔧 常用脚本

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `快速启动.sh` | 交互式管理工具 | 日常管理（推荐） |
| `rebuild_all.sh` | 完整重建 | 首次部署、重大更新 |
| `check_monitoring.sh` | 监控诊断 | 检查系统是否正常工作 |
| `backup.sh` | 数据备份 | 定期备份 |
| `update.sh` | 从Git更新 | 拉取最新代码并部署 |

## 📖 使用示例

### 1. 创建监控规则

登录系统后：

1. 点击"监控规则"
2. 点击"创建规则"
3. 填写规则信息：
   - 规则名称：如"Python后端岗位"
   - 关键词：Python, Django, Flask
   - 城市：北京, 上海
   - 薪资范围：20-40K
4. 保存并激活

### 2. 查看监控结果

- 点击"扫描结果"查看所有监控记录
- 点击"仪表板"的统计卡片快速跳转
- 在"平台数据监控"查看模拟平台数据变化

### 3. 第三方平台推送数据

查看"第三方数据接入"页面的完整API文档和示例代码。

简单示例：

```python
import requests

# 1. 登录获取Token
resp = requests.post("http://your-server:5000/api/v1/auth/login",
    json={"username": "your_user", "password": "your_pass"})
token = resp.json()["data"]["access_token"]

# 2. 推送职位
requests.post("http://your-server:5000/api/v1/jobs/push",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "job_id": "unique_job_001",
        "company": "示例公司",
        "position": "Python工程师",
        "skills": ["Python", "Django"],
        "location": "北京",
        "salary_min": 25,
        "salary_max": 35
    })
```

## 🛠️ 常见问题

### Q: 服务启动失败怎么办？

```bash
# 查看日志
docker-compose logs

# 完全重建
./rebuild_all.sh
```

### Q: 监控没有发现新职位？

```bash
# 运行诊断工具
./check_monitoring.sh
```

检查：
1. 是否创建了监控规则？
2. 规则是否已激活？
3. 筛选条件是否太严格？

### Q: 如何备份数据？

```bash
./backup.sh
```

备份文件保存在 `./backups` 目录。

### Q: 忘记密码怎么办？

```bash
# 使用快速启动脚本重置
./快速启动.sh
# 选择选项 9，创建新账号
```

## 🔒 生产环境部署

### 安全加固

1. **修改默认密码**
   - 编辑 `docker-compose.yml` 修改数据库密码
   - 编辑 `backend/config.py` 修改 SECRET_KEY

2. **配置防火墙**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **使用Nginx反向代理**
   - 参考 [Ubuntu部署完整指南.md](Ubuntu部署完整指南.md#配置nginx反向代理)

4. **配置HTTPS**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

### 性能优化

- 限制Docker容器资源
- 配置PostgreSQL性能参数
- 启用Nginx缓存
- 定期清理Docker资源

详见：[Ubuntu部署完整指南.md](Ubuntu部署完整指南.md#性能优化)

## 📊 系统架构

```
┌─────────────┐
│   Frontend  │ (Vue 3 + Ant Design)
│  :8080      │
└──────┬──────┘
       │
       ↓
┌─────────────┐     ┌──────────────┐
│   Backend   │────→│  PostgreSQL  │
│   :5000     │     │    :5432     │
└──────┬──────┘     └──────────────┘
       │
       ↓
┌─────────────┐     ┌──────────────┐
│   Redis     │←────│    Celery    │
│   :6379     │     │ Worker/Beat  │
└─────────────┘     └──────────────┘
       │
       ↓
┌─────────────┐
│Mock Platform│ (模拟招聘平台)
│   :5001     │
└─────────────┘
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

- 查看文档：[Ubuntu使用指南.md](Ubuntu使用指南.md)
- 运行诊断：`./check_monitoring.sh`
- 查看日志：`docker-compose logs -f`

---

**快速开始：`./快速启动.sh`** 🚀
