#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/30 上午8:11
# @Author  : scott
"""管理员登录"""
import time
from flask import current_app, request
from flask_restful import Resource

from app.api.common import error_code
from app.api.common.fields import user_fields
from app.api.common.parser import user_sign_in_parser
from app.api.common.response import error, success
from app.models.users import User
from app.models import db

class SignIn(Resource):

    def post(self):
        """
        登录接口
        """
        args = user_sign_in_parser()
        username = args['username']
        password = args['password']

        # 1. 查询用户
        user = User.query.filter(User.username == username).first()
        if not user:
            return error(error_code.USER_NOT_EXISTS, msg=u'用户不存在')
          
        # 2. 验证密码 
        if not user.check_password(password):
            current_app.logger.warning(f"密码错误: {username}")
            return error(error_code.USER_PASSWORD_NOT_CORRECT, msg=u'密码不正确')
        

        current_ts = int(time.time())
        user.e_time = current_ts  # 更新数据库中的 e_time 字段
        
        try:
            db.session.commit()  # 提交到数据库
        except Exception as e:
            db.session.rollback()
            # 记录日志但不影响用户登录
            print(f"更新登录时间失败: {e}")


        # 5. 生成 Token (关键步骤：登录必须返回Token)
        token = user.generate_auth_token()

        # 6. 构造返回数据
        data = user.to_dict()
        
        # 将 Token 放入返回数据中
        data['auth_token'] = token
        
        if isinstance(data['auth_token'], bytes):
            data['auth_token'] = data['auth_token'].decode('utf-8')

        return success(msg=u'登录成功', data=data, data_fileds=user_fields())