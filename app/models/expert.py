#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 上午10:00
# @Software：PyCharm
# @Author  : system
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadSignature
from app.models import db
from app.utils.common import md5_str, time_to_str
import base64
import random
import time

class Expert(db.Model):
    __tablename__ = 'expert'
    __table_args__ = {'comment': '专家信息表'}

    expert_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        comment='专家ID'
    )
    username = db.Column(
        db.String(50, collation='utf8mb4_unicode_ci'),
        nullable=False,
        unique=True,
        comment='用户名'
    )
    email = db.Column(
        db.String(100, collation='utf8mb4_unicode_ci'),
        nullable=False,
        unique=True,
        comment='邮箱'
    )
    mobile = db.Column(
        db.String(11, collation='utf8mb4_unicode_ci'),
        nullable=False,
        unique=True,
        comment='手机号'
    )
    real_name = db.Column(
        db.String(50, collation='utf8mb4_unicode_ci'),
        nullable=False,
        comment='真实姓名'
    )
    title = db.Column(
        db.String(100, collation='utf8mb4_unicode_ci'),
        comment='职称'
    )
    organization = db.Column(
        db.String(200, collation='utf8mb4_unicode_ci'),
        nullable=False,
        comment='工作单位'
    )
    research_field = db.Column(
        db.String(200, collation='utf8mb4_unicode_ci'),
        comment='研究领域'
    )
    introduction = db.Column(
        db.Text(collation='utf8mb4_unicode_ci'),
        comment='个人简介'
    )
    avatar = db.Column(
        db.String(500, collation='utf8mb4_unicode_ci'),
        comment='头像URL'
    )
    
    # 密码字段
    password = db.Column(
        db.String(300, collation='utf8mb4_unicode_ci'),
        nullable=False,
        comment='密码'
    )
    
    # 审批状态
    is_approved = db.Column(
        db.Boolean,
        default=False,
        comment='是否通过审批'
    )
    approval_status = db.Column(
        db.String(20, collation='utf8mb4_unicode_ci'),
        default='pending',
        comment='审批状态: pending(待审批), approved(已批准), rejected(已拒绝)'
    )
    approved_by = db.Column(
        db.Integer,
        comment='审批人ID'
    )
    approved_time = db.Column(
        db.Integer,
        comment='审批时间'
    )
    approval_notes = db.Column(
        db.Text(collation='utf8mb4_unicode_ci'),
        comment='审批备注'
    )
    
    # 个人信息
    gender = db.Column(
        db.String(10, collation='utf8mb4_unicode_ci'),
        comment='性别: male(男), female(女)'
    )
    birth_date = db.Column(
        db.String(20, collation='utf8mb4_unicode_ci'),
        comment='出生日期'
    )
    degree = db.Column(
        db.String(50, collation='utf8mb4_unicode_ci'),
        comment='学历'
    )
    work_years = db.Column(
        db.Integer,
        comment='工作年限'
    )
    
    # 状态字段
    status = db.Column(
        db.SmallInteger,
        default=1,
        comment='状态: 1-正常, 2-禁用, 0-删除'
    )
    
    # 登录信息
    last_login = db.Column(
        db.Integer,
        comment='最后登录时间'
    )
    last_login_ip = db.Column(
        db.String(50, collation='utf8mb4_unicode_ci'),
        comment='最后登录IP'
    )
    login_count = db.Column(
        db.Integer,
        default=0,
        comment='登录次数'
    )
    
    # 时间戳
    create_time = db.Column(
        db.Integer,
        comment='创建时间'
    )
    update_time = db.Column(
        db.Integer,
        comment='更新时间'
    )
    delete_time = db.Column(
        db.Integer,
        comment='删除时间'
    )

    @staticmethod
    def generation_password(password):
        """生成加密密码"""
        rand1 = md5_str(str(random.randint(1000, 9999)))
        rand2 = md5_str(str(random.randint(1000, 9999)))
        _password = rand1[1:-2] + md5_str(base64.b64encode(md5_str(password).encode('utf8'))) + rand2[5: -3]
        return _password

    def check_password(self, password):
        """验证密码"""
        encrypted_password = Expert.generation_password(password)
        return self.password == encrypted_password

    def generate_auth_token(self, expiration=60 * 60 * 24 * 30, app_type='web'):
        """
        生成token供使用 设置有效期
        :param expiration: 有效期
        :param app_type: 客户端类型 android web ios
        :return:  auth_token值
        """
        from app import redis_store
        s = Serializer(secret_key=current_app.config['SECRET_KEY'],
                       salt=current_app.config['SALT_KEY'])
        auth_token = s.dumps({'confirm_id': self.expert_id})

        # 将auth_token保存到redis里面，并设置有效期
        redis_store.set('{}_{}_auth_token'.format(app_type, self.expert_id), auth_token, expiration)

        return auth_token

    def delete_auth_token(self, app_type=None):
        """从redis中删除auth_token表示无效"""
        from app import redis_store
        if not app_type:
            return False
        redis_store.delete('{}_{}_auth_token'.format(app_type, self.expert_id))
        return True

    @staticmethod
    def verify_auth_token(token, app_type=None):
        """验证token是否有效"""
        from app import redis_store
        if not app_type:
            return None

        s = Serializer(secret_key=current_app.config['SECRET_KEY'],
                       salt=current_app.config['SALT_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            # token超时失效了
            return None
        except BadSignature as e:
            # token错误
            current_app.logger.exception(e)
            return None
        except Exception as e:
            # 未知的异常错误
            current_app.logger.exception(e)
            return None

        if 'confirm_id' not in data:
            return None

        expert_id = data['confirm_id']

        try:
            expert = Expert.query.filter_by(expert_id=expert_id).first()
        except Exception as e:
            current_app.logger.exception(e)
            return None

        return expert

    @staticmethod
    def expert_is_exist(expert_id):
        """检查专家是否存在"""
        return Expert.query.filter_by(expert_id=expert_id).first()

    @staticmethod
    def create_expert(username, email, mobile, real_name, password, 
                     title=None, organization=None, research_field=None, 
                     introduction=None, gender=None, birth_date=None, 
                     degree=None, work_years=None, avatar=None):
        """创建专家"""
        expert = Expert()
        
        # 检查用户名是否已存在
        if Expert.query.filter_by(username=username).first():
            return None, '用户名已存在'
        
        # 检查邮箱是否已存在
        if Expert.query.filter_by(email=email).first():
            return None, '邮箱已存在'
        
        # 检查手机号是否已存在
        if Expert.query.filter_by(mobile=mobile).first():
            return None, '手机号已存在'
        
        # 验证密码强度
        if len(password) < 6:
            return None, '密码至少6位'
        
        # 生成加密密码
        _password = Expert.generation_password(password)
        
        # 设置专家信息
        expert.username = username
        expert.email = email
        expert.mobile = mobile
        expert.real_name = real_name
        expert.password = _password
        expert.title = title
        expert.organization = organization
        expert.research_field = research_field
        expert.introduction = introduction
        expert.gender = gender
        expert.birth_date = birth_date
        expert.degree = degree
        expert.work_years = work_years
        expert.avatar = avatar
        
        # 设置时间戳
        expert.create_time = int(time.time())
        expert.update_time = expert.create_time
        
        # 默认状态为待审批
        expert.is_approved = False
        expert.approval_status = 'pending'
        expert.status = 1
        
        db.session.add(expert)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return None, str(e)
        
        return expert, '注册成功，等待管理员审批'

    @staticmethod
    def get_expert(expert_id):
        """获取专家"""
        return Expert.query.filter_by(expert_id=expert_id).first()

    @staticmethod
    def update_expert(expert_id, **kwargs):
        """更新专家信息"""
        expert = Expert.query.filter_by(expert_id=expert_id).first()
        if not expert:
            return None, '专家不存在'
        
        # 过滤掉不能更新的字段
        exclude_fields = ['expert_id', 'password', 'is_approved', 'approval_status', 
                         'approved_by', 'approved_time', 'approval_notes', 'create_time']
        for key, value in kwargs.items():
            if key in exclude_fields:
                continue
            if hasattr(expert, key):
                setattr(expert, key, value)
        
        # 更新更新时间
        expert.update_time = int(time.time())
        
        try:
            db.session.commit()
            return expert, '更新成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_expert(expert_id):
        """软删除专家"""
        expert = Expert.query.filter_by(expert_id=expert_id).first()
        if not expert:
            return False, '专家不存在'
        
        # 软删除
        expert.status = 0
        expert.delete_time = int(time.time())
        
        try:
            db.session.commit()
            return True, '删除成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def disable_expert(expert_id):
        """禁用专家"""
        expert = Expert.query.filter_by(expert_id=expert_id).first()
        if not expert:
            return False, '专家不存在'
        
        expert.status = 2
        expert.update_time = int(time.time())
        
        try:
            db.session.commit()
            return True, '禁用成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def enable_expert(expert_id):
        """启用专家"""
        expert = Expert.query.filter_by(expert_id=expert_id).first()
        if not expert:
            return False, '专家不存在'
        
        expert.status = 1
        expert.update_time = int(time.time())
        
        try:
            db.session.commit()
            return True, '启用成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def restore_expert(expert_id):
        """恢复已删除的专家"""
        expert = Expert.query.filter_by(expert_id=expert_id).first()
        if not expert:
            return False, '专家不存在'
        
        if expert.status != 0:
            return False, '专家未被删除'
        
        expert.status = 1
        expert.delete_time = None
        expert.update_time = int(time.time())
        
        try:
            db.session.commit()
            return True, '恢复成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def approve_expert(expert_id, approved_by, notes=''):
        """批准专家"""
        expert = Expert.query.filter_by(expert_id=expert_id).first()
        if not expert:
            return False, '专家不存在'
        
        if expert.approval_status != 'pending':
            return False, '专家当前状态不可审批'
        
        expert.is_approved = True
        expert.approval_status = 'approved'
        expert.approved_by = approved_by
        expert.approved_time = int(time.time())
        expert.approval_notes = notes
        expert.update_time = int(time.time())
        
        try:
            db.session.commit()
            return True, '专家批准成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def reject_expert(expert_id, approved_by, notes=''):
        """拒绝专家"""
        expert = Expert.query.filter_by(expert_id=expert_id).first()
        if not expert:
            return False, '专家不存在'
        
        if expert.approval_status != 'pending':
            return False, '专家当前状态不可审批'
        
        expert.is_approved = False
        expert.approval_status = 'rejected'
        expert.approved_by = approved_by
        expert.approved_time = int(time.time())
        expert.approval_notes = notes
        expert.update_time = int(time.time())
        
        try:
            db.session.commit()
            return True, '专家拒绝成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def reset_password(expert_id, new_password):
        """重置密码"""
        expert = Expert.query.filter_by(expert_id=expert_id).first()
        if not expert:
            return False, '专家不存在'
        
        if len(new_password) < 6:
            return False, '密码至少6位'
        
        _password = Expert.generation_password(new_password)
        expert.password = _password
        expert.update_time = int(time.time())
        
        try:
            db.session.commit()
            return True, '密码重置成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def get_expert_list(page=1, per_page=20, keyword=None, approval_status=None, 
                       status=None, order_by='create_time', order='desc'):
        """获取专家列表"""
        query = Expert.query
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                db.or_(
                    Expert.username.like(f'%{keyword}%'),
                    Expert.real_name.like(f'%{keyword}%'),
                    Expert.email.like(f'%{keyword}%'),
                    Expert.mobile.like(f'%{keyword}%'),
                    Expert.organization.like(f'%{keyword}%'),
                    Expert.research_field.like(f'%{keyword}%')
                )
            )
        
        # 审批状态筛选
        if approval_status and approval_status != 'all':
            if approval_status in ['pending', 'approved', 'rejected']:
                query = query.filter_by(approval_status=approval_status)
        
        # 状态筛选
        if status and status != 'all':
            if status == 'active':
                query = query.filter_by(status=1)
            elif status == 'disabled':
                query = query.filter_by(status=2)
            elif status == 'deleted':
                query = query.filter_by(status=0)
        
        # 排序
        order_column = getattr(Expert, order_by, Expert.create_time)
        if order == 'desc':
            query = query.order_by(db.desc(order_column))
        else:
            query = query.order_by(order_column)
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total

    @staticmethod
    def get_expert_count(keyword=None, approval_status=None, status=None):
        """获取专家数量"""
        query = Expert.query
        
        if keyword:
            query = query.filter(
                db.or_(
                    Expert.username.like(f'%{keyword}%'),
                    Expert.real_name.like(f'%{keyword}%'),
                    Expert.email.like(f'%{keyword}%'),
                    Expert.mobile.like(f'%{keyword}%')
                )
            )
        
        if approval_status and approval_status != 'all':
            query = query.filter_by(approval_status=approval_status)
        
        if status and status != 'all':
            if status == 'active':
                query = query.filter_by(status=1)
            elif status == 'disabled':
                query = query.filter_by(status=2)
            elif status == 'deleted':
                query = query.filter_by(status=0)
        
        return query.count()

    def can_login(self):
        """检查是否可以登录"""
        if self.status == 0:
            return False, '账号已被删除'
        elif self.status == 2:
            return False, '账号已被禁用'
        elif not self.is_approved:
            return False, '账号未通过审批'
        
        return True, ''

    def record_login(self, ip_address):
        """记录登录信息"""
        self.last_login = int(time.time())
        self.last_login_ip = ip_address
        self.login_count += 1
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return False

    def to_dict(self):
        """转换为字典"""
        res = {
            'expert_id': self.expert_id,
            'username': self.username,
            'email': self.email,
            'mobile': self.mobile,
            'real_name': self.real_name,
            'title': self.title,
            'organization': self.organization,
            'research_field': self.research_field,
            'introduction': self.introduction,
            'avatar': self.avatar,
            'is_approved': self.is_approved,
            'approval_status': self.approval_status,
            'status': self.status,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'degree': self.degree,
            'work_years': self.work_years,
            'last_login': time_to_str(self.last_login) if self.last_login else None,
            'last_login_ip': self.last_login_ip,
            'login_count': self.login_count,
            'create_time': time_to_str(self.create_time) if self.create_time else None,
            'update_time': time_to_str(self.update_time) if self.update_time else None
        }
        
        # 如果有审批信息
        if self.approved_by:
            from app.models.admin import Admin
            admin = Admin.query.filter_by(admin_id=self.approved_by).first()
            res['approved_by'] = {
                'admin_id': self.approved_by,
                'username': admin.username if admin else None,
                'real_name': admin.real_name if admin else None
            }
            res['approved_time'] = time_to_str(self.approved_time) if self.approved_time else None
            res['approval_notes'] = self.approval_notes
        
        return res

    def to_simple_dict(self):
        """简略信息"""
        return {
            'expert_id': self.expert_id,
            'username': self.username,
            'real_name': self.real_name,
            'organization': self.organization,
            'title': self.title,
            'is_approved': self.is_approved,
            'approval_status': self.approval_status,
            'status': self.status,
            'create_time': time_to_str(self.create_time) if self.create_time else None
        }

    def to_public_dict(self):
        """公开信息（用于对外展示）"""
        return {
            'expert_id': self.expert_id,
            'real_name': self.real_name,
            'title': self.title,
            'organization': self.organization,
            'research_field': self.research_field,
            'introduction': self.introduction,
            'avatar': self.avatar,
            'work_years': self.work_years,
            'create_time': time_to_str(self.create_time) if self.create_time else None
        }