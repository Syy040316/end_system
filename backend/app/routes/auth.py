"""用户认证路由"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User, UserPreference
from flasgger import swag_from

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    ---
    tags:
      - 用户认证
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: john_doe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: 注册成功
      400:
        description: 参数错误
      409:
        description: 用户已存在
    """
    data = request.get_json()
    
    # 验证必填字段
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({
            'code': 400,
            'message': '缺少必填字段',
            'data': None
        }), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'code': 409,
            'message': '用户名已存在',
            'data': None
        }), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'code': 409,
            'message': '邮箱已存在',
            'data': None
        }), 409
    
    # 创建用户
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # 创建默认用户偏好
    preference = UserPreference(
        user_id=user.user_id,
        email_address=user.email,
        email_frequency='12hourly'
    )
    preference.set_notification_types(['new', 'updated', 'deleted'])
    
    db.session.add(preference)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '注册成功',
        'data': user.to_dict(),
        'timestamp': datetime.utcnow().isoformat()
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    ---
    tags:
      - 用户认证
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: john_doe
            password:
              type: string
              example: password123
    responses:
      200:
        description: 登录成功
      401:
        description: 认证失败
    """
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'password']):
        return jsonify({
            'code': 400,
            'message': '缺少必填字段',
            'data': None
        }), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({
            'code': 401,
            'message': '用户名或密码错误',
            'data': None
        }), 401
    
    if not user.is_active:
        return jsonify({
            'code': 403,
            'message': '账户已被禁用',
            'data': None
        }), 403
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.session.commit()
    
    # 生成Token（user_id必须转为字符串）
    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))
    
    return jsonify({
        'code': 0,
        'message': '登录成功',
        'data': {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        },
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    刷新访问令牌
    ---
    tags:
      - 用户认证
    security:
      - Bearer: []
    responses:
      200:
        description: 刷新成功
    """
    current_user_id = get_jwt_identity()  # 已经是字符串
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'code': 0,
        'message': '刷新成功',
        'data': {
            'access_token': access_token
        },
        'timestamp': datetime.utcnow().isoformat()
    })


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    获取当前用户信息
    ---
    tags:
      - 用户认证
    security:
      - Bearer: []
    responses:
      200:
        description: 成功获取用户信息
    """
    current_user_id = int(get_jwt_identity())  # 转回整数
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'code': 404,
            'message': '用户不存在',
            'data': None
        }), 404
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': user.to_dict(),
        'timestamp': datetime.utcnow().isoformat()
    })

