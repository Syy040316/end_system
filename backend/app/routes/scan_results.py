"""扫描结果路由"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import ScanResult

bp = Blueprint('scan_results', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_scan_results():
    """
    获取扫描结果列表
    ---
    tags:
      - 扫描结果
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
      - name: rule_id
        in: query
        type: integer
    responses:
      200:
        description: 成功获取扫描结果
    """
    current_user_id = int(get_jwt_identity())  # 转回整数
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    rule_id = request.args.get('rule_id')
    
    query = ScanResult.query.filter_by(user_id=current_user_id)
    
    if rule_id:
        query = query.filter_by(rule_id=int(rule_id))
    
    # 按时间倒序
    query = query.order_by(ScanResult.scan_time.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    results = [result.to_dict() for result in pagination.items]
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'results': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        },
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/<int:result_id>', methods=['GET'])
@jwt_required()
def get_scan_result(result_id):
    """
    获取单个扫描结果详情
    ---
    tags:
      - 扫描结果
    security:
      - Bearer: []
    parameters:
      - name: result_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 成功获取扫描结果详情
    """
    current_user_id = int(get_jwt_identity())  # 转回整数
    
    result = ScanResult.query.filter_by(
        result_id=result_id,
        user_id=current_user_id
    ).first()
    
    if not result:
        return jsonify({
            'code': 404,
            'message': '扫描结果不存在',
            'data': None
        }), 404
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': result.to_dict(),
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_scan_stats():
    """
    获取扫描统计信息
    ---
    tags:
      - 扫描结果
    security:
      - Bearer: []
    responses:
      200:
        description: 成功获取统计信息
    """
    current_user_id = int(get_jwt_identity())  # 转回整数
    
    # 获取最近的扫描结果统计
    recent_results = ScanResult.query.filter_by(user_id=current_user_id)\
        .order_by(ScanResult.scan_time.desc())\
        .limit(10)\
        .all()
    
    total_new = sum(len(r.get_jobs_new()) for r in recent_results)
    total_updated = sum(len(r.get_jobs_updated()) for r in recent_results)
    total_deleted = sum(len(r.get_jobs_deleted()) for r in recent_results)
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'recent_scans': len(recent_results),
            'total_new_jobs': total_new,
            'total_updated_jobs': total_updated,
            'total_deleted_jobs': total_deleted
        },
        'timestamp': datetime.utcnow().isoformat()
    })

