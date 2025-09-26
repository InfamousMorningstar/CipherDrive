"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2025-09-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'USER', 'DOWNLOAD_ONLY', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('force_password_reset', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create user_quotas table
    op.create_table('user_quotas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quota_bytes', sa.BigInteger(), nullable=False),
        sa.Column('used_bytes', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_quotas_id'), 'user_quotas', ['id'], unique=False)

    # Create file_metadata table
    op.create_table('file_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('filepath', sa.String(length=1024), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('is_directory', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_metadata_id'), 'file_metadata', ['id'], unique=False)
    op.create_index(op.f('ix_file_metadata_filepath'), 'file_metadata', ['filepath'], unique=False)

    # Create shares table
    op.create_table('shares',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('share_token', sa.String(length=64), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_downloads', sa.Integer(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'EXPIRED', 'DISABLED', name='sharestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shares_id'), 'shares', ['id'], unique=False)
    op.create_index(op.f('ix_shares_share_token'), 'shares', ['share_token'], unique=True)

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_path', sa.String(length=1024), nullable=True),
        sa.Column('remote_ip', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_shares_share_token'), table_name='shares')
    op.drop_index(op.f('ix_shares_id'), table_name='shares')
    op.drop_table('shares')
    op.drop_index(op.f('ix_file_metadata_filepath'), table_name='file_metadata')
    op.drop_index(op.f('ix_file_metadata_id'), table_name='file_metadata')
    op.drop_table('file_metadata')
    op.drop_index(op.f('ix_user_quotas_id'), table_name='user_quotas')
    op.drop_table('user_quotas')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enums
    sa.Enum(name='sharestatus').drop(op.get_bind())
    sa.Enum(name='userrole').drop(op.get_bind())