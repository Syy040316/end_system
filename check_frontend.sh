#!/bin/bash

echo "=========================================="
echo "前端服务诊断"
echo "=========================================="
echo ""

echo "1. 检查前端容器状态..."
docker-compose ps frontend

echo ""
echo "2. 查看前端最新日志..."
docker-compose logs --tail=50 frontend

echo ""
echo "3. 检查端口占用..."
netstat -tuln | grep 5173 || ss -tuln | grep 5173

echo ""
echo "4. 尝试重启前端服务..."
docker-compose restart frontend

echo ""
echo "5. 等待10秒..."
sleep 10

echo ""
echo "6. 再次检查状态..."
docker-compose ps frontend

echo ""
echo "7. 查看重启后日志..."
docker-compose logs --tail=30 frontend

echo ""
echo "=========================================="
echo "诊断完成！"
echo "=========================================="
echo ""
echo "如果服务正常，请访问: http://localhost:5173"
echo ""

