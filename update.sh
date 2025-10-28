#!/bin/bash

# 更新脚本 - 从Git拉取最新代码并重新部署

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "系统更新工具"
echo "==========================================${NC}"
echo ""

# 检查是否是git仓库
if [ ! -d ".git" ]; then
    echo -e "${RED}✗ 当前目录不是Git仓库${NC}"
    echo "如果需要从Git更新，请先初始化仓库"
    exit 1
fi

echo "1. 备份当前数据..."
./backup.sh

echo ""
echo "2. 拉取最新代码..."
git fetch origin

# 显示变更
echo ""
echo "将要更新的内容："
git log HEAD..origin/main --oneline 2>/dev/null || git log HEAD..origin/master --oneline

echo ""
read -p "确定要更新吗？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "已取消更新"
    exit 0
fi

# 保存本地修改
echo ""
echo "3. 保存本地修改..."
git stash

# 拉取代码
echo ""
echo "4. 拉取最新代码..."
git pull origin main 2>/dev/null || git pull origin master

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 代码拉取失败${NC}"
    echo "正在恢复本地修改..."
    git stash pop
    exit 1
fi

# 恢复本地修改
if git stash list | grep -q "stash@{0}"; then
    echo ""
    echo "5. 恢复本地修改..."
    git stash pop
fi

# 重新构建
echo ""
echo "6. 重新构建服务..."
docker-compose down
docker-compose up -d --build

echo ""
echo "7. 等待服务启动..."
sleep 30

# 运行数据库迁移（如果有）
echo ""
echo "8. 检查数据库迁移..."
docker-compose exec -T backend flask db current 2>/dev/null
if [ $? -eq 0 ]; then
    echo "运行数据库迁移..."
    docker-compose exec -T backend flask db upgrade
fi

# 检查服务状态
echo ""
echo "9. 检查服务状态..."
docker-compose ps

echo ""
echo -e "${GREEN}=========================================="
echo "✓ 更新完成！"
echo "==========================================${NC}"
echo ""
echo "访问地址："
echo "  前端: http://localhost:8080"
echo "  后端: http://localhost:5000"
echo ""
echo "如果遇到问题："
echo "  1. 查看日志: docker-compose logs -f"
echo "  2. 完全重建: ./rebuild_all.sh"
echo "  3. 恢复备份: 查看 ./backups 目录"
echo ""

