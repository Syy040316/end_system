#!/bin/bash

echo "=========================================="
echo "API功能测试"
echo "=========================================="
echo ""

# 测试后端健康检查
echo "1. 测试后端健康检查..."
curl -s http://localhost:5000/health | python3 -m json.tool || echo "健康检查失败"

echo ""
echo ""

# 测试模拟平台
echo "2. 测试模拟平台..."
curl -s http://localhost:5001/api/v1/stats | python3 -m json.tool || echo "模拟平台失败"

echo ""
echo ""

# 测试注册API
echo "3. 测试用户注册API..."
curl -s -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser_'$(date +%s)'","email":"test'$(date +%s)'@example.com","password":"password123"}' \
  | python3 -m json.tool

echo ""
echo ""

echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "如果看到成功的响应，说明API正常工作"
echo ""

