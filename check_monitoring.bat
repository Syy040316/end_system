@echo off
chcp 65001 >nul
echo ==========================================
echo 监控系统诊断
echo ==========================================

echo.
echo 1. 检查Celery Beat是否在运行...
docker-compose logs --tail=20 celery_beat | findstr "execute_all_monitoring_tasks"

echo.
echo 2. 检查Celery Worker是否在运行...
docker-compose logs --tail=20 celery_worker | findstr "monitoring"

echo.
echo 3. 检查模拟平台数据变化...
curl -s http://localhost:5001/api/v1/stats

echo.
echo 4. 手动触发一次监控任务...
docker-compose exec -T backend python -c "from app import create_app, db; from app.models import MonitoringRule; from app.tasks.monitor import execute_monitoring_task; app = create_app(register_blueprints=False); app.app_context().push(); rules = MonitoringRule.query.filter_by(is_active=True).all(); print(f'找到 {len(rules)} 个活跃规则'); [execute_monitoring_task.delay(rule.rule_id) for rule in rules]"

echo.
echo 5. 等待5秒后查看扫描结果...
timeout /t 5 /nobreak
docker-compose exec -T backend python -c "from app import create_app, db; from app.models import ScanResult; app = create_app(register_blueprints=False); app.app_context().push(); results = ScanResult.query.order_by(ScanResult.scan_time.desc()).limit(5).all(); print(f'\n最近 {len(results)} 次扫描结果:'); [print(f'- 时间: {r.scan_time}, 新增: {len(r.get_jobs_new())}, 更新: {len(r.get_jobs_updated())}, 下架: {len(r.get_jobs_deleted())}') for r in results]"

echo.
echo ==========================================
echo 诊断完成！
echo ==========================================
pause

