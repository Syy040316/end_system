# Ubuntu服务器部署完整指南

## 📋 前置要求

### 系统要求
- Ubuntu 20.04 LTS 或更高版本
- 至少 4GB RAM
- 至少 20GB 可用磁盘空间

### 需要安装的软件

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将当前用户添加到docker组（避免每次使用sudo）
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
docker-compose --version

# 安装Git（如果还没有）
sudo apt install -y git

# 安装Python3和pip（用于测试脚本）
sudo apt install -y python3 python3-pip
pip3 install requests
```

## 🚀 部署步骤

### 1. 上传代码到Ubuntu服务器

#### 方法A：使用Git（推荐）

在Ubuntu服务器上：

```bash
# 克隆仓库
cd ~
git clone https://github.com/Syy040316/end_system.git
cd end_system
```

#### 方法B：使用SCP从Windows上传

在Windows PowerShell中：

```powershell
# 压缩项目（排除node_modules等）
# 手动压缩 end_system 文件夹为 end_system.zip

# 使用SCP上传（需要先安装OpenSSH）
scp end_system.zip username@your-ubuntu-server-ip:~/

# 然后SSH到Ubuntu服务器解压
ssh username@your-ubuntu-server-ip
cd ~
unzip end_system.zip
cd end_system
```

#### 方法C：使用FTP/SFTP工具

使用 WinSCP、FileZilla 等工具上传整个项目文件夹。

### 2. 配置环境变量

```bash
cd ~/end_system

# 创建.env文件（邮件配置，可选）
cat > .env << 'EOF'
# 邮件配置（可选，不配置则邮件功能不可用）
# Gmail示例
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# QQ邮箱示例（取消注释并修改）
# MAIL_SERVER=smtp.qq.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-qq@qq.com
# MAIL_PASSWORD=你的授权码
# MAIL_DEFAULT_SENDER=your-qq@qq.com

# 163邮箱示例（取消注释并修改）
# MAIL_SERVER=smtp.163.com
# MAIL_PORT=465
# MAIL_USE_SSL=True
# MAIL_USERNAME=your-email@163.com
# MAIL_PASSWORD=你的授权码
# MAIL_DEFAULT_SENDER=your-email@163.com
EOF

# 编辑配置（如果需要）
nano .env
```

### 3. 赋予脚本执行权限

```bash
chmod +x rebuild_all.sh
chmod +x check_monitoring.sh
chmod +x start.sh
chmod +x quick_fix.sh
chmod +x rebuild_backend.sh
```

### 4. 启动所有服务

```bash
# 方法1：使用自动化脚本
./rebuild_all.sh

# 方法2：手动启动
docker-compose down
docker-compose up -d --build

# 查看启动日志
docker-compose logs -f
```

### 5. 等待服务启动完成

```bash
# 持续查看所有服务状态（按Ctrl+C退出）
watch -n 2 'docker-compose ps'

# 或者查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

等待所有服务状态变为 `Up (healthy)` 或 `Up`。

### 6. 验证服务

```bash
# 检查所有容器是否运行
docker-compose ps

# 测试后端健康检查
curl http://localhost:5000/health

# 测试模拟平台
curl http://localhost:5001/api/v1/stats

# 测试前端（应该返回HTML）
curl http://localhost:8080
```

### 7. 创建测试账号

```bash
# 方法1：通过前端界面注册
# 访问 http://your-server-ip:8080 在浏览器中注册

# 方法2：通过命令行创建
docker-compose exec backend python << 'EOF'
from app import create_app, db
from app.models import User

app = create_app(register_blueprints=False)
with app.app_context():
    # 检查用户是否已存在
    existing_user = User.query.filter_by(username='admin').first()
    if not existing_user:
        user = User(
            username='admin',
            email='admin@example.com'
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        print("管理员账号创建成功！")
        print("用户名: admin")
        print("密码: admin123")
    else:
        print("用户已存在")
EOF
```

### 8. 测试新功能

```bash
# 测试推送API
python3 test_push_api.py

# 检查监控系统
./check_monitoring.sh
```

## 🌐 配置外网访问

### 方法1：直接访问（临时测试用）

```bash
# 配置防火墙允许端口
sudo ufw allow 8080/tcp  # 前端
sudo ufw allow 5000/tcp  # 后端API
sudo ufw allow 5001/tcp  # 模拟平台（可选）

# 启用防火墙（如果还没启用）
sudo ufw enable
sudo ufw status
```

然后从外网访问：`http://your-server-ip:8080`

### 方法2：使用Nginx反向代理（生产环境推荐）

```bash
# 安装Nginx
sudo apt update
sudo apt install -y nginx

# 创建配置文件
sudo nano /etc/nginx/sites-available/job-monitor

# 添加以下内容：
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名或IP

    # 前端
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 模拟平台（可选）
    location /mock {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/job-monitor /etc/nginx/sites-enabled/

# 删除默认站点（可选）
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

# 配置防火墙
sudo ufw allow 'Nginx Full'
```

### 方法3：配置HTTPS（使用Let's Encrypt）

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取SSL证书（需要域名）
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

## 📊 监控和维护

### 查看日志

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f postgres

# 查看最近100行日志
docker-compose logs --tail=100

# 保存日志到文件
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
docker-compose restart frontend
docker-compose restart celery_worker

# 完全重建（如果有代码更新）
./rebuild_all.sh
```

### 数据库维护

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U admin job_monitor > backup_$(date +%Y%m%d).sql

# 恢复数据库
cat backup_20251028.sql | docker-compose exec -T postgres psql -U admin job_monitor

# 进入数据库命令行
docker-compose exec postgres psql -U admin -d job_monitor

# 查看数据库大小
docker-compose exec postgres psql -U admin -d job_monitor -c "SELECT pg_size_pretty(pg_database_size('job_monitor'));"
```

### 系统资源监控

```bash
# 安装htop（如果没有）
sudo apt install htop

# 查看系统资源
htop

# 查看Docker容器资源使用
docker stats

# 查看磁盘使用
df -h
docker system df
```

### 清理资源

```bash
# 清理未使用的Docker镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理未使用的网络
docker network prune

# 一次性清理所有未使用资源
docker system prune -a --volumes
```

## 🔧 常见问题解决

### 问题1：容器无法启动

```bash
# 查看错误日志
docker-compose logs

# 完全清理并重启
docker-compose down -v
docker system prune -af --volumes
docker-compose up -d --build --force-recreate
```

### 问题2：端口被占用

```bash
# 查看端口占用
sudo lsof -i :8080
sudo lsof -i :5000
sudo lsof -i :5432

# 杀死占用端口的进程
sudo kill -9 <PID>

# 或修改docker-compose.yml中的端口映射
```

### 问题3：前端无法连接后端

```bash
# 检查后端是否运行
curl http://localhost:5000/health

# 检查网络连通性
docker-compose exec frontend ping backend

# 查看前端环境变量
docker-compose exec frontend env | grep VITE

# 重启前端
docker-compose restart frontend
```

### 问题4：数据库连接失败

```bash
# 检查PostgreSQL状态
docker-compose exec postgres pg_isready -U admin -d job_monitor

# 查看数据库日志
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

### 问题5：Celery任务不执行

```bash
# 检查Celery Beat
docker-compose logs celery_beat | grep "Scheduler"

# 检查Celery Worker
docker-compose logs celery_worker | grep "ready"

# 检查Redis连接
docker-compose exec redis redis-cli ping

# 手动触发任务测试
./check_monitoring.sh
```

## 🔒 安全加固（生产环境必做）

### 1. 修改默认密码

编辑 `docker-compose.yml`：

```yaml
postgres:
  environment:
    POSTGRES_PASSWORD: 使用强密码  # 修改这里
```

编辑 `backend/config.py`：

```python
SECRET_KEY = '生成一个长随机字符串'  # 修改这里
```

```bash
# 生成随机密钥
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. 配置防火墙

```bash
# 只允许必要的端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. 禁用不必要的端口暴露

编辑 `docker-compose.yml`，注释掉不需要外网访问的端口：

```yaml
postgres:
  # ports:
  #   - "5432:5432"  # 注释掉，只允许内部访问

redis:
  # ports:
  #   - "6379:6379"  # 注释掉
```

### 4. 设置环境变量

```bash
# 创建.env文件存储敏感信息
cat > .env << 'EOF'
# 数据库
POSTGRES_PASSWORD=strong_password_here

# JWT密钥
SECRET_KEY=your_secret_key_here

# 邮件配置
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password
EOF

# 设置权限
chmod 600 .env
```

## 📈 性能优化

### 1. 配置Docker资源限制

编辑 `docker-compose.yml` 添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          memory: 512M
```

### 2. 配置PostgreSQL性能

```bash
# 编辑PostgreSQL配置
docker-compose exec postgres bash
vi /var/lib/postgresql/data/postgresql.conf

# 或挂载自定义配置
# 在docker-compose.yml中添加：
volumes:
  - ./postgres.conf:/etc/postgresql/postgresql.conf
```

### 3. 配置Nginx缓存

在Nginx配置中添加：

```nginx
# 添加缓存配置
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location /api {
    proxy_cache my_cache;
    proxy_cache_valid 200 5m;
    # ... 其他配置
}
```

## 🔄 自动更新部署

### 创建更新脚本

```bash
cat > update.sh << 'EOF'
#!/bin/bash

echo "开始更新系统..."

# 拉取最新代码
git pull

# 重新构建
docker-compose down
docker-compose up -d --build

# 等待服务启动
sleep 30

# 检查状态
docker-compose ps

echo "更新完成！"
EOF

chmod +x update.sh
```

### 配置自动备份

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/$(whoami)/backups"
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T postgres pg_dump -U admin job_monitor > "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"

# 只保留最近7天的备份
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete

echo "备份完成：$BACKUP_DIR"
EOF

chmod +x backup.sh

# 添加到crontab（每天凌晨2点备份）
crontab -e
# 添加这一行：
# 0 2 * * * /home/yourusername/end_system/backup.sh
```

## 📞 快速命令参考

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 重新构建
./rebuild_all.sh

# 检查监控
./check_monitoring.sh

# 测试API
python3 test_push_api.py

# 备份数据库
./backup.sh

# 更新系统
./update.sh
```

---

**部署完成后，访问 `http://your-server-ip:8080` 开始使用！** 🎉

如遇问题，请查看日志：`docker-compose logs -f`

