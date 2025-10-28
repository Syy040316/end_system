"""监控任务"""
from app.celery_app import celery
from app import create_app, db
from app.models import MonitoringRule, ScanResult, JobCache
from datetime import datetime
import requests
import os
import logging

logger = logging.getLogger(__name__)

MOCK_PLATFORM_URL = os.getenv('MOCK_PLATFORM_URL', 'http://localhost:5001')


@celery.task(bind=True, name='app.tasks.monitor.execute_all_monitoring_tasks')
def execute_all_monitoring_tasks(self):
    """执行所有活跃的监控任务"""
    app = create_app(register_blueprints=False)
    
    with app.app_context():
        # 获取所有活跃的监控规则
        rules = MonitoringRule.query.filter_by(is_active=True).all()
        
        logger.info(f"开始执行 {len(rules)} 个监控任务")
        
        for rule in rules:
            try:
                execute_monitoring_task.delay(rule.rule_id)
            except Exception as e:
                logger.error(f"提交监控任务失败 rule_id={rule.rule_id}: {e}")
        
        return {
            'executed_count': len(rules),
            'timestamp': datetime.utcnow().isoformat()
        }


@celery.task(bind=True, name='app.tasks.monitor.execute_monitoring_task')
def execute_monitoring_task(self, rule_id):
    """执行单个监控任务"""
    app = create_app(register_blueprints=False)
    
    with app.app_context():
        rule = MonitoringRule.query.get(rule_id)
        
        if not rule:
            logger.error(f"监控规则不存在: {rule_id}")
            return {'error': 'Rule not found'}
        
        logger.info(f"开始执行监控任务: rule_id={rule_id}, rule_name={rule.rule_name}")
        
        try:
            # 1. 从模拟平台获取招聘信息
            jobs = fetch_jobs_from_platform(rule)
            
            # 2. 获取上次的缓存数据
            cached_jobs = get_cached_jobs(rule_id)
            
            # 3. 检测变化
            changes = detect_changes(jobs, cached_jobs)
            
            # 4. 更新缓存
            update_job_cache(rule_id, jobs)
            
            # 5. 保存扫描结果
            result = save_scan_result(rule, changes)
            
            # 6. 更新规则执行时间
            rule.last_executed_at = datetime.utcnow()
            db.session.commit()
            
            # 7. 触发邮件通知
            if should_send_notification(rule, changes):
                from app.tasks.email import send_monitoring_notification
                send_monitoring_notification.delay(result.result_id)
            
            logger.info(f"监控任务完成: rule_id={rule_id}, 新增={len(changes['new'])}, "
                       f"更新={len(changes['updated'])}, 下架={len(changes['deleted'])}")
            
            return {
                'rule_id': rule_id,
                'result_id': result.result_id,
                'changes': {
                    'new': len(changes['new']),
                    'updated': len(changes['updated']),
                    'deleted': len(changes['deleted'])
                }
            }
            
        except Exception as e:
            logger.error(f"执行监控任务失败 rule_id={rule_id}: {e}")
            raise


def fetch_jobs_from_platform(rule: MonitoringRule):
    """从模拟平台获取招聘信息"""
    keywords = rule.get_keywords()
    cities = rule.get_city_filter()
    
    params = {
        'keyword': ','.join(keywords) if keywords else '',
        'city': cities[0] if cities else None,
        'salary_min': rule.salary_min or 0,
        'salary_max': rule.salary_max or 999999
    }
    
    try:
        response = requests.get(
            f'{MOCK_PLATFORM_URL}/api/v1/jobs/search',
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') == 0:
            return data['data']['jobs']
        else:
            logger.error(f"平台返回错误: {data.get('message')}")
            return []
            
    except requests.RequestException as e:
        logger.error(f"请求模拟平台失败: {e}")
        return []


def get_cached_jobs(rule_id: int):
    """获取缓存的招聘信息"""
    cached = JobCache.query.filter_by(rule_id=rule_id).all()
    return {cache.job_id: cache.get_job_data() for cache in cached}


def detect_changes(current_jobs, cached_jobs):
    """检测招聘信息变化"""
    current_ids = {job['id']: job for job in current_jobs}
    cached_ids = set(cached_jobs.keys())
    current_id_set = set(current_ids.keys())
    
    # 新增检测
    new_ids = current_id_set - cached_ids
    new_jobs = [current_ids[job_id] for job_id in new_ids]
    
    # 下架检测
    deleted_ids = cached_ids - current_id_set
    deleted_jobs = [
        {'id': job_id, **cached_jobs[job_id]}
        for job_id in deleted_ids
    ]
    
    # 更新检测
    updated_jobs = []
    common_ids = current_id_set & cached_ids
    
    for job_id in common_ids:
        current = current_ids[job_id]
        cached = cached_jobs[job_id]
        
        # 检查关键字段是否变化
        if has_job_changed(current, cached):
            updated_jobs.append({
                'id': job_id,
                'current': current,
                'previous': cached,
                'changes': get_job_changes(current, cached)
            })
    
    return {
        'new': new_jobs,
        'updated': updated_jobs,
        'deleted': deleted_jobs
    }


def has_job_changed(current, cached):
    """判断招聘信息是否有变化"""
    key_fields = ['salary_min', 'salary_max', 'job_description', 'status', 'experience_required']
    
    for field in key_fields:
        if current.get(field) != cached.get(field):
            return True
    
    return False


def get_job_changes(current, cached):
    """获取具体的变化内容"""
    changes = {}
    key_fields = ['salary_min', 'salary_max', 'job_description', 'status', 'experience_required']
    
    for field in key_fields:
        if current.get(field) != cached.get(field):
            changes[field] = {
                'old': cached.get(field),
                'new': current.get(field)
            }
    
    return changes


def update_job_cache(rule_id: int, jobs):
    """更新招聘缓存"""
    # 删除旧缓存
    JobCache.query.filter_by(rule_id=rule_id).delete()
    
    # 添加新缓存
    for job in jobs:
        cache = JobCache(rule_id=rule_id, job_id=job['id'])
        cache.set_job_data(job)
        db.session.add(cache)
    
    db.session.commit()


def save_scan_result(rule: MonitoringRule, changes):
    """保存扫描结果"""
    result = ScanResult(
        user_id=rule.user_id,
        rule_id=rule.rule_id
    )
    
    result.set_jobs_new(changes['new'])
    result.set_jobs_updated([u['current'] for u in changes['updated']])
    result.set_jobs_deleted(changes['deleted'])
    
    db.session.add(result)
    db.session.commit()
    
    return result


def should_send_notification(rule: MonitoringRule, changes):
    """判断是否应该发送通知"""
    total_changes = len(changes['new']) + len(changes['updated']) + len(changes['deleted'])
    
    if total_changes == 0:
        return False
    
    trigger = rule.notification_trigger
    
    if trigger == 'immediately':
        return True
    
    if trigger == 'when_count':
        return total_changes >= (rule.notification_count or 5)
    
    # hourly, daily等可以根据last_executed_at判断
    # 这里简化处理，直接返回True
    return True

