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
from app.utils.decorators import login_required
from app.utils.uploader import Uploader

class UserInfoResource(Resource):
    method_decorators = [login_required]

    def post(self):

        # 1. 解析参数
        args = user_update_parser()
        nickname = args.get('nickname')
        avatar_file = args.get('avatar')
        bio = args.get('bio')
        email = args.get('email')
        tag_action = args.get('tag_action')
        tag_name = args.get('tag_name')

        # 2. 获取当前用户对象
        user = User.query.get(g.user.id)
        if not user:
            return error(error_code.USER_NOT_EXISTS, msg=u"用户不存在")

        # 3. 执行业务逻辑
        # 处理标签
        if tag_action and tag_name:
            if tag_action == "add":
                user.add_tag(tag_name)
            elif tag_action == "delete":
                user.delete_tag(tag_name)

        # 处理基本文本
        if nickname:
            user.nickname = nickname
        if bio is not None:
            user.bio = bio

        # 处理邮箱唯一性
        if email:
            is_exist = User.query.filter(User.email == email, User.id != user.id).first()
            if is_exist:
                return error(error_code.DB_ERROR, msg=u"该邮箱已被占用")
            user.email = email

        # 处理头像
        if avatar_file:
            config = {
                "pathFormat": "uploads/avatar/{yyyy}{mm}{dd}/{time}{rand:6}",
                "maxSize": 2 * 1024 * 1024,
                "allowFiles": [".png", ".jpg", ".jpeg", ".gif"],
                "oriName": avatar_file.filename
            }
            uploader = Uploader(avatar_file, config, current_app.static_folder)
            if uploader.stateInfo == "SUCCESS":
                user.avatar = uploader.getFileInfo()['url']
            else:
                return error(error_code.FILE_UPLOAD_ERROR, msg=uploader.stateInfo)

        # 4. 更新修改时间 (防止 SQL 报错并记录活跃)
        user.e_time = int(time.time())

        # 5. 提交数据库
        try:
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update User Error: {str(e)}")
            return error(error_code.DB_ERROR, msg=u"数据库保存失败")

        # 6. 构造返回数据 (与 SignIn 逻辑一致)
        data = user.to_dict()
        
        # 7. 返回结果并使用 fields 过滤
        return success(
            msg=u"资料更新成功", 
            data=data, 
            data_fileds=user_upd_fields()
        )