#!/bin/bash

echo "=========================================="
echo "数据库诊断和修复工具"
echo "=========================================="
echo ""

echo "1. 检查后端容器状态..."
docker-compose ps backend

echo ""
echo "2. 检查数据库迁移状态..."
docker-compose exec backend flask db current || echo "迁移状态检查失败"

echo ""
echo "3. 查看后端日志（查找错误）..."
docker-compose logs --tail=30 backend | grep -i error || echo "未发现错误日志"

echo ""
echo "4. 尝试执行数据库迁移..."
docker-compose exec backend flask db upgrade

echo ""
echo "5. 重启后端服务..."
docker-compose restart backend

echo ""
echo "6. 等待5秒..."
sleep 5

echo ""
echo "7. 再次检查后端状态..."
docker-compose ps backend

echo ""
echo "8. 查看重启后的日志..."
docker-compose logs --tail=20 backend

echo ""
echo "=========================================="
echo "修复完成！"
echo "=========================================="
echo ""
echo "请刷新浏览器页面重试"
echo ""

