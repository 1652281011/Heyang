#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful import Resource
from app.api.common import error_code
from app.api.common.parser import admin_register_parser
from app.api.common.response import success, error
from app.models.admin import Admin
from app.models import db

class AdminRegister(Resource):

    def post(self):
        """
        管理员注册接口
        URL: /v1/admin/register
        Method: POST
        """
        # 1. 解析参数
        args = admin_register_parser()
        username = args['username']
        email = args['email']
        mobile = args['mobile']
        password = args['password']
        real_name = args.get('real_name')

        # 2. 优先根据【用户名】查找是否存在历史记录
        existing_admin = Admin.query.filter_by(username=username).first()

        if existing_admin:
            # === 用户已存在，根据状态进行分流处理 ===
            status = existing_admin.status
            
            if status == '0':
                # 状态: 待审核
                return success(msg='您的注册申请正在审核中，请耐心等待', data=existing_admin.to_simple_dict())
            
            elif status == '1':
                # 状态: 已通过
                return error(resid=400, msg='该用户名已注册且审核通过，请直接登录')
            
            elif status == '2':
                # 状态: 已拒绝
                return error(resid=400, msg='您的注册申请已被拒绝，无法重复注册。如有疑问请联系超级管理员。')

        # 1. 检查邮箱和手机号是否被占用 (全局检查)
        if Admin.query.filter_by(email=email).first():
            return error(resid=400, msg='邮箱已存在')
        
        if Admin.query.filter_by(mobile=mobile).first():
            return error(resid=400, msg='手机号已存在')

        # 2. 调用模型创建管理员
        new_admin, msg = Admin.create_admin(
            username=username,
            email=email,
            mobile=mobile,
            real_name=real_name,
            password=password,
            status='0' 
        )

        # 3. 判断创建结果
        if not new_admin:
            return error(resid=error_code.DATABASE_TABLE_INSERT_ERROR, msg=msg or '注册失败')

        return success(msg='注册成功，请等待管理员审核', data=new_admin.to_dict())