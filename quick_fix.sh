#!/bin/bash

echo "=========================================="
echo "快速修复并重启后端"
echo "=========================================="
echo ""

echo "1. 重新构建后端..."
docker-compose build backend

echo ""
echo "2. 重启后端和celery..."
docker-compose restart backend celery_worker celery_beat

echo ""
echo "3. 等待10秒..."
sleep 10

echo ""
echo "4. 检查服务状态..."
docker-compose ps

echo ""
echo "5. 查看后端日志..."
docker-compose logs --tail=30 backend

echo ""
echo "=========================================="
echo "修复完成！"
echo "=========================================="
echo ""
echo "现在请："
echo "1. 在浏览器中退出登录"
echo "2. 重新登录"
echo "3. 刷新页面"
echo ""
echo "问题应该已经解决！"
echo ""

