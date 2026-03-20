# -*- coding: utf-8 -*-
from flask_restful import Resource
from app.api.common.parser import user_register_parser
from app.api.common.response import success, error
from app.models.users import User

class Register(Resource):
    def post(self):
        """用户注册接口"""
        # 1. 获取参数
        args = user_register_parser()
        
        # 2. 检查手机号是否存在
        if User.query.filter_by(username=args['username']).first():
            return error(resid=400, msg='该手机号已被注册')

        # 3. 执行创建逻辑 (接收两个返回值)
        new_user, msg = User.create_user(
            username=args['username'],
            password_plain=args['password'], # 传入明文
            nickname=args.get('nickname',"momo"),
            role_type=args.get('role_type', "1")
        )

        # 4. 根据结果返回
        if not new_user:
            # 如果创建失败，msg 里会包含具体的数据库报错信息
            return error(resid=100, msg=msg)

        return success(msg='注册成功', data=new_user.to_dict())