"""数据库模型"""
from datetime import datetime
from app import db
import bcrypt
import json


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    monitoring_rules = db.relationship('MonitoringRule', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    scan_results = db.relationship('ScanResult', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password: str):
        """设置密码"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'is_active': self.is_active
        }


class MonitoringRule(db.Model):
    """监控规则表"""
    __tablename__ = 'monitoring_rules'
    
    rule_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    rule_name = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.Text)  # JSON数组
    exclude_keywords = db.Column(db.Text)  # JSON数组
    city_filter = db.Column(db.Text)  # JSON数组
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    notification_trigger = db.Column(db.String(20), default='immediately')  # immediately, hourly, daily, when_count
    notification_count = db.Column(db.Integer)  # 当触发类型为when_count时的数量
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_executed_at = db.Column(db.DateTime)
    
    # 关系
    scan_results = db.relationship('ScanResult', backref='rule', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_keywords(self):
        """获取关键词列表"""
        return json.loads(self.keywords) if self.keywords else []
    
    def set_keywords(self, keywords_list):
        """设置关键词列表"""
        self.keywords = json.dumps(keywords_list, ensure_ascii=False)
    
    def get_exclude_keywords(self):
        """获取排除关键词列表"""
        return json.loads(self.exclude_keywords) if self.exclude_keywords else []
    
    def set_exclude_keywords(self, keywords_list):
        """设置排除关键词列表"""
        self.exclude_keywords = json.dumps(keywords_list, ensure_ascii=False)
    
    def get_city_filter(self):
        """获取城市过滤列表"""
        return json.loads(self.city_filter) if self.city_filter else []
    
    def set_city_filter(self, cities_list):
        """设置城市过滤列表"""
        self.city_filter = json.dumps(cities_list, ensure_ascii=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'keywords': self.get_keywords(),
            'exclude_keywords': self.get_exclude_keywords(),
            'city_filter': self.get_city_filter(),
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'notification_trigger': self.notification_trigger,
            'notification_count': self.notification_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_executed_at': self.last_executed_at.isoformat() if self.last_executed_at else None
        }


class ScanResult(db.Model):
    """扫描结果表"""
    __tablename__ = 'scan_results'
    
    result_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('monitoring_rules.rule_id'), nullable=False, index=True)
    scan_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    jobs_new = db.Column(db.Text)  # JSON
    jobs_updated = db.Column(db.Text)  # JSON
    jobs_deleted = db.Column(db.Text)  # JSON
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_time = db.Column(db.DateTime)
    
    def get_jobs_new(self):
        """获取新增招聘列表"""
        return json.loads(self.jobs_new) if self.jobs_new else []
    
    def set_jobs_new(self, jobs_list):
        """设置新增招聘列表"""
        self.jobs_new = json.dumps(jobs_list, ensure_ascii=False)
    
    def get_jobs_updated(self):
        """获取更新招聘列表"""
        return json.loads(self.jobs_updated) if self.jobs_updated else []
    
    def set_jobs_updated(self, jobs_list):
        """设置更新招聘列表"""
        self.jobs_updated = json.dumps(jobs_list, ensure_ascii=False)
    
    def get_jobs_deleted(self):
        """获取删除招聘列表"""
        return json.loads(self.jobs_deleted) if self.jobs_deleted else []
    
    def set_jobs_deleted(self, jobs_list):
        """设置删除招聘列表"""
        self.jobs_deleted = json.dumps(jobs_list, ensure_ascii=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'result_id': self.result_id,
            'rule_id': self.rule_id,
            'scan_time': self.scan_time.isoformat() if self.scan_time else None,
            'jobs_new': self.get_jobs_new(),
            'jobs_updated': self.get_jobs_updated(),
            'jobs_deleted': self.get_jobs_deleted(),
            'email_sent': self.email_sent,
            'email_sent_time': self.email_sent_time.isoformat() if self.email_sent_time else None,
            'total_changes': len(self.get_jobs_new()) + len(self.get_jobs_updated()) + len(self.get_jobs_deleted())
        }


class UserPreference(db.Model):
    """用户偏好设置表"""
    __tablename__ = 'user_preferences'
    
    preference_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True, index=True)
    email_address = db.Column(db.String(120))  # 可与user表不同
    email_frequency = db.Column(db.String(20), default='12hourly')  # immediate, 6hourly, 12hourly, daily
    notification_types = db.Column(db.Text)  # JSON数组: ['new', 'updated', 'deleted']
    quiet_hours_start = db.Column(db.Time)
    quiet_hours_end = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_notification_types(self):
        """获取通知类型列表"""
        return json.loads(self.notification_types) if self.notification_types else ['new', 'updated', 'deleted']
    
    def set_notification_types(self, types_list):
        """设置通知类型列表"""
        self.notification_types = json.dumps(types_list, ensure_ascii=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'preference_id': self.preference_id,
            'email_address': self.email_address,
            'email_frequency': self.email_frequency,
            'notification_types': self.get_notification_types(),
            'quiet_hours_start': self.quiet_hours_start.isoformat() if self.quiet_hours_start else None,
            'quiet_hours_end': self.quiet_hours_end.isoformat() if self.quiet_hours_end else None
        }


class JobCache(db.Model):
    """招聘信息缓存表（用于变化检测）"""
    __tablename__ = 'job_cache'
    
    cache_id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('monitoring_rules.rule_id'), nullable=False, index=True)
    job_id = db.Column(db.String(100), nullable=False, index=True)
    job_data = db.Column(db.Text)  # JSON
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('rule_id', 'job_id', name='uq_rule_job'),
    )
    
    def get_job_data(self):
        """获取招聘数据"""
        return json.loads(self.job_data) if self.job_data else {}
    
    def set_job_data(self, data):
        """设置招聘数据"""
        self.job_data = json.dumps(data, ensure_ascii=False)

