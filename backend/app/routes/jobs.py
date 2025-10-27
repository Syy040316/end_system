"""招聘信息路由"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import requests
import os

bp = Blueprint('jobs', __name__)

MOCK_PLATFORM_URL = os.getenv('MOCK_PLATFORM_URL', 'http://localhost:5001')


@bp.route('', methods=['GET'])
@jwt_required()
def get_jobs():
    """
    获取招聘列表
    ---
    tags:
      - 招聘信息
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
      - name: status
        in: query
        type: string
        default: active
      - name: city
        in: query
        type: string
      - name: keyword
        in: query
        type: string
    responses:
      200:
        description: 成功获取招聘列表
    """
    params = {
        'page': request.args.get('page', 1),
        'per_page': request.args.get('per_page', 20),
        'status': request.args.get('status', 'active'),
        'city': request.args.get('city'),
        'keyword': request.args.get('keyword')
    }
    
    try:
        response = requests.get(f'{MOCK_PLATFORM_URL}/api/v1/jobs', params=params, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({
            'code': 500,
            'message': f'无法连接到招聘平台: {str(e)}',
            'data': None,
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@bp.route('/<job_id>', methods=['GET'])
@jwt_required()
def get_job_detail(job_id):
    """
    获取招聘详情
    ---
    tags:
      - 招聘信息
    security:
      - Bearer: []
    parameters:
      - name: job_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 成功获取招聘详情
    """
    try:
        response = requests.get(f'{MOCK_PLATFORM_URL}/api/v1/jobs/{job_id}', timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({
            'code': 500,
            'message': f'无法连接到招聘平台: {str(e)}',
            'data': None,
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@bp.route('/search', methods=['GET'])
@jwt_required()
def search_jobs():
    """
    搜索招聘信息
    ---
    tags:
      - 招聘信息
    security:
      - Bearer: []
    parameters:
      - name: keyword
        in: query
        type: string
      - name: skills
        in: query
        type: string
      - name: city
        in: query
        type: string
      - name: salary_min
        in: query
        type: integer
      - name: salary_max
        in: query
        type: integer
    responses:
      200:
        description: 成功搜索招聘信息
    """
    params = {
        'keyword': request.args.get('keyword', ''),
        'skills': request.args.get('skills', ''),
        'city': request.args.get('city'),
        'salary_min': request.args.get('salary_min', 0),
        'salary_max': request.args.get('salary_max', 999999)
    }
    
    try:
        response = requests.get(f'{MOCK_PLATFORM_URL}/api/v1/jobs/search', params=params, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({
            'code': 500,
            'message': f'无法连接到招聘平台: {str(e)}',
            'data': None,
            'timestamp': datetime.utcnow().isoformat()
        }), 500

