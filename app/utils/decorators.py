#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/30 上午9:28
# @Software：PyCharm
# @Author  : scott
from functools import wraps

from flask import g

from app.api.common.error_code import AUTH_TOKEN_ERROR, USER_NOT_ACTIVE_OR_LOCKED, CURRENT_USER_ID_ERROR
from app.api.common.response import error
from app.models.DoctorInfo import DoctorInfo
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

            current_user_id = g.current_user_id
            if not current_user_id or str(admin.id) != current_user_id:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户不匹配,请重新登录'.format(CURRENT_USER_ID_ERROR))

            g.admin = admin
        else:
            user = User.verify_auth_token(g.auth_token, g.app_type)
            if not user:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')

            current_user_id = g.current_user_id
            if not current_user_id or str(user.id) != current_user_id:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户不匹配,请重新登录'.format(CURRENT_USER_ID_ERROR))

            g.user = user
        return f(*args, **kwargs)

    return decorated_function


def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not g.auth_token:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请登录后操作')

        admin = DoctorInfo.verify_auth_token(g.auth_token)

        if not admin:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')

        if admin.delete is True:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户已经被禁用或冻结'.format(USER_NOT_ACTIVE_OR_LOCKED))
        current_user_id = g.current_user_id
        if not current_user_id or str(admin.id) != current_user_id:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户不匹配,请重新登录'.format(CURRENT_USER_ID_ERROR))
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
