#!/bin/bash

echo "=========================================="
echo "招聘信息监控系统 - 快速启动脚本"
echo "=========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建.env文件（如果不存在）
if [ ! -f .env ]; then
    echo "创建环境变量文件..."
    cat > .env << EOF
# 邮件配置（可选，不配置则邮件功能不可用）
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
EOF
    echo "已创建 .env 文件，请根据需要配置邮件信息"
fi

echo "启动所有服务..."
docker-compose up -d

echo ""
echo "等待服务启动..."
sleep 10

echo ""
echo "=========================================="
echo "启动完成！"
echo "=========================================="
echo ""
echo "服务地址："
echo "  - 前端界面: http://localhost:5173"
echo "  - 后端API: http://localhost:5000"
echo "  - API文档: http://localhost:5000/apidocs"
echo "  - 模拟招聘平台: http://localhost:5001"
echo ""
echo "查看日志："
echo "  docker-compose logs -f"
echo ""
echo "停止服务："
echo "  docker-compose down"
echo ""
echo "=========================================="

