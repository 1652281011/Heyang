# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse
from app.api.common.parser import email_code_parser, user_register_parser
from app.api.common.response import success, error
from app.models.users import User
from app.services.user.user_service import UserService

class SendCode(Resource):
    def post(self):
        args = email_code_parser()
        flag, code, msg = UserService.send_code(args['email'], args['type'])
        if not flag: return error(resid=code, msg=msg)
        return success(msg=msg)

class Register(Resource):
    def post(self):
        args = user_register_parser()
        user, code, msg = UserService.register(args)
        if not user: return error(resid=code, msg=msg)
        return success(msg=u'注册成功', data=user.to_dict())