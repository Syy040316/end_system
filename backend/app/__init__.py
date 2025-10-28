"""应用工厂"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flasgger import Swagger
from config import config
import redis

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
swagger = Swagger()

# Redis连接
redis_client = None


def create_app(config_name='default', register_blueprints=True):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    # 只在需要时初始化Swagger（避免Celery中的问题）
    if register_blueprints:
        swagger.init_app(app)
    
    # 配置CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 初始化Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # 只在需要时注册蓝图
    if register_blueprints:
        from app.routes import auth, monitoring, jobs, scan_results
        app.register_blueprint(auth.bp, url_prefix='/api/v1/auth')
        app.register_blueprint(monitoring.bp, url_prefix='/api/v1/monitoring-rules')
        app.register_blueprint(jobs.bp, url_prefix='/api/v1/jobs')
        app.register_blueprint(scan_results.bp, url_prefix='/api/v1/scan-results')
        
        # 健康检查
        @app.route('/health')
        def health():
            return {'status': 'healthy'}
    
    return app

