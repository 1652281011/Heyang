#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful import Resource
from app.api.common import error_code
from app.api.common.parser import professor_sign_up_parser
from app.api.common.response import error, success
from app.models.professor import Professor

class ProfessorSignUp(Resource):

    def post(self):
        """
        教授注册
        URL: /v1/professor/sign-up
        """
        args = professor_sign_up_parser()
        
        email = args['email']
        password = args['password']
        professor_name = args['professor_name']
        
        # 获取选填参数
        organization = args.get('organization')
        gender = args.get('gender')
        title = args.get('title')

        # 2. 检查邮箱是否已存在
        _user = Professor.professor_is_exist(email)
        
        # 3. 如果不存在，则创建
        if not _user:
            _user = Professor.create_professor(
                email=email,
                password=password,
                professor_name=professor_name,
                organization=organization,
                gender=gender,
                title=title
            )
            
            if not _user:
                return error(resid=error_code.DATABASE_TABLE_INSERT_ERROR, msg=u'注册失败，请稍后重试')
            
            # 新注册成功的响应
            return success(msg='注册提交成功，请等待管理员审核', data=_user.to_dict())

        # 4. 如果已存在，根据状态返回提示
        user_status = getattr(_user, 'professor_status', 'wait')
        
        status_msg_map = {
            'wait': '账号已存在，正在等待审核',
            'accept': '账号已存在且审核通过，请直接登录',
            'reject': '账号申请曾被拒绝，请联系管理员'
        }
        
        msg = status_msg_map.get(user_status, f'账号已存在，当前状态: {user_status}')
        
        # 返回已存在用户的数据
        return success(msg=msg, data=_user.to_dict(), status=user_status)