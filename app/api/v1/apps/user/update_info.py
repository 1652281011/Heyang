# -*- coding: utf-8 -*-
import time
from flask import g, current_app
from flask_restful import Resource

from app.api.common import error_code
from app.api.common.fields import user_fields, user_upd_fields  # 导入对应的 fields
from app.api.common.parser import user_update_parser
from app.api.common.response import success, error
from app.models.base import db
from app.models.users import User
from app.services.user.user_service import UserService
from app.utils.decorators import login_required
from app.utils.uploader import Uploader

class UserInfoResource(Resource):
    # 依然保留登录限制
    method_decorators = [login_required]

    def post(self):
        """更新用户信息接口"""
        args = user_update_parser()

        data, code, msg = UserService.update_profile(g.user.id, args)

        # 3. 错误处理
        if not data:
            return error(resid=code, msg=msg)

        # 4. 成功返回 (严格保持你要求的样式)
        return success(
            msg=msg, 
            data=data, 
            data_fileds=user_upd_fields()
        )