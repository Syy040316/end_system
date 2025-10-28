#!/bin/bash

echo "=========================================="
echo "监控系统诊断工具"
echo "=========================================="
echo ""

echo "📊 1. 检查所有服务状态..."
echo "----------------------------------------"
docker-compose ps
echo ""

echo "⏰ 2. 检查Celery Beat（定时任务调度器）..."
echo "----------------------------------------"
beat_logs=$(docker-compose logs --tail=20 celery_beat 2>/dev/null)
if echo "$beat_logs" | grep -q "Scheduler"; then
    echo "✓ Celery Beat 正在运行"
    echo "$beat_logs" | grep "execute_all_monitoring_tasks" | tail -3
else
    echo "✗ Celery Beat 可能未正常运行"
    echo "最近日志："
    echo "$beat_logs" | tail -5
fi
echo ""

echo "🔄 3. 检查Celery Worker（任务执行器）..."
echo "----------------------------------------"
worker_logs=$(docker-compose logs --tail=20 celery_worker 2>/dev/null)
if echo "$worker_logs" | grep -q "ready"; then
    echo "✓ Celery Worker 正在运行"
else
    echo "✗ Celery Worker 可能未正常运行"
fi
echo "$worker_logs" | grep -i "monitoring" | tail -3
echo ""

echo "📡 4. 检查模拟平台数据..."
echo "----------------------------------------"
platform_stats=$(curl -s http://localhost:5001/api/v1/stats 2>/dev/null)
if [ -n "$platform_stats" ]; then
    echo "✓ 模拟平台正常运行"
    echo "$platform_stats" | python3 -m json.tool 2>/dev/null || echo "$platform_stats"
else
    echo "✗ 无法连接到模拟平台"
fi
echo ""

echo "🔍 5. 检查数据库连接..."
echo "----------------------------------------"
db_status=$(docker-compose exec -T postgres pg_isready -U admin -d job_monitor 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✓ 数据库连接正常"
else
    echo "✗ 数据库连接失败"
fi
echo ""

echo "📋 6. 查看监控规则..."
echo "----------------------------------------"
docker-compose exec -T backend python << 'EOF'
from app import create_app, db
from app.models import MonitoringRule

app = create_app(register_blueprints=False)
with app.app_context():
    rules = MonitoringRule.query.all()
    active_rules = [r for r in rules if r.is_active]
    print(f"总规则数: {len(rules)}")
    print(f"活跃规则: {len(active_rules)}")
    print("")
    if active_rules:
        print("活跃规则列表:")
        for r in active_rules:
            print(f"  - [{r.rule_id}] {r.rule_name}")
    else:
        print("⚠️  没有活跃的监控规则！")
        print("   请登录系统创建监控规则。")
EOF
echo ""

echo "🚀 7. 手动触发监控任务（测试）..."
echo "----------------------------------------"
docker-compose exec -T backend python << 'EOF'
from app import create_app, db
from app.models import MonitoringRule
from app.tasks.monitor import execute_monitoring_task

app = create_app(register_blueprints=False)
with app.app_context():
    rules = MonitoringRule.query.filter_by(is_active=True).all()
    
    if len(rules) == 0:
        print("⚠️  没有活跃的监控规则，无法触发任务")
        print("   请先登录系统创建监控规则")
    else:
        print(f"找到 {len(rules)} 个活跃规则，开始触发...")
        for rule in rules:
            print(f"  触发规则: {rule.rule_name}")
            try:
                result = execute_monitoring_task.delay(rule.rule_id)
                print(f"  ✓ 任务已提交，ID: {result.id}")
            except Exception as e:
                print(f"  ✗ 触发失败: {e}")
EOF
echo ""

echo "⏳ 等待5秒让任务执行..."
sleep 5
echo ""

echo "📊 8. 查看扫描结果..."
echo "----------------------------------------"
docker-compose exec -T backend python << 'EOF'
from app import create_app, db
from app.models import ScanResult

app = create_app(register_blueprints=False)
with app.app_context():
    results = ScanResult.query.order_by(ScanResult.scan_time.desc()).limit(10).all()
    
    if len(results) == 0:
        print("⚠️  暂无扫描结果")
        print("   可能原因：")
        print("   1. 监控规则刚创建，还未执行")
        print("   2. Celery Beat 调度间隔未到")
        print("   3. 监控条件太严格，没有匹配到职位")
    else:
        print(f"最近 {len(results)} 次扫描结果:")
        print("")
        for i, r in enumerate(results, 1):
            new_count = len(r.get_jobs_new())
            updated_count = len(r.get_jobs_updated())
            deleted_count = len(r.get_jobs_deleted())
            total = new_count + updated_count + deleted_count
            
            print(f"{i}. 时间: {r.scan_time}")
            print(f"   规则ID: {r.rule_id}")
            print(f"   变化: 新增 {new_count} | 更新 {updated_count} | 下架 {deleted_count} | 总计 {total}")
            print(f"   邮件: {'已发送' if r.email_sent else '未发送'}")
            print("")
EOF
echo ""

echo "=========================================="
echo "✓ 诊断完成！"
echo "=========================================="
echo ""
echo "💡 提示："
echo "  - 如果没有扫描结果，请确保已创建监控规则"
echo "  - 查看完整日志: docker-compose logs -f"
echo "  - 访问前端: http://localhost:8080"
echo "  - 测试推送API: python3 test_push_api.py"
echo ""

