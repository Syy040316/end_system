#!/bin/bash

echo "=========================================="
echo "重新构建后端并查看详细日志"
echo "=========================================="
echo ""

echo "1. 重新构建后端..."
docker-compose build backend

echo ""
echo "2. 重启后端..."
docker-compose restart backend

echo ""
echo "3. 等待5秒..."
sleep 5

echo ""
echo "4. 开始实时查看日志（请在浏览器刷新页面）..."
echo "现在请在浏览器中刷新页面，然后观察下面的日志输出"
echo "按 Ctrl+C 停止"
echo ""

docker-compose logs -f backend

