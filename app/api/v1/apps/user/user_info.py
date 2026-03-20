# -*- coding: utf-8 -*-
from flask import g, request
from flask_restful import Resource
from sqlalchemy.orm import joinedload
from app.models.users import User
from app.api.common.response import success, error
from app.api.common.fields import user_full_info_fields
from app.utils.decorators import login_required

class UserFullInfoResource(Resource):
    method_decorators = [login_required]

    def get(self):
        """
        获取用户详细信息
        """
        # 1. 获取请求参数中的 user_id
        target_user_id = request.args.get('user_id', type=int)

        # 2. 确定查询目标：传了查别人，没传查自己
        if not target_user_id:
            target_user_id = g.user.id
        
        # 3. 执行查询 (使用 joinedload 预加载专业信息，减少查询次数)
        user = User.query.options(joinedload(User.pro_info)).get(target_user_id)

        if not user:
            return error(msg="目标用户不存在")

        # 4. 返回数据，通过 fields 自动处理格式化和嵌套逻辑
        return success(
            msg="获取资料成功",
            data=user,
            data_fileds=user_full_info_fields()
        )