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
from app.services.user.user_service import UserService

class SignIn(Resource):
    def post(self):
        """用户登录"""
        args = user_sign_in_parser()
        data, code, msg = UserService.login(args['username'], args['password'])
        if not data:
            return error(resid=code, msg=msg)
        # 保持原样式，并应用 fields
        return success(msg=msg, data=data, data_fileds=user_fields())