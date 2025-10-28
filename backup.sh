#!/bin/bash

# 备份脚本 - 备份数据库和配置文件

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 备份目录
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}"

echo -e "${YELLOW}=========================================="
echo "开始备份系统数据"
echo "==========================================${NC}"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "1. 备份数据库..."
docker-compose exec -T postgres pg_dump -U admin job_monitor > "$BACKUP_DIR/${BACKUP_FILE}_database.sql"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据库备份成功${NC}"
    DB_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_FILE}_database.sql" | cut -f1)
    echo "  文件大小: $DB_SIZE"
else
    echo "✗ 数据库备份失败"
fi

echo ""
echo "2. 备份配置文件..."

# 创建临时目录
TEMP_DIR="$BACKUP_DIR/temp_$TIMESTAMP"
mkdir -p "$TEMP_DIR"

# 复制配置文件
cp -r .env "$TEMP_DIR/" 2>/dev/null
cp -r docker-compose.yml "$TEMP_DIR/"
cp -r backend/config.py "$TEMP_DIR/" 2>/dev/null

# 打包配置文件
cd "$BACKUP_DIR"
tar -czf "${BACKUP_FILE}_config.tar.gz" "temp_$TIMESTAMP"
cd ..
rm -rf "$TEMP_DIR"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 配置文件备份成功${NC}"
    CONFIG_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_FILE}_config.tar.gz" | cut -f1)
    echo "  文件大小: $CONFIG_SIZE"
else
    echo "✗ 配置文件备份失败"
fi

echo ""
echo "3. 清理旧备份（保留最近7天）..."
find "$BACKUP_DIR" -name "backup_*" -mtime +7 -delete
REMAINING=$(ls -1 "$BACKUP_DIR"/backup_* 2>/dev/null | wc -l)
echo -e "${GREEN}✓ 清理完成，剩余备份: $REMAINING 个${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "备份完成！"
echo "==========================================${NC}"
echo ""
echo "备份位置: $BACKUP_DIR"
echo "备份文件:"
echo "  - ${BACKUP_FILE}_database.sql"
echo "  - ${BACKUP_FILE}_config.tar.gz"
echo ""
echo "恢复数据库："
echo "  cat $BACKUP_DIR/${BACKUP_FILE}_database.sql | docker-compose exec -T postgres psql -U admin job_monitor"
echo ""

