# Ubuntu环境启动指南

## 🚀 快速开始

### 1. 赋予脚本执行权限

```bash
chmod +x rebuild_all.sh check_monitoring.sh
```

### 2. 重新构建所有服务

```bash
./rebuild_all.sh
```

或者手动执行：

```bash
# 停止所有服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 等待服务启动

等待约30秒，直到所有服务健康检查通过：

```bash
# 持续监控服务状态
watch docker-compose ps

# 或者查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. 访问系统

- **前端界面**: http://localhost:8080
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/apidocs
- **模拟平台**: http://localhost:5001

### 5. 检查监控系统

```bash
./check_monitoring.sh
```

## 📊 测试推送API

### 安装Python依赖

```bash
pip3 install requests
```

### 运行测试脚本

```bash
python3 test_push_api.py
```

## 🔍 常用命令

### 查看所有服务状态

```bash
docker-compose ps
```

### 查看特定服务日志

```bash
# 后端日志
docker-compose logs -f backend

# Celery Worker日志
docker-compose logs -f celery_worker

# Celery Beat日志
docker-compose logs -f celery_beat

# 前端日志
docker-compose logs -f frontend

# 数据库日志
docker-compose logs -f postgres

# 模拟平台日志
docker-compose logs -f mock_platform
```

### 重启特定服务

```bash
# 重启后端
docker-compose restart backend

# 重启前端
docker-compose restart frontend

# 重启Celery worker
docker-compose restart celery_worker
```

### 进入容器调试

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U admin -d job_monitor

# 进入前端容器
docker-compose exec frontend sh
```

### 手动触发监控任务

```bash
docker-compose exec backend python << 'EOF'
from app import create_app, db
from app.models import MonitoringRule
from app.tasks.monitor import execute_monitoring_task

app = create_app(register_blueprints=False)
with app.app_context():
    rules = MonitoringRule.query.filter_by(is_active=True).all()
    print(f"找到 {len(rules)} 个活跃规则")
    
    for rule in rules:
        print(f"执行规则: {rule.rule_name}")
        result = execute_monitoring_task.delay(rule.rule_id)
        print(f"任务ID: {result.id}")
EOF
```

### 查看数据库数据

```bash
# 查看所有用户
docker-compose exec backend python << 'EOF'
from app import create_app, db
from app.models import User

app = create_app(register_blueprints=False)
with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"ID: {u.user_id}, 用户名: {u.username}, 邮箱: {u.email}")
EOF

# 查看监控规则
docker-compose exec backend python << 'EOF'
from app import create_app, db
from app.models import MonitoringRule

app = create_app(register_blueprints=False)
with app.app_context():
    rules = MonitoringRule.query.all()
    for r in rules:
        print(f"ID: {r.rule_id}, 名称: {r.rule_name}, 激活: {r.is_active}")
EOF

# 查看扫描结果
docker-compose exec backend python << 'EOF'
from app import create_app, db
from app.models import ScanResult

app = create_app(register_blueprints=False)
with app.app_context():
    results = ScanResult.query.order_by(ScanResult.scan_time.desc()).limit(10).all()
    for r in results:
        print(f"规则ID: {r.rule_id}, 时间: {r.scan_time}, 新增: {len(r.get_jobs_new())}, 更新: {len(r.get_jobs_updated())}")
EOF
```

## 🔧 故障排查

### 问题1：端口被占用

```bash
# 查看端口占用
sudo netstat -tlnp | grep ':8080\|:5000\|:5001\|:5432\|:6379'

# 或使用lsof
sudo lsof -i :8080
sudo lsof -i :5000

# 停止占用端口的进程
sudo kill -9 <PID>
```

### 问题2：Docker权限问题

```bash
# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或刷新组
newgrp docker

# 测试
docker ps
```

### 问题3：服务无法启动

```bash
# 完全清理并重启
docker-compose down -v
docker system prune -f
docker-compose up -d --build --force-recreate

# 查看详细日志
docker-compose logs --tail=100
```

### 问题4：数据库连接失败

```bash
# 检查PostgreSQL是否就绪
docker-compose exec postgres pg_isready -U admin -d job_monitor

# 查看数据库日志
docker-compose logs postgres

# 手动连接测试
docker-compose exec postgres psql -U admin -d job_monitor -c "SELECT 1;"
```

### 问题5：前端无法访问后端

```bash
# 检查网络
docker-compose exec frontend ping backend

# 检查后端是否正常
curl http://localhost:5000/health

# 查看前端环境变量
docker-compose exec frontend env | grep VITE
```

### 问题6：监控没有执行

```bash
# 检查Celery Beat
docker-compose logs celery_beat | grep "Scheduler"

# 检查Celery Worker
docker-compose logs celery_worker | grep "ready"

# 查看Redis连接
docker-compose exec redis redis-cli ping
```

## 📈 性能优化

### 查看资源使用

```bash
# 查看Docker容器资源使用
docker stats

# 查看系统资源
htop
# 或
top
```

### 清理Docker资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理未使用的网络
docker network prune

# 一次性清理所有（谨慎使用）
docker system prune -a --volumes
```

## 🌐 外网访问配置

如果需要从外网访问：

### 1. 修改前端配置

编辑 `frontend/.env.production`:

```bash
VITE_API_BASE_URL=http://your-server-ip:5000
```

### 2. 配置防火墙

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 8080/tcp
sudo ufw allow 5000/tcp
sudo ufw allow 5001/tcp

# 或使用iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### 3. 配置Nginx反向代理（推荐）

```bash
# 安装Nginx
sudo apt update
sudo apt install nginx

# 创建配置文件
sudo nano /etc/nginx/sites-available/job-monitor
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/job-monitor /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

## 📝 日常维护

### 备份数据库

```bash
# 导出数据
docker-compose exec postgres pg_dump -U admin job_monitor > backup_$(date +%Y%m%d).sql

# 恢复数据
cat backup_20251028.sql | docker-compose exec -T postgres psql -U admin job_monitor
```

### 更新系统

```bash
# 拉取最新代码
git pull

# 重新构建
./rebuild_all.sh

# 运行数据库迁移（如有）
docker-compose exec backend flask db upgrade
```

### 定期清理日志

```bash
# 查看日志大小
docker-compose logs --tail=0 | wc -l

# 清理旧日志
docker-compose down
docker-compose up -d
```

## 🆘 紧急恢复

如果系统完全崩溃：

```bash
#!/bin/bash
# 保存为 emergency_reset.sh

echo "警告：这将删除所有数据！"
read -p "确定要继续吗？(yes/no): " confirm

if [ "$confirm" == "yes" ]; then
    echo "停止所有服务..."
    docker-compose down -v
    
    echo "清理Docker资源..."
    docker system prune -af --volumes
    
    echo "重新构建..."
    docker-compose up -d --build --force-recreate
    
    echo "等待服务启动..."
    sleep 30
    
    echo "检查状态..."
    docker-compose ps
    
    echo "完成！请访问 http://localhost:8080"
else
    echo "已取消"
fi
```

---

**现在可以运行 `./rebuild_all.sh` 开始使用了！** 🚀

