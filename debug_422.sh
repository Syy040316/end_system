#!/bin/bash

echo "=========================================="
echo "422错误深度诊断"
echo "=========================================="
echo ""

echo "1. 查看后端实时日志（请在浏览器刷新页面触发请求）..."
echo "按 Ctrl+C 停止查看日志"
echo ""
docker-compose logs -f backend

