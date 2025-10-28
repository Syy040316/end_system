#!/bin/bash

echo "=========================================="
echo "最终修复并重启"
echo "=========================================="
echo ""

echo "1. 停止所有服务..."
docker-compose down

echo ""
echo "2. 重新构建后端..."
docker-compose build backend

echo ""
echo "3. 启动所有服务..."
docker-compose up -d

echo ""
echo "4. 等待15秒..."
sleep 15

echo ""
echo "5. 检查服务状态..."
docker-compose ps

echo ""
echo "6. 查看后端日志（检查是否有错误）..."
docker-compose logs --tail=30 backend

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="
echo ""
echo "✅ 现在请："
echo "1. 访问 http://localhost:5173"
echo "2. 退出登录（如果已登录）"
echo "3. 重新登录"
echo "4. 应该可以正常使用了！"
echo ""

