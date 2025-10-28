#!/bin/bash

echo "=========================================="
echo "重新构建所有服务..."
echo "=========================================="

echo ""
echo "1. 停止所有服务..."
docker-compose down

echo ""
echo "2. 重新构建并启动..."
docker-compose up -d --build

echo ""
echo "3. 等待服务启动..."
echo "等待30秒让服务完全启动..."
sleep 30

echo ""
echo "4. 查看服务状态..."
docker-compose ps

echo ""
echo "5. 查看最新日志..."
docker-compose logs --tail=50

echo ""
echo "=========================================="
echo "✓ 完成！"
echo "前端访问: http://localhost:8080"
echo "后端API: http://localhost:5000"
echo "模拟平台: http://localhost:5001"
echo "=========================================="
echo ""
echo "提示："
echo "  - 查看实时日志: docker-compose logs -f"
echo "  - 检查监控系统: ./check_monitoring.sh"
echo "  - 测试推送API: python3 test_push_api.py"
echo ""

