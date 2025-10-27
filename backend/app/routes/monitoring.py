"""监控规则路由"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import MonitoringRule
from app.tasks.monitor import execute_monitoring_task

bp = Blueprint('monitoring', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_monitoring_rules():
    """
    获取用户的所有监控规则
    ---
    tags:
      - 监控规则
    security:
      - Bearer: []
    responses:
      200:
        description: 成功获取规则列表
    """
    current_user_id = get_jwt_identity()
    
    rules = MonitoringRule.query.filter_by(user_id=current_user_id).all()
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'rules': [rule.to_dict() for rule in rules],
            'count': len(rules)
        },
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('', methods=['POST'])
@jwt_required()
def create_monitoring_rule():
    """
    创建新的监控规则
    ---
    tags:
      - 监控规则
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - rule_name
            - keywords
          properties:
            rule_name:
              type: string
              example: Python后端岗位监控
            keywords:
              type: array
              items:
                type: string
              example: ["Python", "后端", "Django"]
            exclude_keywords:
              type: array
              items:
                type: string
              example: ["实习"]
            city_filter:
              type: array
              items:
                type: string
              example: ["北京", "上海"]
            salary_min:
              type: integer
              example: 15000
            salary_max:
              type: integer
              example: 30000
            notification_trigger:
              type: string
              example: immediately
            notification_count:
              type: integer
              example: 5
    responses:
      201:
        description: 创建成功
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('rule_name') or not data.get('keywords'):
        return jsonify({
            'code': 400,
            'message': '缺少必填字段',
            'data': None
        }), 400
    
    rule = MonitoringRule(
        user_id=current_user_id,
        rule_name=data['rule_name'],
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        notification_trigger=data.get('notification_trigger', 'immediately'),
        notification_count=data.get('notification_count'),
        is_active=data.get('is_active', True)
    )
    
    rule.set_keywords(data['keywords'])
    
    if data.get('exclude_keywords'):
        rule.set_exclude_keywords(data['exclude_keywords'])
    
    if data.get('city_filter'):
        rule.set_city_filter(data['city_filter'])
    
    db.session.add(rule)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': rule.to_dict(),
        'timestamp': datetime.utcnow().isoformat()
    }), 201


@bp.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_monitoring_rule(rule_id):
    """
    获取指定监控规则
    ---
    tags:
      - 监控规则
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 成功获取规则
      404:
        description: 规则不存在
    """
    current_user_id = get_jwt_identity()
    
    rule = MonitoringRule.query.filter_by(
        rule_id=rule_id,
        user_id=current_user_id
    ).first()
    
    if not rule:
        return jsonify({
            'code': 404,
            'message': '规则不存在',
            'data': None
        }), 404
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': rule.to_dict(),
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/<int:rule_id>', methods=['PATCH'])
@jwt_required()
def update_monitoring_rule(rule_id):
    """
    更新监控规则
    ---
    tags:
      - 监控规则
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
    responses:
      200:
        description: 更新成功
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    rule = MonitoringRule.query.filter_by(
        rule_id=rule_id,
        user_id=current_user_id
    ).first()
    
    if not rule:
        return jsonify({
            'code': 404,
            'message': '规则不存在',
            'data': None
        }), 404
    
    # 更新字段
    if 'rule_name' in data:
        rule.rule_name = data['rule_name']
    if 'keywords' in data:
        rule.set_keywords(data['keywords'])
    if 'exclude_keywords' in data:
        rule.set_exclude_keywords(data['exclude_keywords'])
    if 'city_filter' in data:
        rule.set_city_filter(data['city_filter'])
    if 'salary_min' in data:
        rule.salary_min = data['salary_min']
    if 'salary_max' in data:
        rule.salary_max = data['salary_max']
    if 'notification_trigger' in data:
        rule.notification_trigger = data['notification_trigger']
    if 'notification_count' in data:
        rule.notification_count = data['notification_count']
    if 'is_active' in data:
        rule.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '更新成功',
        'data': rule.to_dict(),
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_monitoring_rule(rule_id):
    """
    删除监控规则
    ---
    tags:
      - 监控规则
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 删除成功
    """
    current_user_id = get_jwt_identity()
    
    rule = MonitoringRule.query.filter_by(
        rule_id=rule_id,
        user_id=current_user_id
    ).first()
    
    if not rule:
        return jsonify({
            'code': 404,
            'message': '规则不存在',
            'data': None
        }), 404
    
    db.session.delete(rule)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '删除成功',
        'data': None,
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/<int:rule_id>/test', methods=['POST'])
@jwt_required()
def test_monitoring_rule(rule_id):
    """
    测试监控规则（手动触发一次）
    ---
    tags:
      - 监控规则
    security:
      - Bearer: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 测试任务已提交
    """
    current_user_id = get_jwt_identity()
    
    rule = MonitoringRule.query.filter_by(
        rule_id=rule_id,
        user_id=current_user_id
    ).first()
    
    if not rule:
        return jsonify({
            'code': 404,
            'message': '规则不存在',
            'data': None
        }), 404
    
    # 异步执行监控任务
    task = execute_monitoring_task.delay(rule_id)
    
    return jsonify({
        'code': 0,
        'message': '测试任务已提交',
        'data': {
            'task_id': task.id
        },
        'timestamp': datetime.utcnow().isoformat()
    })

