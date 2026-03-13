#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from flask import current_app, g
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db
from app.utils.common import time_to_str

class Admin(db.Model):
    __tablename__ = 'admin'
    __table_args__ = {'comment': '管理员信息表'}

    # 主键
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='管理员ID')
    
    # 核心字段
    username = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), nullable=False, unique=True, comment='用户名')
    email = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=False, unique=True, comment='邮箱')
    mobile = db.Column(db.String(11, collation='utf8mb4_unicode_ci'), nullable=False, unique=True, comment='手机号')
    real_name = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), comment='真实姓名')
    password = db.Column(db.String(300, collation='utf8mb4_unicode_ci'), nullable=False, comment='加密密码')
    status = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default='1', comment='"待审核":0, "已通过":1, "已失效":2')

    # 统计字段
    last_login = db.Column(db.Integer, comment='最后登录时间')
    last_login_ip = db.Column(db.String(50, collation='utf8mb4_unicode_ci'), comment='最后登录IP')
    login_count = db.Column(db.Integer, default=0, comment='登录次数')

    # 时间戳
    create_time = db.Column(db.Integer, default=lambda: int(time.time()), comment='创建时间')
    update_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()), comment='更新时间')
    delete_time = db.Column(db.Integer, comment='删除时间')


    # 密码处理 (标准化)
    @staticmethod
    def hash_password(password):
        """生成安全密码Hash"""
        return generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)


    # Token 处理
    def generate_auth_token(self, expiration=60 * 60 * 24 * 30, app_type='web'):
        """生成并缓存 Token"""
        from app import redis_store
        s = Serializer(secret_key=current_app.config['SECRET_KEY'],
                       salt=current_app.config['SALT_KEY'])
        
        # 使用 admin_id
        token_payload = {'confirm_id': self.admin_id}
        auth_token = s.dumps(token_payload)

        # 存入 Redis
        try:
            redis_key = '{}_{}_auth_token'.format(app_type, self.admin_id)
            # 如果 token 是 bytes，转字符串
            if isinstance(auth_token, bytes):
                auth_token = auth_token.decode('utf-8')
            redis_store.set(redis_key, auth_token, expiration)
        except Exception as e:
            current_app.logger.error(f"Redis Error: {e}")

        return auth_token

    def delete_auth_token(self, app_type=None):
        """销毁 Token"""
        from app import redis_store
        if not app_type:
            return False
        try:
            redis_store.delete('{}_{}_auth_token'.format(app_type, self.admin_id))
        except Exception:
            pass
        g.user = None
        return True

    @staticmethod
    def verify_auth_token(token, app_type=None):
        """验证 Token 有效性"""
        s = Serializer(secret_key=current_app.config['SECRET_KEY'],
                       salt=current_app.config['SALT_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return None

        if 'confirm_id' not in data:
            return None

        admin_id = data['confirm_id']
        return Admin.query.filter_by(admin_id=admin_id).first()


    # 业务逻辑
    @staticmethod
    def create_admin(username, email, mobile, real_name, password, status='1'):
        """创建管理员"""
        # 查重
        if Admin.query.filter_by(username=username).first():
            return None, '用户名已存在'
        if Admin.query.filter_by(mobile=mobile).first():
            return None, '手机号已存在'

        admin = Admin()
        admin.username = username
        admin.email = email
        admin.mobile = mobile
        admin.real_name = real_name
        admin.password = Admin.hash_password(password)
        admin.status = status # 默认为1直接通过，方便测试

        db.session.add(admin)
        try:
            db.session.commit()
            return admin, '创建成功'
        except Exception as e:
            db.session.rollback()
            return None, f'数据库错误: {str(e)}'
        
    @staticmethod
    def get_admin_list(page=1, per_page=20, keyword=None, status=None):
        """
        获取管理员列表 (分页 + 搜索)
        """
        query = Admin.query
        
        # 1. 关键词搜索 (支持 用户名/真实姓名/邮箱/手机号)
        if keyword:
            like_keyword = f'%{keyword}%'
            query = query.filter(
                db.or_(
                    Admin.username.like(like_keyword),
                    Admin.real_name.like(like_keyword),
                    Admin.email.like(like_keyword),
                    Admin.mobile.like(like_keyword)
                )
            )
        
        # 2. 状态筛选
        if status and status != 'all':
            query = query.filter_by(status=str(status))
        
        # 3. 排序：按创建时间倒序
        query = query.order_by(db.desc(Admin.create_time))
        
        # 4. 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total


    def to_dict(self):
        """完整信息字典"""
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'email': self.email,
            'mobile': self.mobile,
            'real_name': self.real_name,
            'status': self.status,
            'last_login': time_to_str(self.last_login) if self.last_login else None,
            'create_time': time_to_str(self.create_time) if self.create_time else None
        }
    
    def to_simple_dict(self):
        """简略信息字典 (用于注册查询等场景)"""
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'real_name': self.real_name,
            'status': self.status,
            'create_time': time_to_str(self.create_time) if self.create_time else None
        }