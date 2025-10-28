#!/bin/bash

echo "=========================================="
echo "重启招聘监控系统服务"
echo "=========================================="
echo ""

echo "1. 停止所有服务..."
docker-compose down

echo ""
echo "2. 重新构建后端、Celery服务..."
docker-compose build backend celery_worker celery_beat

echo ""
echo "3. 启动所有服务..."
docker-compose up -d

echo ""
echo "4. 等待15秒让服务完全启动..."
sleep 15

echo ""
echo "5. 检查服务状态..."
docker-compose ps

echo ""
echo "6. 查看关键服务日志..."
echo ""
echo "=== 后端日志 ==="
docker-compose logs --tail=20 backend

echo ""
echo "=== Celery Worker日志 ==="
docker-compose logs --tail=20 celery_worker

echo ""
echo "=== 前端日志 ==="
docker-compose logs --tail=10 frontend

echo ""
echo "=========================================="
echo "重启完成！"
echo "=========================================="
echo ""
echo "访问系统："
echo "  - 前端: http://localhost:5173"
echo "  - 后端API: http://localhost:5000/health"
echo "  - 模拟平台: http://localhost:5001/health"
echo ""
echo "实时查看日志："
echo "  docker-compose logs -f"
echo ""

