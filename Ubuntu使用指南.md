# Ubuntu 使用指南

## 🚀 快速开始

### 第一次使用

```bash
# 1. 赋予脚本执行权限
chmod +x *.sh

# 2. 启动系统（推荐使用交互式菜单）
./快速启动.sh

# 或直接重建所有服务
./rebuild_all.sh
```

### 访问系统

- **前端界面**: http://localhost:8080
- **后端API**: http://localhost:5000  
- **API文档**: http://localhost:5000/apidocs
- **模拟平台**: http://localhost:5001

## 📜 可用脚本说明

### 🔧 核心脚本

#### `快速启动.sh` - 交互式管理工具（推荐）
功能齐全的交互式菜单，包含所有常用操作：

```bash
./快速启动.sh
```

提供以下功能：
1. 首次安装/完整重建
2. 启动所有服务
3. 停止所有服务
4. 重启所有服务
5. 查看服务状态
6. 查看实时日志
7. 检查监控系统
8. 创建管理员账号

#### `rebuild_all.sh` - 完整重建
停止所有服务，重新构建并启动：

```bash
./rebuild_all.sh
```

**用途**：
- 首次部署
- 代码有重大更新
- 遇到无法解决的问题需要重新开始

#### `check_monitoring.sh` - 监控系统诊断
全面诊断监控系统是否正常工作：

```bash
./check_monitoring.sh
```

**检查内容**：
- 所有服务状态
- Celery Beat 定时任务
- Celery Worker 任务执行
- 模拟平台数据
- 数据库连接
- 监控规则列表
- 手动触发测试
- 查看扫描结果

### 🔄 维护脚本

#### `backup.sh` - 数据备份
备份数据库和配置文件：

```bash
./backup.sh
```

**备份内容**：
- PostgreSQL 数据库
- 配置文件（.env, docker-compose.yml等）
- 自动清理7天前的旧备份

**恢复方法**：
```bash
# 恢复数据库
cat backups/backup_20251028_120000_database.sql | docker-compose exec -T postgres psql -U admin job_monitor
```

#### `update.sh` - 从Git更新
从Git仓库拉取最新代码并重新部署：

```bash
./update.sh
```

**更新流程**：
1. 自动备份当前数据
2. 显示待更新内容
3. 拉取最新代码
4. 重新构建服务
5. 运行数据库迁移
6. 检查服务状态

### 🧪 测试脚本

<!-- 推送API功能暂未实现，测试脚本已移除
如需实现，请参考 紧急修复说明.md -->

## 🛠️ 常用命令

### Docker Compose 基础命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除所有数据
docker-compose down -v

# 查看服务状态
docker-compose ps

# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker

# 重启服务
docker-compose restart
docker-compose restart backend

# 重新构建
docker-compose up -d --build

# 强制重建
docker-compose up -d --build --force-recreate
```

### 进入容器调试

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库
docker-compose exec postgres psql -U admin -d job_monitor

# 进入前端容器
docker-compose exec frontend sh

# 执行Python命令
docker-compose exec backend python -c "from app import create_app; print('OK')"
```

### 数据库操作

```bash
# 检查数据库连接
docker-compose exec postgres pg_isready -U admin -d job_monitor

# 备份数据库
docker-compose exec postgres pg_dump -U admin job_monitor > backup.sql

# 恢复数据库
cat backup.sql | docker-compose exec -T postgres psql -U admin job_monitor

# 查看数据库大小
docker-compose exec postgres psql -U admin -d job_monitor -c "SELECT pg_size_pretty(pg_database_size('job_monitor'));"

# 查询用户表
docker-compose exec -T backend python << 'EOF'
from app import create_app, db
from app.models import User
app = create_app(register_blueprints=False)
with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"{u.user_id}: {u.username} - {u.email}")
EOF
```

### 手动触发监控任务

```bash
docker-compose exec -T backend python << 'EOF'
from app import create_app, db
from app.models import MonitoringRule
from app.tasks.monitor import execute_monitoring_task

app = create_app(register_blueprints=False)
with app.app_context():
    rules = MonitoringRule.query.filter_by(is_active=True).all()
    for rule in rules:
        print(f"触发: {rule.rule_name}")
        execute_monitoring_task.delay(rule.rule_id)
EOF
```

### 查看系统资源

```bash
# 查看Docker容器资源使用
docker stats

# 查看系统资源
htop  # 或 top

# 查看磁盘使用
df -h
docker system df

# 查看Docker日志大小
du -sh /var/lib/docker/containers/*/*-json.log
```

## 🔧 故障排查

### 问题1：端口被占用

```bash
# 查看端口占用
sudo lsof -i :8080
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>
```

### 问题2：服务无法启动

```bash
# 查看详细日志
docker-compose logs

# 完全清理并重启
docker-compose down -v
docker system prune -af --volumes
./rebuild_all.sh
```

### 问题3：数据库连接失败

```bash
# 检查PostgreSQL
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres

# 等待数据库就绪
docker-compose exec postgres pg_isready -U admin -d job_monitor
```

### 问题4：前端无法访问后端

```bash
# 检查后端健康
curl http://localhost:5000/health

# 检查网络
docker-compose exec frontend ping backend

# 重启前端
docker-compose restart frontend
```

### 问题5：监控不工作

```bash
# 运行诊断工具
./check_monitoring.sh

# 查看Celery日志
docker-compose logs celery_worker
docker-compose logs celery_beat

# 检查Redis
docker-compose exec redis redis-cli ping
```

## 🔒 安全建议（生产环境）

### 1. 修改默认密码

```bash
# 编辑docker-compose.yml
nano docker-compose.yml
# 修改 POSTGRES_PASSWORD

# 生成随机密钥
python3 -c "import secrets; print(secrets.token_hex(32))"

# 编辑backend/config.py
nano backend/config.py
# 修改 SECRET_KEY
```

### 2. 配置防火墙

```bash
# 只开放必要端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. 使用Nginx反向代理

```bash
# 安装Nginx
sudo apt update
sudo apt install nginx

# 创建配置
sudo nano /etc/nginx/sites-available/job-monitor

# 启用站点
sudo ln -s /etc/nginx/sites-available/job-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. 配置HTTPS

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 📈 性能优化

### 限制容器资源

编辑 `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### 清理Docker资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理所有未使用资源
docker system prune -a --volumes

# 查看空间占用
docker system df
```

## 📅 定期维护

### 设置自动备份

```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点备份
0 2 * * * /home/yourusername/end_system/backup.sh

# 添加每周日凌晨3点清理
0 3 * * 0 /usr/bin/docker system prune -af
```

### 监控日志大小

```bash
# 限制Docker日志大小
# 编辑 /etc/docker/daemon.json
sudo nano /etc/docker/daemon.json

# 添加：
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# 重启Docker
sudo systemctl restart docker
```

## 📞 获取帮助

### 查看文档

- `Ubuntu部署完整指南.md` - 完整部署教程
- `更新说明.md` - 新功能说明
- `启动指南-Ubuntu.md` - 详细命令参考

### 常用资源

- Docker官方文档: https://docs.docker.com/
- Docker Compose文档: https://docs.docker.com/compose/
- PostgreSQL文档: https://www.postgresql.org/docs/

### 日志位置

```bash
# 容器日志
docker-compose logs

# 系统日志
/var/log/syslog

# Nginx日志（如果安装）
/var/log/nginx/access.log
/var/log/nginx/error.log
```

## 🎯 快速参考

```bash
# 启动
./快速启动.sh              # 交互式菜单
./rebuild_all.sh          # 完整重建

# 日常操作
docker-compose up -d      # 启动
docker-compose down       # 停止
docker-compose restart    # 重启
docker-compose ps         # 状态
docker-compose logs -f    # 日志

# 维护
./backup.sh               # 备份
./update.sh               # 更新
./check_monitoring.sh     # 诊断

# 测试
curl http://localhost:5000/health  # 健康检查
```

---

**遇到问题？运行 `./check_monitoring.sh` 进行全面诊断！** 🔍

