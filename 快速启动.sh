#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "招聘信息监控系统 - 快速启动"
echo -e "==========================================${NC}"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker 未安装${NC}"
    echo "请先安装Docker: https://docs.docker.com/engine/install/ubuntu/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose 未安装${NC}"
    echo "请先安装Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker 环境检查通过${NC}"
echo ""

# 菜单选项
echo "请选择操作："
echo "  1) 首次安装/完整重建（停止→清理→重建→启动）"
echo "  2) 启动所有服务"
echo "  3) 停止所有服务"
echo "  4) 重启所有服务"
echo "  5) 查看服务状态"
echo "  6) 查看实时日志"
echo "  7) 检查监控系统"
echo "  8) 测试推送API"
echo "  9) 创建管理员账号"
echo "  0) 退出"
echo ""

read -p "请输入选项 [0-9]: " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}开始完整重建...${NC}"
        echo "这将删除所有数据并重新开始！"
        read -p "确定继续吗？(yes/no): " confirm
        
        if [ "$confirm" == "yes" ]; then
            echo ""
            echo "1. 停止所有服务..."
            docker-compose down -v
            
            echo ""
            echo "2. 清理Docker资源..."
            docker system prune -f
            
            echo ""
            echo "3. 重新构建并启动..."
            docker-compose up -d --build --force-recreate
            
            echo ""
            echo "4. 等待服务启动（30秒）..."
            sleep 30
            
            echo ""
            echo "5. 检查服务状态..."
            docker-compose ps
            
            echo ""
            echo -e "${GREEN}✓ 完整重建完成！${NC}"
        else
            echo "已取消"
        fi
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}启动所有服务...${NC}"
        docker-compose up -d
        sleep 10
        docker-compose ps
        echo -e "${GREEN}✓ 启动完成${NC}"
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}停止所有服务...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ 已停止${NC}"
        ;;
        
    4)
        echo ""
        echo -e "${YELLOW}重启所有服务...${NC}"
        docker-compose restart
        sleep 10
        docker-compose ps
        echo -e "${GREEN}✓ 重启完成${NC}"
        ;;
        
    5)
        echo ""
        echo -e "${YELLOW}服务状态：${NC}"
        docker-compose ps
        echo ""
        echo "Docker容器资源使用："
        docker stats --no-stream
        ;;
        
    6)
        echo ""
        echo -e "${YELLOW}实时日志（按Ctrl+C退出）：${NC}"
        echo ""
        docker-compose logs -f
        ;;
        
    7)
        echo ""
        echo -e "${YELLOW}运行监控系统诊断...${NC}"
        ./check_monitoring.sh
        ;;
        
    8)
        echo ""
        echo -e "${YELLOW}测试推送API...${NC}"
        if command -v python3 &> /dev/null; then
            if python3 -c "import requests" 2>/dev/null; then
                python3 test_push_api.py
            else
                echo -e "${RED}✗ 缺少requests库${NC}"
                echo "请先安装: pip3 install requests"
            fi
        else
            echo -e "${RED}✗ 未安装Python3${NC}"
        fi
        ;;
        
    9)
        echo ""
        echo -e "${YELLOW}创建管理员账号...${NC}"
        read -p "用户名: " username
        read -sp "密码: " password
        echo ""
        read -p "邮箱: " email
        
        docker-compose exec -T backend python << EOF
from app import create_app, db
from app.models import User

app = create_app(register_blueprints=False)
with app.app_context():
    existing_user = User.query.filter_by(username='$username').first()
    if existing_user:
        print("✗ 用户名已存在")
    else:
        user = User(username='$username', email='$email')
        user.set_password('$password')
        db.session.add(user)
        db.session.commit()
        print("✓ 账号创建成功！")
        print(f"用户名: $username")
        print(f"邮箱: $email")
EOF
        ;;
        
    0)
        echo ""
        echo "再见！"
        exit 0
        ;;
        
    *)
        echo ""
        echo -e "${RED}✗ 无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}=========================================="
echo "访问地址："
echo "  前端: http://localhost:8080"
echo "  后端API: http://localhost:5000"
echo "  API文档: http://localhost:5000/apidocs"
echo "  模拟平台: http://localhost:5001"
echo -e "==========================================${NC}"
echo ""
echo "更多命令："
echo "  查看日志: docker-compose logs -f [service_name]"
echo "  进入容器: docker-compose exec [service_name] bash"
echo "  重启服务: docker-compose restart [service_name]"
echo ""

