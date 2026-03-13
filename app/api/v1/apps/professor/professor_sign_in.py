#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import current_app
from flask_restful import Resource
from app.api.common import error_code
from app.api.common.fields import professor_fields
from app.api.common.parser import professor_sign_in_parser
from app.api.common.response import error, success
from app.models.professor import Professor

class ProfessorSignIn(Resource):

    def post(self):
        """
        教授登录
        URL: /v1/professor/sign-in
        """
        args = professor_sign_in_parser()
        
        # 获取邮箱和密码
        email = args['email']
        password = args['password']

        # 1. 查询用户 (使用 email)
        professor = Professor.query.filter_by(email=email).first()
        
        if not professor:
            return error(error_code.USER_NOT_EXISTS, msg=u'用户不存在')
        
        # 2. 检查审核状态
        user_status = getattr(professor, 'professor_status', 'wait')
        if user_status != 'accept':
            current_app.logger.warning(f"教授登录失败(状态受限): {email}, 状态: {user_status}")
            status_map = {
                'wait': '账号正在审核中，请耐心等待',
                'reject': '您的申请已被拒绝',
                'block': '账号已被停用'
            }
            return error(resid=403, msg=status_map.get(user_status, '账号状态异常'))

        # 3. 验证密码 (使用标准哈希验证)
        if not professor.check_password(password):
            current_app.logger.info(f"教授登录密码错误: {email}")
            return error(error_code.USER_PASSWORD_NOT_CORRECT, msg=u'密码错误')

        # 4. 生成 Token 并返回
        token = professor.generate_auth_token()
        
        # 构造返回数据
        data = professor.to_dict()
        data['auth_token'] = token
        
        # 处理 bytes 转 string
        if isinstance(token, bytes):
            data['auth_token'] = token.decode('utf-8')

        return success(msg=u'登录成功', data=data, data_fileds=professor_fields())