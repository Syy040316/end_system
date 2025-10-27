"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建用户表
    op.create_table('users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 创建监控规则表
    op.create_table('monitoring_rules',
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rule_name', sa.String(length=100), nullable=False),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('exclude_keywords', sa.Text(), nullable=True),
        sa.Column('city_filter', sa.Text(), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('notification_trigger', sa.String(length=20), nullable=True),
        sa.Column('notification_count', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_executed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('rule_id')
    )
    op.create_index(op.f('ix_monitoring_rules_user_id'), 'monitoring_rules', ['user_id'], unique=False)
    op.create_index(op.f('ix_monitoring_rules_is_active'), 'monitoring_rules', ['is_active'], unique=False)

    # 创建扫描结果表
    op.create_table('scan_results',
        sa.Column('result_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('scan_time', sa.DateTime(), nullable=True),
        sa.Column('jobs_new', sa.Text(), nullable=True),
        sa.Column('jobs_updated', sa.Text(), nullable=True),
        sa.Column('jobs_deleted', sa.Text(), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=True),
        sa.Column('email_sent_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['rule_id'], ['monitoring_rules.rule_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('result_id')
    )
    op.create_index(op.f('ix_scan_results_user_id'), 'scan_results', ['user_id'], unique=False)
    op.create_index(op.f('ix_scan_results_rule_id'), 'scan_results', ['rule_id'], unique=False)
    op.create_index(op.f('ix_scan_results_scan_time'), 'scan_results', ['scan_time'], unique=False)

    # 创建用户偏好表
    op.create_table('user_preferences',
        sa.Column('preference_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email_address', sa.String(length=120), nullable=True),
        sa.Column('email_frequency', sa.String(length=20), nullable=True),
        sa.Column('notification_types', sa.Text(), nullable=True),
        sa.Column('quiet_hours_start', sa.Time(), nullable=True),
        sa.Column('quiet_hours_end', sa.Time(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('preference_id')
    )
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=True)

    # 创建招聘缓存表
    op.create_table('job_cache',
        sa.Column('cache_id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=100), nullable=False),
        sa.Column('job_data', sa.Text(), nullable=True),
        sa.Column('cached_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['rule_id'], ['monitoring_rules.rule_id'], ),
        sa.PrimaryKeyConstraint('cache_id'),
        sa.UniqueConstraint('rule_id', 'job_id', name='uq_rule_job')
    )
    op.create_index(op.f('ix_job_cache_rule_id'), 'job_cache', ['rule_id'], unique=False)
    op.create_index(op.f('ix_job_cache_job_id'), 'job_cache', ['job_id'], unique=False)


def downgrade():
    op.drop_table('job_cache')
    op.drop_table('user_preferences')
    op.drop_table('scan_results')
    op.drop_table('monitoring_rules')
    op.drop_table('users')

