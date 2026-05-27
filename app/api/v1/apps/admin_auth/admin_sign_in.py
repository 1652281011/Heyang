# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# # @Time    : 2022/7/30 上午8:11
# # @Author  : scott
# """管理员登录"""
# import time
# from flask import current_app, request
# from flask_restful import Resource

# from app.api.common import error_code
# from app.api.common.fields import admin_fields
# from app.api.common.parser import admin_sign_in_parser
# from app.api.common.response import error, success
# from app.models.admin import Admin
# from app.models import db

# class AdminSignIn(Resource):

#     def post(self):
#         """
#         管理员登录接口
#         """
#         args = admin_sign_in_parser()
#         username = args['username']
#         password = args['password']

#         # 1. 查询用户
#         admin = Admin.query.filter(Admin.mobile == username).first()
#         if not admin:
#             return error(error_code.USER_NOT_EXISTS, msg=u'用户不存在')
        
#         # 2. 验证密码 
#         if not admin.check_password(password):
#             current_app.logger.warning(f"管理员登录密码错误: {username}")
#             return error(error_code.USER_PASSWORD_NOT_CORRECT, msg=u'密码不正确')

#         # 3. 检查状态
#         # 约定：0-待审核, 1-已通过, 2-已拒绝
#         user_status = getattr(admin, 'status', '0')
        
#         if user_status != '1':
#             current_app.logger.warning(f"管理员状态未通过: {username}, 状态: {user_status}")
#             if user_status == '0':
#                 return error(resid=403, msg='账号正在审核中，请耐心等待')
#             elif user_status == '2':
#                 return error(resid=403, msg='账号申请已被拒绝，无法登录')
#             else:
#                 return error(resid=403, msg='账号状态异常')

#         # 4. 更新登录统计信息 (可选，但推荐)
#         try:
#             admin.last_login = int(time.time())
#             admin.last_login_ip = request.remote_addr
#             admin.login_count = (admin.login_count or 0) + 1
#             db.session.commit()
#         except Exception as e:
#             current_app.logger.error(f"更新登录信息失败: {e}")
#             db.session.rollback()

#         # 5. 生成 Token (关键步骤：登录必须返回Token)
#         token = admin.generate_auth_token()

#         # 6. 构造返回数据
#         data = admin.to_dict()
        
#         # 将 Token 放入返回数据中
#         data['auth_token'] = token
        
#         if isinstance(data['auth_token'], bytes):
#             data['auth_token'] = data['auth_token'].decode('utf-8')

#         return success(msg=u'登录成功', data=data, data_fileds=admin_fields())