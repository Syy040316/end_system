"""
第三方数据推送接口
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Job

bp = Blueprint('push', __name__, url_prefix='/api/v1/jobs/push')


@bp.route('', methods=['POST'])
@jwt_required()
def push_single_job():
    """推送单个职位"""
    current_user_id = int(get_jwt_identity())
    
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['job_id', 'company', 'position', 'skills', 'location', 'salary_min', 'salary_max']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}',
                    'data': None
                }), 400
        
        # 检查job_id是否已存在
        existing_job = Job.query.filter_by(job_id=data['job_id']).first()
        
        if existing_job:
            # 更新现有职位
            existing_job.company = data.get('company', existing_job.company)
            existing_job.position = data.get('position', existing_job.position)
            existing_job.description = data.get('description', existing_job.description)
            existing_job.requirements = data.get('requirements', existing_job.requirements)
            existing_job.skills = data.get('skills', existing_job.skills)
            existing_job.location = data.get('location', existing_job.location)
            existing_job.salary_min = data.get('salary_min', existing_job.salary_min)
            existing_job.salary_max = data.get('salary_max', existing_job.salary_max)
            existing_job.status = data.get('status', existing_job.status)
            existing_job.update_date = datetime.fromisoformat(data['update_date'].replace('Z', '+00:00')) if 'update_date' in data else datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'code': 0,
                'message': '职位更新成功',
                'data': {
                    'job_id': existing_job.job_id,
                    'created': False
                },
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            # 创建新职位
            new_job = Job(
                job_id=data['job_id'],
                company=data['company'],
                position=data['position'],
                description=data.get('description', ''),
                requirements=data.get('requirements', ''),
                skills=data['skills'],
                location=data['location'],
                salary_min=data['salary_min'],
                salary_max=data['salary_max'],
                status=data.get('status', 'active'),
                publish_date=datetime.fromisoformat(data['publish_date'].replace('Z', '+00:00')) if 'publish_date' in data else datetime.utcnow(),
                update_date=datetime.fromisoformat(data['update_date'].replace('Z', '+00:00')) if 'update_date' in data else datetime.utcnow()
            )
            
            db.session.add(new_job)
            db.session.commit()
            
            return jsonify({
                'code': 0,
                'message': '职位推送成功',
                'data': {
                    'job_id': new_job.job_id,
                    'created': True
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'推送失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/batch', methods=['POST'])
@jwt_required()
def push_batch_jobs():
    """批量推送职位"""
    current_user_id = int(get_jwt_identity())
    
    try:
        data = request.get_json()
        
        if 'jobs' not in data or not isinstance(data['jobs'], list):
            return jsonify({
                'code': 400,
                'message': '请提供jobs数组',
                'data': None
            }), 400
        
        jobs_list = data['jobs']
        
        # 限制批量数量
        if len(jobs_list) > 100:
            return jsonify({
                'code': 400,
                'message': '单次批量推送最多支持100条',
                'data': None
            }), 400
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for job_data in jobs_list:
            try:
                # 验证必填字段
                required_fields = ['job_id', 'company', 'position', 'skills', 'location', 'salary_min', 'salary_max']
                missing_fields = [field for field in required_fields if field not in job_data]
                
                if missing_fields:
                    errors.append({
                        'job_id': job_data.get('job_id', 'unknown'),
                        'error': f'缺少必填字段: {", ".join(missing_fields)}'
                    })
                    failed_count += 1
                    continue
                
                # 检查是否存在
                existing_job = Job.query.filter_by(job_id=job_data['job_id']).first()
                
                if existing_job:
                    # 更新
                    existing_job.company = job_data.get('company', existing_job.company)
                    existing_job.position = job_data.get('position', existing_job.position)
                    existing_job.description = job_data.get('description', existing_job.description)
                    existing_job.requirements = job_data.get('requirements', existing_job.requirements)
                    existing_job.skills = job_data.get('skills', existing_job.skills)
                    existing_job.location = job_data.get('location', existing_job.location)
                    existing_job.salary_min = job_data.get('salary_min', existing_job.salary_min)
                    existing_job.salary_max = job_data.get('salary_max', existing_job.salary_max)
                    existing_job.status = job_data.get('status', existing_job.status)
                    existing_job.update_date = datetime.utcnow()
                else:
                    # 创建
                    new_job = Job(
                        job_id=job_data['job_id'],
                        company=job_data['company'],
                        position=job_data['position'],
                        description=job_data.get('description', ''),
                        requirements=job_data.get('requirements', ''),
                        skills=job_data['skills'],
                        location=job_data['location'],
                        salary_min=job_data['salary_min'],
                        salary_max=job_data['salary_max'],
                        status=job_data.get('status', 'active'),
                        publish_date=datetime.utcnow(),
                        update_date=datetime.utcnow()
                    )
                    db.session.add(new_job)
                
                success_count += 1
                
            except Exception as e:
                errors.append({
                    'job_id': job_data.get('job_id', 'unknown'),
                    'error': str(e)
                })
                failed_count += 1
        
        # 提交所有成功的
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': '批量推送完成',
            'data': {
                'success_count': success_count,
                'failed_count': failed_count,
                'total': len(jobs_list),
                'errors': errors if errors else None
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'批量推送失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/<job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """更新职位信息"""
    current_user_id = int(get_jwt_identity())
    
    try:
        job = Job.query.filter_by(job_id=job_id).first()
        
        if not job:
            return jsonify({
                'code': 404,
                'message': '职位不存在',
                'data': None
            }), 404
        
        data = request.get_json()
        
        # 更新允许的字段
        updatable_fields = ['company', 'position', 'description', 'requirements', 
                           'skills', 'location', 'salary_min', 'salary_max', 'status']
        
        for field in updatable_fields:
            if field in data:
                setattr(job, field, data[field])
        
        job.update_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': '职位更新成功',
            'data': job.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}',
            'data': None
        }), 500


@bp.route('/<job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """下架职位"""
    current_user_id = int(get_jwt_identity())
    
    try:
        job = Job.query.filter_by(job_id=job_id).first()
        
        if not job:
            return jsonify({
                'code': 404,
                'message': '职位不存在',
                'data': None
            }), 404
        
        # 软删除：标记为inactive
        job.status = 'inactive'
        job.update_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': '职位已下架',
            'data': None,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'下架失败: {str(e)}',
            'data': None
        }), 500

