"""Celery应用配置"""
from celery import Celery
from celery.schedules import crontab
import os

# 创建Celery应用
celery = Celery(
    'job_monitor',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['app.tasks.monitor', 'app.tasks.email']
)

# 配置
celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5分钟超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 定时任务配置
celery.conf.beat_schedule = {
    # 每30分钟执行一次监控任务
    'execute-all-monitoring-tasks': {
        'task': 'app.tasks.monitor.execute_all_monitoring_tasks',
        'schedule': crontab(minute='*/30'),
    },
}

