#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db
from app.utils.common import time_to_str

class Professor(db.Model):
    __tablename__ = 'professors'
    __table_args__ = {'comment': '专业人员信息表'}

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='专家ID(自增主键)'
    )
    
    email = db.Column(
        db.String(100, collation='utf8mb4_unicode_ci'),
        nullable=False,
        unique=True,
        comment='邮箱(登录账号)'
    )

    password = db.Column(db.String(300), nullable=False, comment='加密密码')
    
    professor_status = db.Column(
        db.String(20), 
        default='wait',
        comment='用户状态: wait-待审核, accept-通过, reject-拒绝'
    )

    # 个人详细信息
    professor_name = db.Column(db.String(50), nullable=False, comment='姓名')
    gender = db.Column(db.String(10), nullable=True, comment='性别')
    title = db.Column(db.String(50), nullable=True, comment='职称')
    organization = db.Column(db.String(100), nullable=True, comment='单位')
    
    create_time = db.Column(db.Integer, default=lambda: int(time.time()), comment='注册时间')


    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_auth_token(self, expiration=60 * 60 * 24 * 30, app_type=u'web'):
        from app import redis_store
        s = Serializer(secret_key=current_app.config['SECRET_KEY'], salt=current_app.config['SALT_KEY'])
        
        # 使用 self.id
        token_payload = {'confirm_id': self.id}
        auth_token = s.dumps(token_payload)
        
        try:
            # Redis key 也使用 id
            redis_store.set('{}_{}_auth_token'.format(app_type, self.id), auth_token, expiration)
        except Exception as e:
            current_app.logger.error(f"Redis写入失败: {e}")
            
        return auth_token

    def delete_auth_token(self, app_type=None):
        """销毁Token"""
        from app import redis_store
        if not app_type:
            return False
        try:
            redis_store.delete('{}_{}_auth_token'.format(app_type, self.id))
        except Exception:
            pass
        return True

    @staticmethod
    def verify_auth_token(token, app_type='web'):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'], salt=current_app.config['SALT_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return None
        
        if 'confirm_id' not in data:
            return None
            
        # 根据 id 查询
        return Professor.query.filter_by(id=data['confirm_id']).first()

    
    @staticmethod
    def professor_is_exist(email):
        return Professor.query.filter_by(email=email).first()

    @staticmethod
    def create_professor(email, password, professor_name, gender=None, title=None, organization=None):
        professor = Professor()
        professor.email = email
        professor.password = Professor.hash_password(password)
        professor.professor_name = professor_name
        professor.gender = gender
        professor.title = title
        professor.organization = organization
        professor.professor_status = "wait"

        db.session.add(professor)
        try:
            db.session.commit()
            return professor
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'professor_name': self.professor_name,
            'gender': self.gender,
            'title': self.title,
            'organization': self.organization,
            'professor_status': self.professor_status,
            'create_time': time_to_str(self.create_time) if self.create_time else None
        }