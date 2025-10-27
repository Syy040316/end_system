"""
模拟招聘平台 - 主应用
提供RESTful API接口，定时生成和更新招聘信息
"""
from flask import Flask, jsonify, request
from datetime import datetime
from .data_generator import JobDataGenerator
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)

# 初始化数据生成器
job_generator = JobDataGenerator()

# 初始化数据（500+条招聘信息）
job_generator.initialize_jobs(count=500)


def update_jobs_task():
    """定时更新任务：随机修改招聘信息"""
    job_generator.random_update_jobs()
    print(f"[{datetime.now()}] 执行定时更新任务")


def add_new_jobs_task():
    """定时新增任务：添加新招聘信息"""
    job_generator.add_new_jobs(count=5)
    print(f"[{datetime.now()}] 执行新增任务，新增5条")


# 配置定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_jobs_task, trigger="interval", minutes=10, id='update_jobs')
scheduler.add_job(func=add_new_jobs_task, trigger="interval", minutes=25, id='add_new_jobs')
scheduler.start()

# 确保应用退出时关闭调度器
atexit.register(lambda: scheduler.shutdown())


@app.route('/api/v1/jobs', methods=['GET'])
def get_jobs():
    """
    获取招聘列表（支持分页和过滤）
    
    Query参数:
    - page: 页码（默认1）
    - per_page: 每页数量（默认20）
    - status: 状态过滤（active/inactive）
    - city: 城市过滤
    - keyword: 关键词搜索（岗位或技能）
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    status = request.args.get('status', 'active')
    city = request.args.get('city')
    keyword = request.args.get('keyword')
    
    jobs = job_generator.get_jobs(
        page=page,
        per_page=per_page,
        status=status,
        city=city,
        keyword=keyword
    )
    
    total = job_generator.count_jobs(status=status, city=city, keyword=keyword)
    
    return jsonify({
        "code": 0,
        "message": "success",
        "data": {
            "jobs": jobs,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/jobs/<job_id>', methods=['GET'])
def get_job_detail(job_id):
    """获取单条招聘详情"""
    job = job_generator.get_job_by_id(job_id)
    
    if not job:
        return jsonify({
            "code": 404,
            "message": "Job not found",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 0,
        "message": "success",
        "data": job,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/jobs/search', methods=['GET'])
def search_jobs():
    """
    搜索招聘信息
    
    Query参数:
    - keyword: 关键词（岗位名称或技能）
    - skills: 技能列表（逗号分隔）
    - city: 城市
    - salary_min: 最低薪资
    - salary_max: 最高薪资
    """
    keyword = request.args.get('keyword', '')
    skills = request.args.get('skills', '').split(',') if request.args.get('skills') else None
    city = request.args.get('city')
    salary_min = int(request.args.get('salary_min', 0))
    salary_max = int(request.args.get('salary_max', 999999))
    
    jobs = job_generator.search_jobs(
        keyword=keyword,
        skills=skills,
        city=city,
        salary_min=salary_min,
        salary_max=salary_max
    )
    
    return jsonify({
        "code": 0,
        "message": "success",
        "data": {
            "jobs": jobs,
            "count": len(jobs)
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/jobs/updates', methods=['GET'])
def get_updates():
    """
    获取指定时间后的更新
    
    Query参数:
    - since: ISO格式时间戳
    """
    since_str = request.args.get('since')
    
    if not since_str:
        return jsonify({
            "code": 400,
            "message": "Missing 'since' parameter",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    try:
        since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({
            "code": 400,
            "message": "Invalid datetime format",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    updates = job_generator.get_updates_since(since)
    
    return jsonify({
        "code": 0,
        "message": "success",
        "data": updates,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """获取平台统计信息"""
    stats = job_generator.get_statistics()
    
    return jsonify({
        "code": 0,
        "message": "success",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

