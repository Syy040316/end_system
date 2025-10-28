"""邮件发送任务"""
from app.celery_app import celery
from app import create_app, db, mail
from app.models import ScanResult, User, UserPreference, MonitoringRule
from flask_mail import Message
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery.task(bind=True, name='app.tasks.email.send_monitoring_notification')
def send_monitoring_notification(self, result_id):
    """发送监控通知邮件"""
    app = create_app(register_blueprints=False)
    
    with app.app_context():
        result = ScanResult.query.get(result_id)
        
        if not result:
            logger.error(f"扫描结果不存在: {result_id}")
            return {'error': 'Result not found'}
        
        user = User.query.get(result.user_id)
        rule = MonitoringRule.query.get(result.rule_id)
        preference = UserPreference.query.filter_by(user_id=result.user_id).first()
        
        if not user or not rule:
            logger.error(f"用户或规则不存在: user_id={result.user_id}, rule_id={result.rule_id}")
            return {'error': 'User or rule not found'}
        
        # 获取收件人邮箱
        recipient = preference.email_address if preference and preference.email_address else user.email
        
        # 构建邮件内容
        subject, body = build_email_content(user, rule, result)
        
        try:
            # 发送邮件
            msg = Message(
                subject=subject,
                recipients=[recipient],
                html=body
            )
            
            mail.send(msg)
            
            # 更新发送状态
            result.email_sent = True
            result.email_sent_time = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"邮件发送成功: result_id={result_id}, recipient={recipient}")
            
            return {
                'result_id': result_id,
                'recipient': recipient,
                'sent_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            raise


def build_email_content(user: User, rule: MonitoringRule, result: ScanResult):
    """构建邮件内容"""
    jobs_new = result.get_jobs_new()
    jobs_updated = result.get_jobs_updated()
    jobs_deleted = result.get_jobs_deleted()
    
    total_changes = len(jobs_new) + len(jobs_updated) + len(jobs_deleted)
    
    # 邮件标题
    subject = f"[招聘监控通知] 你感兴趣的岗位有{total_changes}条更新"
    
    # 邮件正文（HTML格式）
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px 10px 0 0;
                text-align: center;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .section {{
                background: white;
                margin: 20px 0;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 15px;
                color: #667eea;
            }}
            .job-item {{
                border-left: 4px solid #667eea;
                padding-left: 15px;
                margin: 15px 0;
            }}
            .job-title {{
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }}
            .job-info {{
                color: #666;
                margin: 5px 0;
            }}
            .badge {{
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                margin: 0 3px;
            }}
            .badge-new {{
                background: #10b981;
                color: white;
            }}
            .badge-updated {{
                background: #f59e0b;
                color: white;
            }}
            .badge-deleted {{
                background: #ef4444;
                color: white;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                color: #999;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📧 招聘信息监控通知</h1>
            <p>监控规则：{rule.rule_name}</p>
        </div>
        
        <div class="content">
            <p>亲爱的 <strong>{user.username}</strong>，</p>
            <p>您关注的岗位有以下更新：</p>
    """
    
    # 新增招聘
    if jobs_new:
        body += f"""
            <div class="section">
                <div class="section-title">
                    <span class="badge badge-new">新增</span> {len(jobs_new)} 条
                </div>
        """
        
        for job in jobs_new[:10]:  # 最多显示10条
            body += f"""
                <div class="job-item">
                    <div class="job-title">{job['company']} | {job['position']}</div>
                    <div class="job-info">💰 薪资: {job['salary_min']}K - {job['salary_max']}K</div>
                    <div class="job-info">📍 地点: {job['location']}</div>
                    <div class="job-info">🛠 技能: {', '.join(job['skills'][:5])}</div>
                </div>
            """
        
        if len(jobs_new) > 10:
            body += f"<p>... 还有 {len(jobs_new) - 10} 条新增</p>"
        
        body += "</div>"
    
    # 更新招聘
    if jobs_updated:
        body += f"""
            <div class="section">
                <div class="section-title">
                    <span class="badge badge-updated">更新</span> {len(jobs_updated)} 条
                </div>
        """
        
        for job in jobs_updated[:10]:
            body += f"""
                <div class="job-item">
                    <div class="job-title">{job['company']} | {job['position']}</div>
                    <div class="job-info">💰 薪资: {job['salary_min']}K - {job['salary_max']}K</div>
                    <div class="job-info">📍 地点: {job['location']}</div>
                </div>
            """
        
        if len(jobs_updated) > 10:
            body += f"<p>... 还有 {len(jobs_updated) - 10} 条更新</p>"
        
        body += "</div>"
    
    # 下架招聘
    if jobs_deleted:
        body += f"""
            <div class="section">
                <div class="section-title">
                    <span class="badge badge-deleted">下架</span> {len(jobs_deleted)} 条
                </div>
        """
        
        for job in jobs_deleted[:10]:
            body += f"""
                <div class="job-item">
                    <div class="job-title">{job['company']} | {job['position']}</div>
                </div>
            """
        
        if len(jobs_deleted) > 10:
            body += f"<p>... 还有 {len(jobs_deleted) - 10} 条下架</p>"
        
        body += "</div>"
    
    body += f"""
            <div class="footer">
                <p>此邮件由招聘信息监控系统自动发送</p>
                <p>扫描时间: {result.scan_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, body

