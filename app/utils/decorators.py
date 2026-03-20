#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/30 上午9:28
# @Software：PyCharm
# @Author  : scott
from functools import wraps

from flask import g, request

from app.api.common.error_code import AUTH_TOKEN_ERROR, USER_NOT_ACTIVE_OR_LOCKED, CURRENT_USER_ID_ERROR
from app.api.common.response import error
from app.models.DoctorInfo import DoctorInfo
from app.models.admin import Admin
from app.models.users import User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.auth_token:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请登录后操作')
        if g.api_type == 'admin':
            admin = DoctorInfo.verify_auth_token(g.auth_token)
            if not admin:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')
            if admin.delete is True:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户已经被禁用或冻结'.format(USER_NOT_ACTIVE_OR_LOCKED))

            # current_user_id = g.current_user_id
            # if not current_user_id or str(admin.id) != current_user_id:
            #     return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户不匹配,请重新登录'.format(CURRENT_USER_ID_ERROR))

            g.admin = admin
        else:
            user = User.verify_auth_token(g.auth_token, g.app_type)
            if not user:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')

            # current_user_id = g.current_user_id
            # if not current_user_id or str(user.id) != current_user_id:
            #     return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户不匹配,请重新登录'.format(CURRENT_USER_ID_ERROR))

            g.user = user
        return f(*args, **kwargs)

    return decorated_function


def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. 拦截器获取的 token 存放在 g.auth_token
        if not g.auth_token:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请登录管理员账号')

        # 2. 调用 Admin 模型的验证逻辑
        app_type = getattr(g, 'app_type', 'web')
        admin = Admin.verify_auth_token(g.auth_token, app_type=app_type)

        if not admin:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'管理员身份已过期，请重新登录')

        # 3. 校验逻辑删除（如果 delete_time 有值，说明已被删除）
        if admin.delete_time is not None:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'该管理员账号已被注销')

        # 4. 校验账号状态
        # status: "0"待审核, "1"已通过, "2"已失效
        if admin.status == '0':
            return error(resid=AUTH_TOKEN_ERROR, msg=u'您的管理员申请正在审核中')
        if admin.status == '2':
            return error(resid=AUTH_TOKEN_ERROR, msg=u'您的管理员账号已失效')
        if admin.status != '1':
            return error(resid=AUTH_TOKEN_ERROR, msg=u'账号异常')

        # 5. 双重校验：Header 中的 User-Id 是否等于 admin_id
        # 注意：Postman 发送的通常是 User-Id，对应数据库里的 admin_id
        # header_uid = request.headers.get('User-Id') or request.headers.get('Current-User-Id')
        # if not header_uid or str(admin.admin_id) != str(header_uid):
        #     return error(resid=AUTH_TOKEN_ERROR, msg=u'管理员信息不匹配')

        # 验证通过，存入全局对象 g
        g.admin = admin
        return f(*args, **kwargs)

    return decorated_function

def professor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 假设 g.user 已经在之前的 login_required 中被赋值
        # 且 g.user 对象里有 role 字段或者身份标识
        if not hasattr(g, 'user') or not g.user:
            return error(msg='请先登录', resid=401)
        
        # 这里的判断条件根据你实际 User 表的设计来，假设 user.role == 'professor'
        # 或者判断是否在 Professor 表中
        if getattr(g.user, 'role', '') != 'professor': 
            return error(msg='权限不足，仅教授可执行此操作', resid=403)
            
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            return error(msg='请先登录', resid=401)
        
        # 假设 Admin 用户 role 为 'admin'
        if getattr(g.user, 'role', '') != 'admin':
            return error(msg='权限不足，需要管理员权限', resid=403)
            
        return f(*args, **kwargs)
    return decorated
