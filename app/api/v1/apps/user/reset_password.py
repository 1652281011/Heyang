from flask_restful import Resource, reqparse

from app.api.common.parser import user_reset_password_parser
from app.api.common.response import error, success
from app.services.user.user_service import UserService


class ResetPassword(Resource):
    def post(self):
        args = user_reset_password_parser()
        flag, code, msg = UserService.reset_password(args['email'], args['code'], args['new_password'])
        if not flag: return error(resid=code, msg=msg)
        return success(msg=msg)