#!/bin/bash

echo "=========================================="
echo "监控系统诊断"
echo "=========================================="
echo ""

echo "1. 检查Celery Beat是否在运行..."
docker-compose logs --tail=20 celery_beat | grep -i "execute_all_monitoring_tasks"

echo ""
echo "2. 检查Celery Worker是否在运行..."
docker-compose logs --tail=20 celery_worker | grep -i "monitoring"

echo ""
echo "3. 检查模拟平台数据变化..."
curl -s http://localhost:5001/api/v1/stats | python3 -m json.tool

echo ""
echo "4. 手动触发一次监控任务..."
docker-compose exec backend python << 'EOF'
from app import create_app, db
from app.models import MonitoringRule
from app.tasks.monitor import execute_monitoring_task

app = create_app(register_blueprints=False)
with app.app_context():
    rules = MonitoringRule.query.filter_by(is_active=True).all()
    print(f"找到 {len(rules)} 个活跃规则")
    
    for rule in rules:
        print(f"执行规则: {rule.rule_name}")
        result = execute_monitoring_task.delay(rule.rule_id)
        print(f"任务ID: {result.id}")
EOF

echo ""
echo "5. 查看扫描结果..."
sleep 5
docker-compose exec backend python << 'EOF'
from app import create_app, db
from app.models import ScanResult

app = create_app(register_blueprints=False)
with app.app_context():
    results = ScanResult.query.order_by(ScanResult.scan_time.desc()).limit(5).all()
    print(f"\n最近 {len(results)} 次扫描结果:")
    for r in results:
        print(f"- 时间: {r.scan_time}, 新增: {len(r.get_jobs_new())}, 更新: {len(r.get_jobs_updated())}, 下架: {len(r.get_jobs_deleted())}")
EOF

echo ""
echo "=========================================="
echo "诊断完成！"
echo "=========================================="

